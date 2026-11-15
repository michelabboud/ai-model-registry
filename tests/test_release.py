"""Offline release contract tests; keys and cloned repositories are disposable."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
ASSETS = ('registry.tar', 'manifest.json', 'manifest.json.sig')
COMMON_SPEC = importlib.util.spec_from_file_location('release_common', REPO / 'scripts/release_common.py')
assert COMMON_SPEC is not None and COMMON_SPEC.loader is not None
release_common = importlib.util.module_from_spec(COMMON_SPEC)
COMMON_SPEC.loader.exec_module(release_common)


def run(args, **kwargs):
    return subprocess.run([str(arg) for arg in args], shell=False,
                          capture_output=True, text=True, timeout=30, **kwargs)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False) + '\n').encode('utf-8')


def digest(data):
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


class ReleaseTree(unittest.TestCase):
    temp: tempfile.TemporaryDirectory[str] | None = None
    work = Path()
    repo = Path()
    out = Path()

    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.TemporaryDirectory(prefix='registry-release-tests-')
        cls.template = Path(cls.base.name) / 'template'
        # Local clone only; reuse existing commits, create no commits or tags.
        result = run(['git', 'clone', '--quiet', '--shared', '--no-tags',
                      str(REPO), cls.template])
        if result.returncode:
            cls.base.cleanup()
            raise RuntimeError(result.stderr)
        for script in (REPO / 'scripts').glob('*.py'):
            shutil.copyfile(script, cls.template / 'scripts' / script.name)
        shutil.copyfile(REPO / '.gitignore', cls.template / '.gitignore')

    @classmethod
    def tearDownClass(cls):
        cls.base.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='registry-release-case-')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.repo = self.work / 'repo'
        shutil.copytree(self.template, self.repo)
        self.out = self.work / 'release'

    def cli(self, script, *args, **kwargs):
        return run([sys.executable, self.repo / 'scripts' / script, *args],
                   cwd=self.repo, **kwargs)

    def build(self, number=1, out=None):
        return self.cli('build_release.py', '--registry', str(number),
                        '--out', out or self.out)

    def assert_ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_refused(self, result, message):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)
        self.assertNotIn('Traceback', result.stderr)


class BuildTests(ReleaseTree):
    def test_tar_is_byte_identical_and_ustar_metadata_is_fixed(self):
        self.assert_ok(self.build())
        second = self.work / 'second'
        # File-system metadata does not affect packaging.
        for path in (self.repo / 'models').glob('*.json'):
            os.utime(path, (123456, 123456))
            path.chmod(0o600)
        self.assert_ok(self.build(out=second))
        self.assertEqual((self.out / 'registry.tar').read_bytes(),
                         (second / 'registry.tar').read_bytes())
        with tarfile.open(self.out / 'registry.tar', 'r:') as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            expected = sorted(path.relative_to(self.repo).as_posix()
                              for folder in ('providers', 'models', 'harnesses', 'schema')
                              for path in (self.repo / folder).rglob('*.json'))
            self.assertEqual(names, expected)
            for member in members:
                self.assertTrue(member.isreg())
                self.assertEqual((member.mtime, member.uid, member.gid, member.mode,
                                  member.uname, member.gname), (0, 0, 0, 0o644, '', ''))
                self.assertFalse(member.pax_headers)
        self.assertEqual((self.out / 'registry.tar').read_bytes()[257:265], b'ustar\x0000')

    def test_manifest_has_canonical_bytes_and_correct_hashes(self):
        self.assert_ok(self.build(number=3))
        raw = (self.out / 'manifest.json').read_bytes()
        manifest = json.loads(raw)
        expected_files = {path.relative_to(self.repo).as_posix(): digest(path.read_bytes())
                          for folder in ('providers', 'models', 'harnesses', 'schema')
                          for path in (self.repo / folder).rglob('*.json')}
        self.assertEqual(manifest, {
            'format': 1, 'registry': 3,
            'created': datetime.now(timezone.utc).date().isoformat(),
            'repo_version': (self.repo / 'VERSION').read_text().strip(),
            'min_client': {'the-operator': '0.17.0'}, 'files': expected_files,
            'tar': digest((self.out / 'registry.tar').read_bytes())})
        self.assertEqual(raw, canonical(manifest))
        self.assertEqual({p.name for p in self.out.iterdir()}, {'registry.tar', 'manifest.json'})

    def test_existing_empty_output_is_accepted(self):
        self.out.mkdir()
        self.assert_ok(self.build())

    def test_nonempty_output_is_preserved(self):
        self.out.mkdir()
        existing = self.out / 'keep.txt'
        existing.write_text('keep')
        self.assert_refused(self.build(), 'empty')
        self.assertEqual(existing.read_text(), 'keep')

    def test_dirty_data_tree_refuses_untracked_modified_and_staged(self):
        path = self.repo / 'providers/openai.json'
        original = path.read_bytes()
        path.write_bytes(original + b'\n')
        self.assert_refused(self.build(), 'dirty')
        self.assert_ok(run(['git', 'add', '--', 'providers/openai.json'], cwd=self.repo))
        self.assert_refused(self.build(), 'dirty')
        # A valid untracked record still trips Git cleanliness after validation.
        path.write_bytes(original)
        self.assert_ok(run(['git', 'reset', '--quiet', 'HEAD', '--', str(path)], cwd=self.repo))
        (self.repo / 'schema/extra.json').write_text('{}\n')
        self.assert_refused(self.build(), 'dirty')
        self.assertFalse(self.out.exists())

    def test_validator_runs_before_dirty_check_and_output_creation(self):
        (self.repo / 'providers/openai.json').write_text('{}\n')
        self.assert_refused(self.build(), 'validation')
        self.assertFalse(self.out.exists())

    def test_output_symlink_refused(self):
        target = self.work / 'target'
        target.mkdir()
        self.out.symlink_to(target, target_is_directory=True)
        self.assert_refused(self.build(), 'symlink')
        self.assertEqual(list(target.iterdir()), [])

    def test_output_within_data_path_refused(self):
        self.assert_refused(self.build(out=self.repo / 'schema/release'), 'data')

    def test_private_pem_is_ignored_at_root_and_under_keys(self):
        result = run(['git', 'check-ignore', '--', 'signing-key.pem',
                      'keys/signing-key.pem', 'keys/registry-signing-key.pub.pem'], cwd=self.repo)
        self.assert_ok(result)
        self.assertEqual(result.stdout.splitlines(), ['signing-key.pem', 'keys/signing-key.pem'])

    def test_missing_public_key_refuses_cleanly(self):
        self.assert_ok(self.build())
        self.assert_refused(self.cli('verify_release.py', '--dir', self.out), 'public key')


class ArchiveBoundsTests(unittest.TestCase):
    def test_signed_size_mismatch_refused_before_hashing(self):
        with tempfile.TemporaryDirectory(prefix='registry-size-test-') as scratch:
            path = Path(scratch) / 'registry.tar'
            expected = digest(b'1234')
            for raw in (b'123', b'12345'):
                with self.subTest(size=len(raw)):
                    path.write_bytes(raw)
                    with patch.object(release_common, 'digest_stream',
                                      side_effect=AssertionError('must refuse before hashing')):
                        with self.assertRaisesRegex(release_common.ReleaseError, 'tar size'):
                            release_common.check_archive(path, {'tar': expected})


class SigningTests(ReleaseTree):
    @classmethod
    def setUpClass(cls):
        result = run(['openssl', 'version']) if shutil.which('openssl') else None
        if result is None or result.returncode or not re.match(r'OpenSSL ([3-9]|[1-9][0-9])\.', result.stdout):
            raise unittest.SkipTest('OpenSSL >= 3.0 absent; throwaway Ed25519 tests skipped')
        super().setUpClass()
        cls.key = Path(cls.base.name) / 'throwaway.pem'
        cls.public = Path(cls.base.name) / 'throwaway.pub.pem'
        result = run(['openssl', 'genpkey', '-algorithm', 'ed25519', '-out', cls.key])
        if result.returncode:
            cls.base.cleanup()
            raise RuntimeError('Cannot create disposable test key')
        cls.key.chmod(0o600)
        result = run(['openssl', 'pkey', '-in', cls.key, '-pubout', '-out', cls.public])
        if result.returncode:
            cls.base.cleanup()
            raise RuntimeError('Cannot derive disposable test public key')

    def setUp(self):
        super().setUp()
        (self.repo / 'keys').mkdir(exist_ok=True)
        shutil.copyfile(self.public, self.repo / 'keys/registry-signing-key.pub.pem')
        self.assert_ok(self.build())

    def sign(self, key=None):
        return self.cli('sign_release.py', '--dir', self.out, '--key', key or self.key)

    def verify(self):
        return self.cli('verify_release.py', '--dir', self.out)

    def signed(self):
        self.assert_ok(self.sign())

    def resign(self, manifest):
        (self.out / 'manifest.json').write_bytes(canonical(manifest))
        self.resign_bytes()

    def resign_bytes(self):
        self.assert_ok(run(['openssl', 'pkeyutl', '-sign', '-rawin', '-inkey', self.key,
                            '-in', self.out / 'manifest.json', '-out', self.out / 'manifest.json.sig']))

    def test_sign_then_verify(self):
        self.signed()
        self.assertEqual((self.out / 'manifest.json.sig').stat().st_size, 64)
        self.assert_ok(self.verify())

    def test_tampered_manifest_fails_signature(self):
        self.signed()
        path = self.out / 'manifest.json'
        path.write_bytes(path.read_bytes().replace(b'"registry":1', b'"registry":2'))
        self.assert_refused(self.verify(), 'signature')

    def test_verified_manifest_bytes_are_the_bytes_parsed_despite_path_swap(self):
        self.signed()
        path = self.out / 'manifest.json'
        signed = path.read_bytes()
        unsigned = signed.replace(b'"registry":1', b'"registry":2')
        self.assertNotEqual(unsigned, signed)
        path.write_bytes(unsigned)
        read_small = release_common.read_small
        reads = []

        def swap_after_read(source, limit, label):
            raw = read_small(source, limit, label)
            if source == path:
                reads.append(raw)
                # The old verifier authenticates this replacement pathname,
                # then parses the unsigned bytes returned from the first read.
                path.write_bytes(signed)
            return raw

        with patch.object(release_common, 'ROOT', self.repo), \
                patch.object(release_common, 'read_small', side_effect=swap_after_read):
            with self.assertRaisesRegex(release_common.ReleaseError, 'signature'):
                release_common.verify_release(self.out)
        self.assertEqual(reads, [unsigned])

    def test_tampered_tar_fails_digest(self):
        self.signed()
        path = self.out / 'registry.tar'
        data = bytearray(path.read_bytes())
        data[1024] ^= 1
        path.write_bytes(data)
        self.assert_refused(self.verify(), 'tar')

    def test_wrong_key_fails_and_leaves_no_signature(self):
        wrong = self.work / 'wrong.pem'
        self.assert_ok(run(['openssl', 'genpkey', '-algorithm', 'ed25519', '-out', wrong]))
        wrong.chmod(0o600)
        self.assert_refused(self.sign(key=wrong), 'signature')
        self.assertFalse((self.out / 'manifest.json.sig').exists())

    def test_wrong_public_key_fails_verification(self):
        self.signed()
        wrong = self.work / 'wrong.pem'
        self.assert_ok(run(['openssl', 'genpkey', '-algorithm', 'ed25519', '-out', wrong]))
        self.assert_ok(run(['openssl', 'pkey', '-in', wrong, '-pubout', '-out',
                            self.repo / 'keys/registry-signing-key.pub.pem']))
        self.assert_refused(self.verify(), 'signature')

    def test_key_mode_symlink_and_inside_repo_refused(self):
        # Only disposable test keys are generated here, never copied by the signer.
        wrong_mode = self.work / 'mode.pem'
        self.assert_ok(run(['openssl', 'genpkey', '-algorithm', 'ed25519', '-out', wrong_mode]))
        wrong_mode.chmod(0o644)
        self.assert_refused(self.sign(key=wrong_mode), '0600')
        link = self.work / 'link.pem'
        link.symlink_to(self.key)
        self.assert_refused(self.sign(key=link), 'symlink')
        inside = self.repo / 'signing-key.pem'
        self.assert_ok(run(['openssl', 'genpkey', '-algorithm', 'ed25519', '-out', inside]))
        inside.chmod(0o600)
        self.assert_refused(self.sign(key=inside), 'outside')
        alias = self.work / 'repo-alias'
        alias.symlink_to(self.repo, target_is_directory=True)
        self.assert_refused(self.sign(key=alias / 'signing-key.pem'), 'outside')

    def test_directory_key_refused(self):
        directory = self.work / 'directory.pem'
        directory.mkdir(mode=0o600)
        self.assert_refused(self.sign(key=directory), 'regular file')

    def test_missing_public_key_refuses_signing(self):
        (self.repo / 'keys/registry-signing-key.pub.pem').unlink()
        self.assert_refused(self.sign(), 'public key')
        self.assertFalse((self.out / 'manifest.json.sig').exists())

    def test_existing_signature_preserved(self):
        self.signed()
        signature = (self.out / 'manifest.json.sig').read_bytes()
        self.assert_refused(self.sign(), 'exists')
        self.assertEqual((self.out / 'manifest.json.sig').read_bytes(), signature)

    def test_signature_must_have_exactly_64_bytes(self):
        self.signed()
        (self.out / 'manifest.json.sig').write_bytes(b'x' * 65)
        self.assert_refused(self.verify(), '64')

    def rewrite_tar(self, edit):
        with tarfile.open(self.out / 'registry.tar', 'r:') as archive:
            members = []
            for member in archive:
                payload = archive.extractfile(member)
                assert payload is not None
                members.append((member, payload.read()))
        members = edit(members)
        with tarfile.open(self.out / 'registry.tar', 'w', format=tarfile.USTAR_FORMAT) as archive:
            for member, data in members:
                archive.addfile(member, io.BytesIO(data) if member.isreg() else None)
        manifest = json.loads((self.out / 'manifest.json').read_bytes())
        manifest['tar'] = digest((self.out / 'registry.tar').read_bytes())
        self.resign(manifest)

    def test_extra_traversal_absolute_symlink_device_and_duplicate_members_refused(self):
        for name, kind, message in (
            ('providers/extra.json', tarfile.REGTYPE, 'membership'),
            ('../escape.json', tarfile.REGTYPE, 'path'),
            ('/escape.json', tarfile.REGTYPE, 'path'),
            ('models/link.json', tarfile.SYMTYPE, 'regular'),
            ('models/hard.json', tarfile.LNKTYPE, 'regular'),
            ('models/device.json', tarfile.CHRTYPE, 'regular'),
            ('providers/openai.json', tarfile.REGTYPE, 'duplicate')):
            with self.subTest(name=name, kind=kind):
                self.assert_ok(self.build(out=self.work / ('fresh-' + str(kind) + '-' + str(len(name)))))
                fresh = self.work / ('fresh-' + str(kind) + '-' + str(len(name)))
                # Reset the unsigned artifacts for each adversarial archive.
                for asset in ('registry.tar', 'manifest.json'):
                    shutil.copyfile(fresh / asset, self.out / asset)
                member = tarfile.TarInfo(name)
                member.type = kind
                member.linkname = 'providers/openai.json' if kind in (tarfile.SYMTYPE, tarfile.LNKTYPE) else ''
                member.size = 2 if kind == tarfile.REGTYPE else 0
                self.rewrite_tar(lambda members: members + [(member, b'{}')])
                self.assert_refused(self.verify(), message)

    def test_missing_member_refused_even_with_signed_tar_hash(self):
        self.rewrite_tar(lambda members: members[1:])
        self.assert_refused(self.verify(), 'membership')

    def test_member_content_checked_after_tar_hash(self):
        def change(members):
            member, data = members[0]
            return [(member, bytes([data[0] ^ 1]) + data[1:])] + members[1:]
        self.rewrite_tar(change)
        self.assert_refused(self.verify(), 'hash')

    def test_signed_manifest_must_be_canonical_and_have_safe_paths(self):
        manifest = json.loads((self.out / 'manifest.json').read_bytes())
        manifest['files']['../escape.json'] = digest(b'{}')
        self.resign(manifest)
        self.assert_refused(self.verify(), 'path')

    def test_signed_noncanonical_manifest_refused(self):
        manifest = json.loads((self.out / 'manifest.json').read_bytes())
        (self.out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        self.resign_bytes()
        self.assert_refused(self.verify(), 'canonical')

    def test_signed_duplicate_json_keys_refused(self):
        raw = (self.out / 'manifest.json').read_bytes()
        (self.out / 'manifest.json').write_bytes(raw.replace(b'"format":1', b'"format":1,"format":1'))
        self.resign_bytes()
        self.assert_refused(self.verify(), 'JSON')

    def test_signed_invalid_manifest_fields_refused(self):
        original = json.loads((self.out / 'manifest.json').read_bytes())
        for field, value, message in (
            ('format', True, 'format'), ('registry', 0, 'registry'),
            ('registry', True, 'registry'), ('created', '2026-02-30', 'created'),
            ('min_client', {}, 'min_client'), ('repo_version', '', 'repo_version'),
            ('files', [], 'files'), ('tar', {'bytes': True, 'sha256': 'a' * 64}, 'hash')):
            with self.subTest(field=field, value=value):
                manifest = {**original, field: value}
                self.resign(manifest)
                self.assert_refused(self.verify(), message)

    def test_signed_archive_with_concatenated_or_trailing_content_refused(self):
        original = (self.out / 'registry.tar').read_bytes()
        for suffix in (b'X', b'\0' * tarfile.RECORDSIZE, original):
            with self.subTest(suffix_bytes=len(suffix)):
                (self.out / 'registry.tar').write_bytes(original + suffix)
                manifest = json.loads((self.out / 'manifest.json').read_bytes())
                manifest['tar'] = digest(original + suffix)
                self.resign(manifest)
                self.assert_refused(self.verify(), 'trailing')

    def test_pax_hidden_header_is_refused(self):
        with tarfile.open(self.out / 'registry.tar', 'r:') as archive:
            members = []
            for member in archive:
                payload = archive.extractfile(member)
                assert payload is not None
                members.append((member, payload.read()))
        with tarfile.open(self.out / 'registry.tar', 'w', format=tarfile.PAX_FORMAT) as archive:
            for index, (member, data) in enumerate(members):
                if index == 0:
                    member.pax_headers = {'comment': 'hidden extra header'}
                archive.addfile(member, io.BytesIO(data))
        manifest = json.loads((self.out / 'manifest.json').read_bytes())
        manifest['tar'] = digest((self.out / 'registry.tar').read_bytes())
        self.resign(manifest)
        self.assert_refused(self.verify(), 'header')

    def test_member_size_record_checked(self):
        manifest = json.loads((self.out / 'manifest.json').read_bytes())
        first = sorted(manifest['files'])[0]
        manifest['files'][first]['bytes'] += 1
        self.resign(manifest)
        self.assert_refused(self.verify(), 'size')

    def test_symlink_asset_refused(self):
        self.signed()
        source = self.out / 'registry.tar'
        target = self.work / 'tar-copy'
        source.rename(target)
        source.symlink_to(target)
        self.assert_refused(self.verify(), 'regular')

    def test_old_or_missing_openssl_refused_cleanly(self):
        self.signed()
        binary = self.work / 'openssl-bin'
        binary.mkdir()
        executable = binary / 'openssl'
        executable.write_text('#!' + sys.executable + '\nprint("OpenSSL 1.1.1")\n')
        executable.chmod(0o700)
        env = os.environ.copy()
        env['PATH'] = str(binary)
        self.assert_refused(self.cli('verify_release.py', '--dir', self.out, env=env), 'OpenSSL >= 3.0')
        executable.unlink()
        self.assert_refused(self.cli('verify_release.py', '--dir', self.out, env=env), 'OpenSSL')

    def test_signature_checked_before_manifest_json_parsing(self):
        self.signed()
        (self.out / 'manifest.json').write_bytes(b'not JSON')
        self.assert_refused(self.verify(), 'signature')

    def fake_gh(self, releases, refs=None, *, corrupt=False, extra_asset: bool | str = False):
        self.assert_ok(run(['git', 'remote', 'set-url', 'origin',
                            'git@github.com:example/registry.git'], cwd=self.repo))
        binary = self.work / 'bin'
        binary.mkdir(exist_ok=True)
        script = binary / 'gh'
        script.write_text('#!' + sys.executable + '\n' + '''import glob, json, pathlib, shutil, sys
args = sys.argv[1:]
root = pathlib.Path(__file__).resolve().parent.parent
with (root / 'gh-calls.jsonl').open('a') as log:
    log.write(json.dumps(args) + '\\n')
state = json.loads((root / 'gh-state.json').read_text())
if args[:1] == ['api']:
    endpoint = args[-1]
    if '/git/matching-refs/' in endpoint:
        print(json.dumps([state['refs']]))
    elif '/releases/tags/' in endpoint:
        names = ['registry.tar', 'manifest.json', 'manifest.json.sig']
        if state['extra_asset']: names.append('extra.txt')
        if state['extra_asset'] == 'null': names.append(None)
        print(json.dumps({'assets': [{'name': n} for n in names]}))
    elif endpoint.endswith('/releases?per_page=100'):
        print(json.dumps(state['releases']))
    else:
        sys.exit('unexpected API request: ' + endpoint)
elif args[:2] == ['release', 'create']:
    store = root / 'uploaded'
    store.mkdir()
    for name in ['registry.tar', 'manifest.json', 'manifest.json.sig']:
        operand = next(a for a in args if pathlib.Path(a).name == name)
        # gh's documented filename#label and asset-pattern interpretation.
        matches = glob.glob(operand.split('#', 1)[0])
        if not matches: sys.exit('asset operand matched no file')
        for match in matches:
            path = pathlib.Path(match)
            shutil.copyfile(path, store / path.name)
elif args[:2] == ['release', 'download']:
    dest = pathlib.Path(args[args.index('--dir') + 1])
    for path in (root / 'uploaded').iterdir(): shutil.copyfile(path, dest / path.name)
    if state['corrupt']: (dest / 'registry.tar').write_bytes(b'corrupted download')
else:
    sys.exit('unexpected gh request')
''')
        script.chmod(0o700)
        (self.work / 'gh-state.json').write_text(json.dumps({
            'releases': releases, 'refs': refs or [], 'corrupt': corrupt,
            'extra_asset': extra_asset}))
        env = os.environ.copy()
        env['PATH'] = str(binary) + os.pathsep + env.get('PATH', '')
        return env

    def publish(self, env):
        return self.cli('publish_release.py', '--dir', self.out, env=env)

    def calls(self):
        return [json.loads(line) for line in (self.work / 'gh-calls.jsonl').read_text().splitlines()]

    def test_publish_refuses_nonconsecutive_number_across_pages(self):
        self.signed()
        env = self.fake_gh([[{'tag_name': 'v0.4.0'}], [{'tag_name': 'registry/2'}]])
        self.assert_refused(self.publish(env), 'next registry number is 3')
        self.assertFalse(any(call[:2] == ['release', 'create'] for call in self.calls()))

    def test_publish_refuses_existing_tag(self):
        self.signed()
        env = self.fake_gh([[]], [{'ref': 'refs/tags/registry/1'}])
        self.assert_refused(self.publish(env), 'tag already exists')
        self.assertFalse(any(call[:2] == ['release', 'create'] for call in self.calls()))

    def test_publish_verifies_before_gh(self):
        self.signed()
        (self.out / 'registry.tar').write_bytes(b'broken')
        env = self.fake_gh([[]])
        self.assert_refused(self.publish(env), 'tar')
        self.assertFalse((self.work / 'gh-calls.jsonl').exists())

    def test_publish_uploads_exact_assets_and_checks_download(self):
        self.signed()
        env = self.fake_gh([[]])
        self.assert_ok(self.publish(env))
        calls = self.calls()
        create = next(call for call in calls if call[:2] == ['release', 'create'])
        self.assertEqual(create[2], 'registry/1')
        uploads = [Path(arg).name for arg in create if Path(arg).name in ASSETS]
        self.assertCountEqual(uploads, ASSETS)
        self.assertIn('--target', create)
        self.assertTrue(any(call[:2] == ['release', 'download'] for call in calls))
        self.assertFalse(any('delete' in call or '--clobber' in call for call in calls))

    def test_publish_detects_corrupt_download_without_deleting_release(self):
        self.signed()
        env = self.fake_gh([[]], corrupt=True)
        self.assert_refused(self.publish(env), 'download')
        self.assertTrue((self.work / 'uploaded').exists())
        self.assertFalse(any('delete' in call for call in self.calls()))

    def test_publish_detects_extra_remote_asset(self):
        self.signed()
        env = self.fake_gh([[]], extra_asset=True)
        self.assert_refused(self.publish(env), 'assets')

    def test_publish_handles_literal_hash_and_glob_directory_without_wrong_file_upload(self):
        self.signed()
        prefix = self.work / 'unrelated.pem'
        prefix.write_bytes(b'unrelated file must never be uploaded')
        literal = self.work / 'unrelated.pem#release[1]'
        self.out.rename(literal)
        self.out = literal
        env = self.fake_gh([[]])
        self.assert_ok(self.publish(env))
        self.assertCountEqual([p.name for p in (self.work / 'uploaded').iterdir()], ASSETS)
        for name in ASSETS:
            self.assertEqual((self.work / 'uploaded' / name).read_bytes(),
                             (self.out / name).read_bytes())

    def test_publish_pins_origin_despite_gh_repository_environment(self):
        self.signed()
        env = self.fake_gh([[]])
        env['GH_REPO'] = 'different/elsewhere'
        env['GH_HOST'] = 'different.example'
        self.assert_ok(self.publish(env))
        for args in self.calls():
            if args[0] == 'api':
                self.assertIn('--hostname', args)
                self.assertEqual(args[args.index('--hostname') + 1], 'github.com')
                self.assertTrue(args[-1].startswith('repos/example/registry/'))
            elif args[:1] == ['release']:
                self.assertIn('--repo', args)
                self.assertEqual(args[args.index('--repo') + 1], 'github.com/example/registry')

    def test_publish_accepts_ssh_url_origin(self):
        self.signed()
        env = self.fake_gh([[]])
        self.assert_ok(run(['git', 'remote', 'set-url', 'origin',
                            'ssh://git@github.com/example/registry.git'], cwd=self.repo))
        self.assert_ok(self.publish(env))

    def test_publish_accepts_https_origin(self):
        self.signed()
        env = self.fake_gh([[]])
        self.assert_ok(run(['git', 'remote', 'set-url', 'origin',
                            'https://github.com/example/registry.git'], cwd=self.repo))
        self.assert_ok(self.publish(env))

    def test_publish_rejects_invalid_destination_without_gh(self):
        self.signed()
        env = self.fake_gh([[]])
        for origin in ('https://example.invalid/owner/repo.git',
                       'https://user:password@github.com/owner/repo.git',
                       'http://github.com/owner/repo.git', '/local/repo'):
            with self.subTest(origin=origin):
                self.assert_ok(run(['git', 'remote', 'set-url', 'origin', origin], cwd=self.repo))
                self.assert_refused(self.publish(env), 'origin')
                self.assertFalse((self.work / 'gh-calls.jsonl').exists())

    def test_publish_rejects_null_remote_asset_name_without_traceback(self):
        self.signed()
        env = self.fake_gh([[]], extra_asset='null')
        self.assert_refused(self.publish(env), 'assets')

    def test_publish_rejects_malformed_tag_refs_before_creation(self):
        self.signed()
        env = self.fake_gh([[]], refs=[{'ref': None}])
        self.assert_refused(self.publish(env), 'tag listing')
        self.assertFalse(any(call[:2] == ['release', 'create'] for call in self.calls()))


if __name__ == '__main__':
    unittest.main()
