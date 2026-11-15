"""Black-box contract tests; every vendor and price here is invented example data."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'scripts/validate.py'
VALID = REPO / 'tests/fixtures/valid'
PROVIDER = 'providers/example-provider.json'
MODELS = 'models/example-provider.json'
HARNESS = 'harnesses/example-cli.json'


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='registry-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(VALID, self.root, dirs_exist_ok=True)

    def run_validator(self, *args, root=None):
        return subprocess.run([sys.executable, str(SCRIPT), '--root', str(root or self.root), *args],
                              capture_output=True, text=True, check=False, timeout=10)

    def change(self, path, edit):
        target = self.root / path
        data = json.loads(target.read_text())
        edit(data)
        target.write_text(json.dumps(data) + '\n')

    def assert_bad(self, path, pointer, *args, root=None):
        result = self.run_validator('--json', *args, root=root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(any(p['path'] == path and p['pointer'] == pointer for p in report['problems']), report)
        return report

    def test_valid_tree(self):
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('3 files', result.stdout)
        self.assertIn('0 problems', result.stdout)

    def test_empty_tree(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ('providers', 'models', 'harnesses'):
                (Path(root) / name).mkdir()
                (Path(root) / name / '.gitkeep').touch()
            self.assertEqual(self.run_validator(root=root).returncode, 0)

    def test_missing_data_directory(self):
        shutil.rmtree(self.root / 'harnesses')
        self.assert_bad('harnesses', '')

    def test_invalid_fixture_catalog(self):
        catalog = REPO / 'tests/fixtures/invalid'
        for case in sorted(catalog.iterdir()):
            with self.subTest(case=case.name):
                expected = json.loads((case / 'expected.json').read_text())
                self.assert_bad(expected['path'], expected['pointer'], root=case)

    def test_bad_stems(self):
        for path, field in ((PROVIDER, 'id'), (MODELS, 'provider'), (HARNESS, 'id')):
            with self.subTest(path=path):
                self.change(path, lambda d: d.__setitem__(field, 'other'))
                self.assert_bad(path, '/' + field)
                shutil.copyfile(VALID / path, self.root / path)

    def test_unknown_top_level_and_nested_keys(self):
        for path, edit, pointer in (
            (PROVIDER, lambda d: d.__setitem__('unknown', 1), '/unknown'),
            (MODELS, lambda d: d['models'][0]['pricing'].__setitem__('currency', 'USD'), '/models/0/pricing/currency'),
            (HARNESS, lambda d: d['env'][0].__setitem__('value', 'example'), '/env/0/value')):
            with self.subTest(pointer=pointer):
                self.change(path, edit)
                self.assert_bad(path, pointer)

    def test_missing_verified_at_each_level(self):
        for path, pointer, select in (
            (PROVIDER, '/verified', lambda d: d),
            (MODELS, '/models/0/verified', lambda d: d['models'][0]),
            (HARNESS, '/verified', lambda d: d)):
            with self.subTest(path=path):
                self.change(path, lambda d: select(d).pop('verified'))
                self.assert_bad(path, pointer)

    def test_urls(self):
        for url in ('http://example.com', 'https://user:pass@example.com', 'https:///missing',
                    'https://example.com:bad', 'https://example.com\\evil', 'https://exa mple.com'):
            with self.subTest(url=url):
                self.change(PROVIDER, lambda d: d.__setitem__('docs_url', url))
                self.assert_bad(PROVIDER, '/docs_url')

    def test_base_url_constraints(self):
        for url in ('https://example.com?key=example', 'https://example.com#frag',
                    'https://{other}.example.com', 'https://example.com/{other}', 'https://example.com?'):
            with self.subTest(url=url):
                self.change(PROVIDER, lambda d: d.__setitem__('base_url', url))
                self.assert_bad(PROVIDER, '/base_url')

    def test_allowed_placeholders(self):
        self.change(PROVIDER, lambda d: d.__setitem__('base_url', 'https://{region}.example.com/v1/{project}'))
        self.assertEqual(self.run_validator().returncode, 0)

    def test_null_and_zero_prices(self):
        self.change(MODELS, lambda d: d['models'][1]['pricing'].update(input=None, output=0, cache_read=None))
        self.assertEqual(self.run_validator().returncode, 0)

    def test_negative_prices(self):
        for key in ('input', 'output', 'cache_read'):
            with self.subTest(key=key):
                self.change(MODELS, lambda d: d['models'][0]['pricing'].__setitem__(key, -1))
                self.assert_bad(MODELS, '/models/0/pricing/' + key)
                shutil.copyfile(VALID / MODELS, self.root / MODELS)

    def test_long_context(self):
        prices = dict(threshold_tokens=100000, input=2, output=4, cache_read=None,
                      cache_writes=[{'ttl': '5m', 'price': 0}, {'ttl': '1h', 'price': None}])
        self.change(MODELS, lambda d: d['models'][0]['pricing'].__setitem__('long_context', prices))
        self.assertEqual(self.run_validator().returncode, 0)
        self.change(MODELS, lambda d: d['models'][0]['pricing']['long_context'].__setitem__('input', -1))
        self.assert_bad(MODELS, '/models/0/pricing/long_context/input')

    def test_price_and_token_types(self):
        for field, value in (('context_window', True), ('max_output_tokens', 0), ('context_window', 1.5)):
            with self.subTest(field=field, value=value):
                self.change(MODELS, lambda d: d['models'][0].__setitem__(field, value))
                self.assert_bad(MODELS, '/models/0/' + field)
                shutil.copyfile(VALID / MODELS, self.root / MODELS)
        self.change(MODELS, lambda d: d['models'][0]['pricing'].__setitem__('input', True))
        self.assert_bad(MODELS, '/models/0/pricing/input')

    def test_two_probes(self):
        self.change(MODELS, lambda d: d['models'][1].__setitem__('probe', True))
        self.assert_bad(MODELS, '/models')

    def test_zero_probes(self):
        self.change(MODELS, lambda d: d['models'][0].__setitem__('probe', False))
        self.assert_bad(MODELS, '/models')

    def test_zero_defaults(self):
        self.change(MODELS, lambda d: d['models'][1].__setitem__('default', False))
        self.assert_bad(MODELS, '/models')

    def test_two_defaults(self):
        self.change(MODELS, lambda d: d['models'][0].__setitem__('default', True))
        self.assert_bad(MODELS, '/models')

    def test_probe_on_preview(self):
        self.change(MODELS, lambda d: d['models'][0].__setitem__('status', 'preview'))
        self.assert_bad(MODELS, '/models/0/probe')

    def test_default_on_preview(self):
        self.change(MODELS, lambda d: d['models'][1].__setitem__('status', 'preview'))
        self.assert_bad(MODELS, '/models/1/default')

    def test_probe_not_cheapest(self):
        self.change(MODELS, lambda d: d['models'][0]['pricing'].__setitem__('input', 3))
        self.assert_bad(MODELS, '/models/0/pricing/input')

    def test_probe_price_required(self):
        self.change(MODELS, lambda d: d['models'][0]['pricing'].__setitem__('input', None))
        self.assert_bad(MODELS, '/models/0/pricing/input')

    def test_duplicate_model_ids(self):
        self.change(MODELS, lambda d: d['models'][1].__setitem__('id', 'example-small'))
        self.assert_bad(MODELS, '/models/1/id')

    def test_deprecated_without_shutdown(self):
        self.change(MODELS, lambda d: d['models'][1].__setitem__('status', 'deprecated'))
        self.assert_bad(MODELS, '/models/1/shutdown')

    def test_shutdown_on_ga(self):
        self.change(MODELS, lambda d: d['models'][1].__setitem__('shutdown', '2026-01-01'))
        self.assert_bad(MODELS, '/models/1/shutdown')

    def test_valid_deprecated_shutdown(self):
        self.change(MODELS, lambda d: d['models'][1].update(default=False, status='deprecated', shutdown='2027-01-01'))
        self.change(MODELS, lambda d: d['models'][0].__setitem__('default', True))
        self.assertEqual(self.run_validator().returncode, 0)

    def test_dates(self):
        future = (datetime.now(timezone.utc).date() + timedelta(days=1)).isoformat()
        for value in (future, '2023-12-31', '2026-02-30', '2026-1-01'):
            with self.subTest(value=value):
                self.change(PROVIDER, lambda d: d.__setitem__('verified', value))
                self.assert_bad(PROVIDER, '/verified')

    def test_all_denied_environment_names(self):
        denied = ('PATH', 'HOME', 'SHELL', 'IFS', 'ENV', 'BASH_ENV', 'PS4', 'NODE_OPTIONS',
                  'NODE_PATH', 'PYTHONPATH', 'PYTHONSTARTUP', 'PERL5OPT', 'PERL5LIB',
                  'RUBYOPT', 'RUBYLIB', 'LD_PRELOAD', 'LD_', 'DYLD_INSERT_LIBRARIES',
                  'GIT_SSH_COMMAND', 'SSH_AUTH_SOCK')
        for name in denied:
            with self.subTest(name=name):
                self.change(HARNESS, lambda d: d['env'][0].__setitem__('name', name))
                self.assert_bad(HARNESS, '/env/0/name')

    def test_duplicate_env_names(self):
        self.change(HARNESS, lambda d: d['env'].append(copy.deepcopy(d['env'][0])))
        self.assert_bad(HARNESS, '/env/1/name')

    def test_bare_commands_and_aliases(self):
        for field in ('command', 'aliases'):
            for value in ('foo/bar', 'foo bar', '..', '.', 'x;evil', '-x\n'):
                with self.subTest(field=field, value=value):
                    self.change(HARNESS, lambda d: d.__setitem__(field, [value] if field == 'aliases' else value))
                    self.assert_bad(HARNESS, '/' + field + ('/0' if field == 'aliases' else ''))

    def test_unknown_adapter(self):
        self.change(HARNESS, lambda d: d.__setitem__('adapter', 'shell_script'))
        self.assert_bad(HARNESS, '/adapter')

    def test_flags_and_probe(self):
        self.change(HARNESS, lambda d: d.__setitem__('version_probe', ['--help']))
        self.assert_bad(HARNESS, '/version_probe/0')
        self.change(HARNESS, lambda d: d.__setitem__('profile_flag', '--a;bad'))
        self.assert_bad(HARNESS, '/profile_flag')

    def test_version_match_regex(self):
        for pattern in ('v[0-9]+', '('):
            with self.subTest(pattern=pattern):
                self.change(HARNESS, lambda d: d.__setitem__('version_match', {'major_pattern': pattern}))
                self.assert_bad(HARNESS, '/version_match/major_pattern')

    def test_input_modalities_require_text(self):
        self.change(MODELS, lambda d: d['models'][0].__setitem__('input_modalities', ['image']))
        self.assert_bad(MODELS, '/models/0/input_modalities')

    def test_missing_provider(self):
        (self.root / PROVIDER).rename(self.root / 'providers/x.json')
        (self.root / MODELS).rename(self.root / 'models/orphan.json')
        self.change('models/orphan.json', lambda d: d.__setitem__('provider', 'orphan'))
        self.assert_bad('models/orphan.json', '/provider')

    def test_stray_files_and_directories(self):
        for name, directory in (('stray.txt', False), ('subdir', True), ('bad.json', True)):
            with self.subTest(name=name):
                path = self.root / 'providers' / name
                path.mkdir() if directory else path.write_text('example')
                self.assert_bad('providers/' + name, '')

    def test_symlink_file_and_directory(self):
        (self.root / 'providers/link.json').symlink_to(self.root / PROVIDER)
        self.assert_bad('providers/link.json', '')
        shutil.rmtree(self.root / 'harnesses')
        (self.root / 'harnesses').symlink_to(VALID / 'harnesses', target_is_directory=True)
        self.assert_bad('harnesses', '')

    def test_media_ignored(self):
        media = self.root / 'media/subdir'
        media.mkdir(parents=True)
        (media / 'not-json').write_bytes(b'\xff')
        self.assertEqual(self.run_validator().returncode, 0)

    def test_duplicate_json_key(self):
        (self.root / PROVIDER).write_text('{"id": "one", "id": "two"}')
        self.assert_bad(PROVIDER, '')

    def test_non_finite_numbers(self):
        for number in ('NaN', 'Infinity', '-Infinity', '1e9999'):
            with self.subTest(number=number):
                (self.root / PROVIDER).write_text('{"number": ' + number + '}')
                self.assert_bad(PROVIDER, '')

    def test_oversize(self):
        path = self.root / PROVIDER
        valid = path.read_bytes()
        size = 1024 * 1024 + 1
        padded = valid.replace(b'{', b'{' + b' ' * (size - len(valid)), 1)
        self.assertEqual(len(padded), size)
        self.assertEqual(json.loads(padded), json.loads(valid))
        path.write_bytes(padded)
        report = self.assert_bad(PROVIDER, '')
        self.assertTrue(any(problem['path'] == PROVIDER
                            and problem['message'] == 'file exceeds 1048576 bytes (1 MiB)'
                            for problem in report['problems']), report)

    def test_just_under_size_limit_valid_provider(self):
        path = self.root / PROVIDER
        valid = path.read_bytes()
        size = 1024 * 1024 - 1
        path.write_bytes(valid.replace(b'{', b'{' + b' ' * (size - len(valid)), 1))
        self.assertEqual(path.stat().st_size, size)
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_non_utf8(self):
        (self.root / PROVIDER).write_bytes(b'\xff')
        self.assert_bad(PROVIDER, '')

    def test_depth_limit(self):
        (self.root / PROVIDER).write_text('[' * 33 + '0' + ']' * 33)
        self.assert_bad(PROVIDER, '')

    def test_extreme_depth_no_traceback(self):
        (self.root / PROVIDER).write_text('[' * 2000 + '0' + ']' * 2000)
        self.assert_bad(PROVIDER, '')

    def test_malformed_json(self):
        (self.root / PROVIDER).write_text('{')
        self.assert_bad(PROVIDER, '')

    def test_json_report(self):
        result = self.run_validator('--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(set(report), {'valid', 'files_checked', 'problem_count', 'problems'})
        self.assertEqual(report, dict(valid=True, files_checked=3, problem_count=0, problems=[]))
        self.change(PROVIDER, lambda d: d.__setitem__('id', 'x' * 1000))
        report = self.assert_bad(PROVIDER, '/id')
        self.assertTrue(all(len(p['message']) < 240 for p in report['problems']))

    def test_usage_errors(self):
        for args in (['--unknown'], ['--root'], ['--root', str(self.root / 'missing')]):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('Traceback', result.stderr)

    def test_actual_schema_field_limits(self):
        cases = [
            (PROVIDER, (), 'schema_version', 2, '/schema_version'),
            (PROVIDER, (), 'schema_version', True, '/schema_version'),
            (PROVIDER, (), 'kind', 'harness', '/kind'),
            (PROVIDER, (), 'id', '-bad', '/id'),
            (PROVIDER, (), 'id', 'x' * 41, '/id'),
            (PROVIDER, (), 'display_name', '', '/display_name'),
            (PROVIDER, (), 'display_name', 'x' * 81, '/display_name'),
            (PROVIDER, (), 'protocols', [], '/protocols'),
            (PROVIDER, (), 'protocols', ['openai_chat', 'openai_chat'], '/protocols/1'),
            (PROVIDER, (), 'protocols', ['custom'], '/protocols/0'),
            (PROVIDER, (), 'auth', 'custom', '/auth'),
            (PROVIDER, (), 'note', 'x' * 501, '/note'),
            (PROVIDER, (), 'sources', [], '/sources'),
            (PROVIDER, (), 'sources', ['https://example.com'] * 21, '/sources'),
            (PROVIDER, (), 'sources', ['http://example.com'], '/sources/0'),
            (MODELS, (), 'models', [], '/models'),
            (MODELS, ('models', 0), 'id', 'example model', '/models/0/id'),
            (MODELS, ('models', 0), 'id', 'x' * 129, '/models/0/id'),
            (MODELS, ('models', 0), 'display_name', '', '/models/0/display_name'),
            (MODELS, ('models', 0), 'status', 'custom', '/models/0/status'),
            (MODELS, ('models', 0), 'tier', 'premium', '/models/0/tier'),
            (MODELS, ('models', 0), 'max_output_tokens', -1, '/models/0/max_output_tokens'),
            (MODELS, ('models', 0), 'input_modalities', [], '/models/0/input_modalities'),
            (MODELS, ('models', 0), 'input_modalities', ['text', 'text'], '/models/0/input_modalities/1'),
            (MODELS, ('models', 0), 'input_modalities', ['text', 'custom'], '/models/0/input_modalities/1'),
            (MODELS, ('models', 0), 'probe', 1, '/models/0/probe'),
            (MODELS, ('models', 0), 'default', 'true', '/models/0/default'),
            (MODELS, ('models', 0, 'pricing'), 'batch_discount_percent', 101, '/models/0/pricing/batch_discount_percent'),
            (MODELS, ('models', 0, 'pricing'), 'batch_discount_percent', -1, '/models/0/pricing/batch_discount_percent'),
            (MODELS, ('models', 0, 'pricing'), 'input', 'unknown', '/models/0/pricing/input'),
            (HARNESS, (), 'aliases', ['example'] * 9, '/aliases'),
            (HARNESS, (), 'aliases', ['example', 'example'], '/aliases/1'),
            (HARNESS, (), 'config_style', 'x' * 41, '/config_style'),
            (HARNESS, (), 'env', [{}] * 17, '/env'),
            (HARNESS, ('env', 0), 'name', 'bad_name', '/env/0/name'),
            (HARNESS, ('env', 0), 'name', 'X' * 65, '/env/0/name'),
            (HARNESS, ('env', 0), 'role', 'command', '/env/0/role'),
            (HARNESS, (), 'profile_flag', '--Bad', '/profile_flag'),
            (HARNESS, (), 'version_probe', ['--version'] * 3, '/version_probe'),
            (HARNESS, (), 'version_match', {'major_pattern': 'x' * 101}, '/version_match/major_pattern'),
            (HARNESS, (), 'icon', '../icon.svg', '/icon'),
            (HARNESS, (), 'note', 'x' * 501, '/note'),
        ]
        for file, location, field, value, at in cases:
            with self.subTest(file=file, field=field, value=str(value)[:40]):
                shutil.copyfile(VALID / file, self.root / file)
                def edit(data):
                    target = data
                    for token in location:
                        target = target[token]
                    target[field] = value
                self.change(file, edit)
                self.assert_bad(file, at)
                shutil.copyfile(VALID / file, self.root / file)

    def test_missing_required_nested_fields(self):
        for file, location, field, at in (
            (MODELS, ('models', 0, 'pricing'), 'cache_read', '/models/0/pricing/cache_read'),
            (HARNESS, ('env', 0), 'note', '/env/0/note'),
            (HARNESS, ('version_match',), 'major_pattern', '/version_match/major_pattern'),
            (MODELS, ('models', 0), 'sources', '/models/0/sources')):
            with self.subTest(at=at):
                def edit(data):
                    target = data
                    for token in location:
                        target = target[token]
                    target.pop(field)
                self.change(file, edit)
                self.assert_bad(file, at)
                shutil.copyfile(VALID / file, self.root / file)

    def test_null_token_limits_and_optional_harness_config(self):
        self.change(MODELS, lambda d: d['models'][0].update(context_window=None, max_output_tokens=None))
        self.change(HARNESS, lambda d: d.update(config_style=None, env=[], aliases=[],
                                             profile_flag=None, model_flag=None,
                                             version_probe=[], version_match=None))
        self.assertEqual(self.run_validator().returncode, 0)

    def test_base_url_ipv6_and_query_on_source_are_valid(self):
        self.change(PROVIDER, lambda d: d.update(base_url='https://[::1]:443/v1',
                                               sources=['https://example.com/docs?edition=example#details']))
        self.assertEqual(self.run_validator().returncode, 0)

    def test_bad_date_on_model_harness_and_shutdown(self):
        self.change(MODELS, lambda d: d['models'][0].__setitem__('verified', '2026-02-30'))
        self.assert_bad(MODELS, '/models/0/verified')
        self.change(HARNESS, lambda d: d.__setitem__('verified', '2026-02-30'))
        self.assert_bad(HARNESS, '/verified')
        self.change(MODELS, lambda d: d['models'][1].update(status='deprecated', shutdown='2026-02-30'))
        self.assert_bad(MODELS, '/models/1/shutdown')

    def test_all_url_locations_reject_userinfo(self):
        for file in (PROVIDER, HARNESS):
            for field in ('docs_url', 'sources'):
                with self.subTest(file=file, field=field):
                    value = 'https://user@example.com/docs'
                    self.change(file, lambda d: d.__setitem__(field, [value] if field == 'sources' else value))
                    self.assert_bad(file, '/' + field + ('/0' if field == 'sources' else ''))
        self.change(MODELS, lambda d: d['models'][0].__setitem__('sources', ['https://user@example.com']))
        self.assert_bad(MODELS, '/models/0/sources/0')

    def test_nonnumeric_and_wrong_object_shapes_report_not_crash(self):
        for file, value, at in ((PROVIDER, None, ''), (MODELS, {'models': [None, {}]}, '/schema_version'),
                                (HARNESS, {'env': [None, {'name': []}], 'version_match': []}, '/schema_version')):
            with self.subTest(file=file):
                (self.root / file).write_text(json.dumps(value))
                self.assert_bad(file, at)

    def test_text_report_escapes_untrusted_paths_and_values(self):
        bad = self.root / 'providers' / 'bad\nname.txt'
        bad.write_text('example')
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(result.stdout.splitlines()), 2)
        self.assertIn('bad\\nname.txt', result.stdout)

    def test_unsupported_keyword_guard(self):
        spec = importlib.util.spec_from_file_location('registry_validator', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for schema in ({'type': 'string', 'format': 'uri'},
                       {'properties': {'x': {'allOf': []}}},
                       {'$defs': {'x': {'minProperties': 1}}}):
            with self.subTest(schema=schema):
                with self.assertRaises(module.SchemaError):
                    module.check_schema(schema)

    def test_schema_guard_fail_closed_in_cli(self):
        # Copy the program beside altered schemas: --root selects data, never policy.
        app = self.root / 'app'
        (app / 'scripts').mkdir(parents=True)
        shutil.copyfile(SCRIPT, app / 'scripts/validate.py')
        shutil.copytree(REPO / 'schema', app / 'schema')
        schema_file = app / 'schema/provider.schema.json'
        schema = json.loads(schema_file.read_text())
        schema['properties']['display_name']['format'] = 'hostname'
        schema_file.write_text(json.dumps(schema))
        result = subprocess.run([sys.executable, str(app / 'scripts/validate.py'), '--root', str(self.root), '--json'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['files_checked'], 0)
        self.assertIn('unsupported', report['problems'][0]['message'])


class SchemaEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('registry_validator_engine', SCRIPT)
        cls.engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.engine)

    def errors(self, value, schema):
        self.engine.check_schema(schema)
        return self.engine.schema_problems(value, schema)

    def test_type_union_number_null_and_bool(self):
        policy = {'type': ['number', 'null'], 'minimum': 0, 'maximum': 100}
        for value in (None, 0, 1.5, 100):
            with self.subTest(value=value):
                self.assertEqual(self.errors(value, policy), [])
        for value in (True, False, -1, 101, '1'):
            with self.subTest(value=value):
                self.assertTrue(self.errors(value, policy))

    def test_integer_matches_json_schema_math(self):
        policy = {'type': 'integer'}
        self.assertEqual(self.errors(1.0, policy), [])
        for value in (True, 1.1):
            self.assertTrue(self.errors(value, policy))

    def test_enum_and_const_distinguish_bool_from_number(self):
        for policy in ({'enum': [1]}, {'const': 1}):
            self.assertEqual(self.errors(1.0, policy), [])
            self.assertTrue(self.errors(True, policy))

    def test_unique_items_uses_json_equality(self):
        self.assertTrue(self.errors([1, 1.0], {'uniqueItems': True}))
        self.assertEqual(self.errors([1, True], {'uniqueItems': True}), [])
        self.assertTrue(self.errors([{'a': [1]}, {'a': [1.0]}], {'uniqueItems': True}))

    def test_string_bounds_and_fullmatch(self):
        policy = {'type': 'string', 'minLength': 2, 'maxLength': 3, 'pattern': '^a+$'}
        self.assertEqual(self.errors('aa', policy), [])
        for value in ('a', 'aaaa', 'aa\n', 'baa'):
            self.assertTrue(self.errors(value, policy))

    def test_array_bounds_items_and_not(self):
        policy = {'type': 'array', 'minItems': 1, 'maxItems': 2,
                  'items': {'type': 'string'}, 'not': {'items': {'enum': ['image']}}}
        self.assertEqual(self.errors(['text'], policy), [])
        for value in ([], ['image'], [1], ['text', 'image', 'audio']):
            self.assertTrue(self.errors(value, policy))

    def test_ref_siblings_and_annotations(self):
        policy = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
                  '$id': 'https://example.com/schema', 'title': 'Example', 'description': 'Example',
                  '$defs': {'identifier': {'type': 'string', 'minLength': 1}},
                  '$ref': '#/$defs/identifier', 'maxLength': 3}
        self.assertEqual(self.errors('abc', policy), [])
        self.assertTrue(self.errors('', policy))
        self.assertTrue(self.errors('abcd', policy))

    def test_required_and_additional_property_pointers(self):
        policy = {'type': 'object', 'properties': {'a/b~c': {'type': 'integer'}},
                  'required': ['a/b~c'], 'additionalProperties': False}
        self.assertEqual(self.errors({'a/b~c': 1}, policy), [])
        self.assertEqual(self.errors({}, policy)[0][0], '/a~1b~0c')
        self.assertEqual(self.errors({'a/b~c': 1, 'bad': 1}, policy)[0][0], '/bad')

    def test_if_then(self):
        policy = {'if': {'properties': {'status': {'const': 'deprecated'}}, 'required': ['status']},
                  'then': {'required': ['shutdown']}}
        self.assertEqual(self.errors({'status': 'ga'}, policy), [])
        self.assertEqual(self.errors({'status': 'deprecated', 'shutdown': '2026-01-01'}, policy), [])
        self.assertEqual(self.errors({'status': 'deprecated'}, policy)[0][0], '/shutdown')

    def test_guard_checks_every_schema_position(self):
        for wrapper in (lambda s: s, lambda s: {'properties': {'example': s}},
                        lambda s: {'$defs': {'example': s}}, lambda s: {'items': s},
                        lambda s: {'not': s}, lambda s: {'if': s},
                        lambda s: {'if': {}, 'then': s}):
            with self.subTest(wrapper=wrapper):
                with self.assertRaises(self.engine.SchemaError):
                    self.engine.check_schema(wrapper({'format': 'date'}))

    def test_guard_malformed_keyword_shapes(self):
        policies = [[], {'type': []}, {'type': ['string', 'typo']}, {'type': [1]},
                    {'type': ['string', 'string']}, {'properties': []}, {'items': True},
                    {'required': 'id'}, {'required': ['id', 'id']}, {'enum': []},
                    {'enum': [1, 1.0]}, {'additionalProperties': True},
                    {'uniqueItems': 'true'}, {'minItems': True}, {'maxLength': -1},
                    {'minimum': True}, {'pattern': 'unanchored'}, {'pattern': '^[$'},
                    {'then': {}}, {'title': 3}]
        for policy in policies:
            with self.subTest(policy=policy):
                with self.assertRaises(self.engine.SchemaError):
                    self.engine.check_schema(policy)

    def test_guard_local_refs_only_and_no_cycles(self):
        for policy in ({'$ref': 'https://example.com/schema'}, {'$ref': '#/$defs/missing'},
                       {'$defs': {'loop': {'$ref': '#/$defs/loop'}}},
                       {'$defs': {'a': {'$ref': '#/$defs/b'}, 'b': {'$ref': '#/$defs/a'}}}):
            with self.subTest(policy=policy):
                with self.assertRaises(self.engine.SchemaError):
                    self.engine.check_schema(policy)

    def test_schema_and_semantics_independently_deny_every_env_name(self):
        schema = json.loads((REPO / 'schema/harness.schema.json').read_text())
        original = json.loads((VALID / HARNESS).read_text())
        denied = ('PATH', 'HOME', 'SHELL', 'IFS', 'ENV', 'BASH_ENV', 'PS4', 'NODE_OPTIONS',
                  'NODE_PATH', 'PYTHONPATH', 'PYTHONSTARTUP', 'PERL5OPT', 'PERL5LIB',
                  'RUBYOPT', 'RUBYLIB', 'LD_PRELOAD', 'DYLD_INSERT_LIBRARIES',
                  'GIT_SSH_COMMAND', 'SSH_AUTH_SOCK', 'LD_', 'DYLD_', 'GIT_', 'SSH_')
        relaxed = copy.deepcopy(schema)
        relaxed['properties']['env']['items']['properties']['name'] = {'type': 'string'}
        self.engine.check_schema(relaxed)
        for name in denied:
            with self.subTest(name=name):
                data = copy.deepcopy(original)
                data['env'][0]['name'] = name
                self.assertIn('/env/0/name', [p for p, _ in self.engine.schema_problems(data, schema)])
                self.assertEqual(self.engine.schema_problems(data, relaxed), [])
                semantic = self.engine.semantic_problems(data, 'harness', 'example-cli', set(), datetime.now(timezone.utc).date())
                self.assertIn('/env/0/name', [p for p, _ in semantic])

    def test_schema_and_semantics_independently_restrict_commands(self):
        schema = json.loads((REPO / 'schema/harness.schema.json').read_text())
        relaxed = copy.deepcopy(schema)
        relaxed['$defs']['bare_command'] = {'type': 'string'}
        original = json.loads((VALID / HARNESS).read_text())
        for field in ('command', 'aliases'):
            for value in ('.', '..', 'example/cli', 'example cli', 'example;echo'):
                with self.subTest(field=field, value=value):
                    data = copy.deepcopy(original)
                    data[field] = [value] if field == 'aliases' else value
                    at = '/' + field + ('/0' if field == 'aliases' else '')
                    self.assertIn(at, [p for p, _ in self.engine.schema_problems(data, schema)])
                    self.assertEqual(self.engine.schema_problems(data, relaxed), [])
                    semantic = self.engine.semantic_problems(data, 'harness', 'example-cli', set(), datetime.now(timezone.utc).date())
                    self.assertIn(at, [p for p, _ in semantic])

    def test_depth_boundary_and_quoted_delimiters(self):
        self.engine.check_depth('[' * 32 + '0' + ']' * 32)
        self.engine.check_depth(json.dumps('"' + '[' * 1000 + '\\'))
        with self.assertRaises(self.engine.InputError):
            self.engine.check_depth('[' * 33 + '0' + ']' * 33)

    def test_semantic_pass_tolerates_schema_invalid_shapes(self):
        # An adversarial type error must be a validation result, never a traceback.
        for kind, record in (
            ('provider', {'verified': {}, 'sources': [None]}),
            ('models', {'models': [None, {'id': [], 'shutdown': {}, 'verified': []}]}),
            ('harness', {'env': [None, {'name': []}], 'aliases': [{}], 'version_match': []})):
            self.engine.semantic_problems(record, kind, 'example', set(), datetime.now(timezone.utc).date())


if __name__ == '__main__':
    unittest.main()
