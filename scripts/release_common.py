"""Shared offline release format and explicit OpenSSL/GitHub CLI boundaries.

No private-key bytes enter Python. Verification never extracts an archive.
Only publish_release invokes gh; build/sign/verify work without network access.
"""
from datetime import date, datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA_DIRS = ('providers', 'models', 'harnesses', 'schema')
ASSETS = ('registry.tar', 'manifest.json', 'manifest.json.sig')
PUBLIC_KEY = Path('keys/registry-signing-key.pub.pem')
FORMAT = 1
MIN_CLIENT = {'the-operator': '0.17.0'}
SIGNATURE_BYTES = 64
MAX_MANIFEST_BYTES = 16 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024
COMMAND_TIMEOUT = 120
SHA256 = re.compile(r'[0-9a-f]{64}\Z')
REGISTRY_TAG = re.compile(r'registry/([1-9][0-9]*)\Z')
GITHUB_HOST = 'github.com'


class ReleaseError(ValueError):
    """A release cannot safely be built, authenticated, or published."""


def command(args, purpose, *, cwd=ROOT):
    """Never invoke a shell or echo subprocess diagnostics (key paths included)."""
    try:
        result = subprocess.run(args, shell=False, cwd=cwd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=COMMAND_TIMEOUT,
                                check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReleaseError(purpose + ': command unavailable or timed out') from exc
    if result.returncode:
        raise ReleaseError(purpose + ': command failed')
    return result.stdout


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def digest_bytes(raw):
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def digest_stream(handle):
    digest = hashlib.sha256()
    size = 0
    while block := handle.read(CHUNK_BYTES):
        digest.update(block)
        size += len(block)
    return {'sha256': digest.hexdigest(), 'bytes': size}


def regular_open(path, label):
    """Refuse links, FIFOs and devices before reading any release input."""
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ReleaseError(label + ': expected a regular file, no symlinks')
        flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
        handle = os.fdopen(os.open(path, flags), 'rb')
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            handle.close()
            raise ReleaseError(label + ': expected a regular file')
        return handle
    except OSError as exc:
        raise ReleaseError(label + ': regular file missing or unreadable') from exc


def read_small(path, limit, label):
    with regular_open(path, label) as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise ReleaseError(label + ': file exceeds size limit')
    return raw


def public_key():
    path = ROOT / PUBLIC_KEY
    # Inspect only; let OpenSSL parse the public PEM.
    with regular_open(path, 'public key (add it at the first release ceremony)'):
        pass
    return path


def require_openssl():
    output = command(['openssl', 'version'], 'OpenSSL >= 3.0 check')
    match = re.match(rb'OpenSSL ([0-9]+)\.([0-9]+)\.', output)
    if match is None or int(match[1]) < 3:
        raise ReleaseError('OpenSSL >= 3.0 is required')


def safe_path(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name or '\x00' in name:
        raise ReleaseError('unsafe release path')
    path = PurePosixPath(name)
    if (path.is_absolute() or '..' in path.parts or len(path.parts) < 2
            or path.parts[0] not in DATA_DIRS or path.as_posix() != name
            or path.suffix != '.json'):
        raise ReleaseError('unsafe release path')
    return name


def member_info(name, size):
    member = tarfile.TarInfo(name)
    member.size = size
    member.type = tarfile.REGTYPE
    member.mtime = member.uid = member.gid = 0
    member.uname = member.gname = ''
    member.mode = 0o644
    return member


def clean_data_tree():
    status = command(['git', 'status', '--porcelain', '--untracked-files=all', '--',
                      *DATA_DIRS], 'data working tree status')
    if status.strip():
        raise ReleaseError('dirty data working tree; commit/review data before building')


def collect_payload():
    files = {}
    for directory in DATA_DIRS:
        base = ROOT / directory
        if base.is_symlink() or not base.is_dir():
            raise ReleaseError('data path must be a directory without symlinks')
        for parent, directories, names in os.walk(base, followlinks=False):
            for child in directories:
                if (Path(parent) / child).is_symlink():
                    raise ReleaseError('data directory symlink is forbidden')
            for name in names:
                if not name.endswith('.json'):
                    continue
                path = Path(parent) / name
                relative = safe_path(path.relative_to(ROOT).as_posix())
                with regular_open(path, 'payload JSON') as handle:
                    files[relative] = handle.read()
    return dict(sorted(files.items()))


def prepare_output(directory):
    if directory.is_symlink():
        raise ReleaseError('output directory must not be a symlink')
    resolved = directory.resolve()
    if any(resolved == ROOT / part or (ROOT / part) in resolved.parents for part in DATA_DIRS):
        raise ReleaseError('output directory must be outside the data paths')
    if directory.exists():
        if not directory.is_dir() or any(directory.iterdir()):
            raise ReleaseError('output directory must be new or empty')
    else:
        directory.mkdir(parents=True)
    return resolved


def build_release(number, directory):
    # Keep the validator as the first substantive build operation.
    command([sys.executable, str(ROOT / 'scripts/validate.py')], 'registry validation')
    clean_data_tree()
    if type(number) is not int or number < 1:
        raise ReleaseError('registry number must be a positive integer')
    files = collect_payload()
    version = read_small(ROOT / 'VERSION', 1024, 'VERSION').decode('utf-8').strip()
    if not version or any(char.isspace() for char in version):
        raise ReleaseError('VERSION must contain a bare version string')
    directory = prepare_output(directory)
    # Exclusive creation preserves artifacts if another process claimed the path.
    with (directory / 'registry.tar').open('xb') as output:
        with tarfile.open(fileobj=output, mode='w', format=tarfile.USTAR_FORMAT,
                          encoding='utf-8', errors='strict') as archive:
            for name, data in files.items():
                archive.addfile(member_info(name, len(data)), io.BytesIO(data))
    with regular_open(directory / 'registry.tar', 'tar') as handle:
        tar_digest = digest_stream(handle)
    manifest = {
        'format': FORMAT, 'registry': number,
        'created': datetime.now(timezone.utc).date().isoformat(),
        'repo_version': version, 'min_client': MIN_CLIENT,
        'files': {name: digest_bytes(data) for name, data in files.items()},
        'tar': tar_digest,
    }
    with (directory / 'manifest.json').open('xb') as output:
        output.write(canonical(manifest))
    return manifest


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReleaseError('manifest contains duplicate JSON keys')
        result[key] = value
    return result


def check_digest(value):
    if (not isinstance(value, dict) or set(value) != {'sha256', 'bytes'}
            or not isinstance(value['sha256'], str) or not SHA256.fullmatch(value['sha256'])
            or type(value['bytes']) is not int or value['bytes'] < 0):
        raise ReleaseError('manifest hash/size record is invalid')


def parse_manifest(raw):
    try:
        manifest = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ReleaseError('manifest JSON is invalid') from exc
    if not isinstance(manifest, dict) or set(manifest) != {
            'format', 'registry', 'created', 'repo_version', 'min_client', 'files', 'tar'}:
        raise ReleaseError('manifest has an invalid field set')
    if type(manifest['format']) is not int or manifest['format'] != FORMAT:
        raise ReleaseError('unsupported manifest format')
    if type(manifest['registry']) is not int or manifest['registry'] < 1:
        raise ReleaseError('manifest registry number must be a positive integer')
    created = manifest['created']
    try:
        if not isinstance(created, str) or date.fromisoformat(created).isoformat() != created:
            raise ValueError
    except ValueError as exc:
        raise ReleaseError('manifest created must be YYYY-MM-DD') from exc
    if not isinstance(manifest['repo_version'], str) or not manifest['repo_version'].strip():
        raise ReleaseError('manifest repo_version must be a nonempty string')
    if manifest['min_client'] != MIN_CLIENT:
        raise ReleaseError('manifest min_client is unsupported')
    if not isinstance(manifest['files'], dict):
        raise ReleaseError('manifest files must be an object')
    for name, record in manifest['files'].items():
        safe_path(name)
        check_digest(record)
    check_digest(manifest['tar'])
    try:
        if canonical(manifest) != raw:
            raise ReleaseError('manifest bytes are not canonical JSON with a trailing newline')
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ReleaseError('manifest bytes are not canonical JSON') from exc
    return manifest


def verify_signature(raw, signature_path, trusted_key):
    signature = read_small(signature_path, SIGNATURE_BYTES, 'signature (64 bytes required)')
    if len(signature) != SIGNATURE_BYTES:
        raise ReleaseError('signature must be exactly 64 bytes')
    # OpenSSL must authenticate the same snapshot that Python will parse,
    # rather than reopening a caller-controlled manifest pathname.
    with tempfile.TemporaryDirectory(prefix='registry-verify-') as scratch:
        manifest_path = Path(scratch) / 'manifest.json'
        with manifest_path.open('xb') as output:
            output.write(raw)
        command(['openssl', 'pkeyutl', '-verify', '-rawin', '-pubin', '-inkey',
                 str(trusted_key), '-in', str(manifest_path), '-sigfile', str(signature_path)],
                'manifest signature verification')


def check_archive(path, manifest):
    with regular_open(path, 'tar') as handle:
        if os.fstat(handle.fileno()).st_size != manifest['tar']['bytes']:
            raise ReleaseError('tar size does not match manifest')
        if digest_stream(handle) != manifest['tar']:
            raise ReleaseError('tar hash or size does not match manifest')
        handle.seek(0)
        seen = []
        end = 0
        with tarfile.open(fileobj=handle, mode='r:', encoding='utf-8', errors='strict') as archive:
            for member in archive:
                name = safe_path(member.name)
                if not member.isreg():
                    raise ReleaseError('tar members must be regular files; no links or devices')
                if name in seen:
                    raise ReleaseError('duplicate tar member')
                if name not in manifest['files']:
                    raise ReleaseError('tar membership differs from manifest files')
                record = manifest['files'][name]
                if member.size != record['bytes']:
                    raise ReleaseError('tar member size does not match manifest')
                payload = archive.extractfile(member)
                if payload is None:
                    raise ReleaseError('tar regular member is unreadable')
                with payload:
                    if digest_stream(payload) != record:
                        raise ReleaseError('tar member hash or size does not match manifest')
                # tarfile hides PAX/GNU extension headers. Require the actual
                # header at the expected offset to be our canonical ustar header.
                if member.offset != end or member.offset_data != end + tarfile.BLOCKSIZE:
                    raise ReleaseError('tar contains hidden or non-ustar headers')
                handle.seek(end)
                expected = member_info(name, member.size).tobuf(tarfile.USTAR_FORMAT,
                                                                 encoding='utf-8', errors='strict')
                if handle.read(tarfile.BLOCKSIZE) != expected:
                    raise ReleaseError('tar header does not match deterministic ustar format')
                data_end = member.offset_data + member.size
                end = data_end + (-member.size % tarfile.BLOCKSIZE)
                handle.seek(data_end)
                if any(handle.read(end - data_end)):
                    raise ReleaseError('tar member padding must be zero')
                seen.append(name)
        if seen != sorted(manifest['files']):
            raise ReleaseError('tar membership/order differs from manifest files')
        expected_size = ((end + 2 * tarfile.BLOCKSIZE + tarfile.RECORDSIZE - 1)
                         // tarfile.RECORDSIZE * tarfile.RECORDSIZE)
        if manifest['tar']['bytes'] != expected_size:
            raise ReleaseError('tar has unexpected trailing bytes')
        handle.seek(end)
        if any(handle.read(expected_size - end)):
            raise ReleaseError('tar has nonzero trailing content')


def verify_release(directory):
    trusted_key = public_key()
    require_openssl()
    raw = read_small(directory / 'manifest.json', MAX_MANIFEST_BYTES, 'manifest')
    verify_signature(raw, directory / 'manifest.json.sig', trusted_key)
    manifest = parse_manifest(raw)
    check_archive(directory / 'registry.tar', manifest)
    return manifest


def check_private_key(path):
    # Never open, read, copy, hash or print this file in Python.
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode):
        raise ReleaseError('private key must not be a symlink')
    if not stat.S_ISREG(metadata.st_mode):
        raise ReleaseError('private key must be a regular file')
    if metadata.st_uid != os.getuid():
        raise ReleaseError('private key must be owned by the current user')
    if stat.S_IMODE(metadata.st_mode) != 0o600:
        raise ReleaseError('private key mode must be exactly 0600')
    resolved = path.resolve(strict=True)
    if resolved == ROOT or ROOT in resolved.parents:
        raise ReleaseError('private key must be outside the repository')
    return resolved


def sign_release(directory, private_key):
    key = check_private_key(private_key)
    trusted_key = public_key()
    require_openssl()
    manifest_path = directory / 'manifest.json'
    raw = read_small(manifest_path, MAX_MANIFEST_BYTES, 'manifest')
    manifest = parse_manifest(raw)
    check_archive(directory / 'registry.tar', manifest)
    destination = directory / 'manifest.json.sig'
    if destination.exists() or destination.is_symlink():
        raise ReleaseError('signature already exists; refusing to overwrite it')
    # OpenSSL writes only to a run-owned temporary path. A failed verification
    # never leaves a final signature behind or replaces an operator's artifact.
    with tempfile.TemporaryDirectory(prefix='.registry-sign-', dir=directory) as scratch:
        signature_path = Path(scratch) / 'manifest.json.sig'
        command(['openssl', 'pkeyutl', '-sign', '-rawin', '-inkey', str(key),
                 '-in', str(manifest_path), '-out', str(signature_path)], 'manifest signing')
        verify_signature(raw, signature_path, trusted_key)
        signature = read_small(signature_path, SIGNATURE_BYTES, 'signature')
        with destination.open('xb') as output:
            output.write(signature)
    return manifest


def gh_json(args, purpose):
    raw = command(['gh', *args], purpose)
    try:
        return json.loads(raw)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ReleaseError(purpose + ': invalid JSON response') from exc


def paged_objects(endpoint, purpose):
    pages = gh_json(['api', '--hostname', GITHUB_HOST, '--paginate', '--slurp', endpoint], purpose)
    if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
        raise ReleaseError(purpose + ': expected arrays of result pages')
    objects = [entry for page in pages for entry in page]
    if any(not isinstance(entry, dict) for entry in objects):
        raise ReleaseError(purpose + ': expected JSON objects')
    return objects


def github_repository():
    """Pin public GitHub origin rather than inheriting gh's host/repo defaults."""
    remote = command(['git', 'remote', 'get-url', 'origin'], 'publication origin').decode('utf-8').strip()
    if remote.startswith('git@' + GITHUB_HOST + ':'):
        path = remote[len('git@' + GITHUB_HOST + ':'):]
    else:
        try:
            parsed = urlsplit(remote)
            https = (parsed.scheme == 'https' and parsed.username is None
                     and parsed.port in (None, 443))
            ssh = (parsed.scheme == 'ssh' and parsed.username == 'git'
                   and parsed.password is None and parsed.port in (None, 22))
            if (not (https or ssh) or parsed.hostname != GITHUB_HOST
                    or parsed.query or parsed.fragment):
                raise ValueError
            path = parsed.path.strip('/')
        except ValueError as exc:
            raise ReleaseError('publication origin must be a credential-free GitHub.com HTTPS or Git SSH remote') from exc
    if path.endswith('.git'):
        path = path[:-4]
    parts = path.split('/')
    if (len(parts) != 2 or any(part in ('', '.', '..') for part in parts)
            or not all(re.fullmatch(r'[A-Za-z0-9_.-]+', part) for part in parts)):
        raise ReleaseError('publication origin must identify one GitHub owner/repository')
    return path


def publish_release(directory):
    manifest = verify_release(directory)
    repository = github_repository()
    destination = GITHUB_HOST + '/' + repository
    api_base = 'repos/' + repository
    number = manifest['registry']
    tag = 'registry/' + str(number)
    releases = paged_objects(api_base + '/releases?per_page=100', 'release listing')
    highest = 0
    for release in releases:
        name = release.get('tag_name')
        if not isinstance(name, str):
            raise ReleaseError('release listing contains an invalid tag name')
        if name.startswith('registry/'):
            match = REGISTRY_TAG.fullmatch(name)
            if match is None:
                raise ReleaseError('release listing contains a malformed registry tag')
            highest = max(highest, int(match[1]))
    if number != highest + 1:
        raise ReleaseError(f'next registry number is {highest + 1}; refusing registry/{number}')
    refs = paged_objects(api_base + '/git/matching-refs/tags/registry/', 'tag listing')
    if any(not isinstance(entry.get('ref'), str) for entry in refs):
        raise ReleaseError('tag listing contains an invalid reference')
    if any(entry.get('ref') == 'refs/tags/' + tag for entry in refs):
        raise ReleaseError('tag already exists; refusing to reuse or move it')
    target = command(['git', 'rev-parse', '--verify', 'HEAD^{commit}'], 'release target').decode('ascii').strip()
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', target):
        raise ReleaseError('invalid release target commit')
    with tempfile.TemporaryDirectory(prefix='registry-publish-') as scratch:
        upload = Path(scratch) / 'upload'
        downloaded = Path(scratch) / 'download'
        upload.mkdir()
        downloaded.mkdir()
        # gh interprets asset operands as filename#label or glob patterns even
        # with shell=False. Fixed basenames from a private staging cwd preserve
        # literal path binding, including directories containing #, [ or *.
        # Only the authenticated public release assets are copied, never a key.
        for name in ASSETS:
            with regular_open(directory / name, 'local asset') as source:
                with (upload / name).open('xb') as output:
                    shutil.copyfileobj(source, output, CHUNK_BYTES)
        verify_release(upload)
        command(['gh', 'release', 'create', tag, *ASSETS, '--repo', destination,
                 '--target', target, '--title', tag,
                 '--notes', 'Signed registry data release ' + str(number) + '.'],
                'release creation (inspect remote state before any retry)', cwd=upload)
        remote = gh_json(['api', '--hostname', GITHUB_HOST,
                          api_base + '/releases/tags/' + tag], 'published release inspection')
        if (not isinstance(remote, dict) or not isinstance(remote.get('assets'), list)
                or any(not isinstance(asset, dict) or not isinstance(asset.get('name'), str)
                       for asset in remote['assets'])
                or sorted(asset['name'] for asset in remote['assets']) != sorted(ASSETS)):
            raise ReleaseError('published release assets differ from the exact three required assets')
        command(['gh', 'release', 'download', tag, '--repo', destination, '--dir', str(downloaded),
                 '--pattern', 'registry.tar', '--pattern', 'manifest.json',
                 '--pattern', 'manifest.json.sig'], 'release download')
        if sorted(path.name for path in downloaded.iterdir()) != sorted(ASSETS):
            raise ReleaseError('downloaded release assets differ from required assets')
        for name in ASSETS:
            with regular_open(upload / name, 'verified upload asset') as local:
                with regular_open(downloaded / name, 'downloaded asset') as remote_asset:
                    while True:
                        block = local.read(CHUNK_BYTES)
                        if block != remote_asset.read(CHUNK_BYTES):
                            raise ReleaseError('download byte comparison failed; inspect remote release')
                        if not block:
                            break
    return manifest


def cli_result(action):
    """Stable 0/1 operational exits; argparse handles usage and --help separately."""
    try:
        manifest = action()
        print(f'registry/{manifest["registry"]}: {len(manifest["files"])} files; '
              f'tar sha256 {manifest["tar"]["sha256"]}')
        return 0
    except (ReleaseError, OSError, ValueError, UnicodeError, tarfile.TarError, OverflowError) as exc:
        # OSError may contain a private-key pathname; never echo it.
        message = str(exc) if isinstance(exc, ReleaseError) else 'release input or output operation failed'
        print('error: ' + message, file=sys.stderr)
        return 1
