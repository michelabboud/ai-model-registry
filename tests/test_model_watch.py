"""Offline behavior tests; fixtures and keys are entirely invented.
Adapted from michelabboud/genie-registry scripts/model_watch.py (Michel's own repository), 2026-11-15.
"""
import contextlib
import email.message
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('model_watch', ROOT / 'scripts/model_watch.py')
mw = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mw
SPEC.loader.exec_module(mw)
FIXTURES = ROOT / 'tests/fixtures/model_watch'
SENTINEL = 'fixture-secret-never-a-real-key'
ALL_KEYS = {name: SENTINEL for name in ('OPENAI_MODELS_KEY', 'ANTHROPIC_MODELS_KEY',
    'GEMINI_MODELS_KEY', 'XAI_MODELS_KEY', 'DEEPSEEK_MODELS_KEY')}


def fixture(name):
    return json.loads((FIXTURES / (name + '.json')).read_text())


def vendor(name):
    return next(v for v in mw.VENDORS if v.name == name)


def routes():
    data = {v.list_url: fixture(v.name) for v in mw.VENDORS
            if v.name not in ('anthropic', 'gemini')}
    data[vendor('anthropic').list_url] = fixture('anthropic_page1')
    data[vendor('anthropic').list_url + '&after_id=fixture-old'] = fixture('anthropic_page2')
    data[vendor('gemini').list_url] = fixture('gemini_page1')
    data[vendor('gemini').list_url + '&pageToken=fixture-page-2'] = fixture('gemini_page2')
    return data


class FakeOpener:
    def __init__(self, responses):
        self.responses, self.calls = responses, []

    def open(self, request, timeout):
        self.calls.append((request.full_url, {k.lower(): v for k, v in request.header_items()}))
        if request.full_url not in self.responses:
            raise AssertionError('unexpected mocked URL; real network forbidden')
        value = self.responses[request.full_url]
        if isinstance(value, Exception):
            raise value
        return io.BytesIO(value if isinstance(value, bytes) else json.dumps(value).encode())


class WatchCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='registry-watch-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for d in ('providers', 'models'):
            (self.root / d).mkdir()
        for v in mw.VENDORS:
            (self.root / 'providers' / (v.name + '.json')).write_text(json.dumps({
                'id': v.name, 'docs_url': 'https://docs.example.invalid/' + v.name}))
            prefix = 'openai/' if v.name == 'openrouter' else ''
            records = [{'id': prefix + model_id, 'status': status,
                        'sources': ['https://prices.example.invalid/' + v.name]}
                       for model_id, status in [('fixture-old', 'ga'),
                            ('fixture-missing', 'preview'), ('fixture-deprecated', 'deprecated')]]
            (self.root / 'models' / (v.name + '.json')).write_text(json.dumps({
                'provider': v.name, 'models': records}))

    def run_watch(self, env=None, responses=None, extra=()):
        opener = FakeOpener(routes() if responses is None else responses)
        out, err = io.StringIO(), io.StringIO()
        args = ['--root', str(self.root), '--pr-body', str(self.root / 'out/body.md'),
                '--summary', str(self.root / 'summary.md'),
                '--github-output', str(self.root / 'outputs')]
        with mock.patch.object(mw, '_OPENER', opener), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = mw.run(args + list(extra), env=ALL_KEYS if env is None else env)
        return code, out.getvalue(), err.getvalue(), opener

    def worksheet(self, name):
        return (self.root / 'candidates' / (name + '.md')).read_text()

    def captured(self, out='', err=''):
        return out + err + ''.join(p.read_text(errors='replace') for p in self.root.rglob('*')
            if p.is_file() and not p.is_symlink())

    def matching_routes(self):
        data = {}
        for v in mw.VENDORS:
            prefix = 'openai/' if v.name == 'openrouter' else ''
            ids = [prefix + 'fixture-old', prefix + 'fixture-missing']
            if v.name == 'gemini':
                data[v.list_url] = {'models': [{'name': 'models/' + i,
                    'supportedGenerationMethods': ['generateContent']} for i in ids]}
            else:
                data[v.list_url] = {'data': [{'id': i} for i in ids]}
                if v.name == 'anthropic':
                    data[v.list_url].update(has_more=False, last_id=ids[-1])
        return data


class Detection(WatchCase):
    def test_six_vendors_new_missing_not_deprecated(self):
        code, out, err, _ = self.run_watch()
        self.assertEqual(code, 3, err)
        for v in mw.VENDORS:
            text = self.worksheet(v.name)
            self.assertIn('fixture-new', text)
            self.assertIn('fixture-missing', text)
            self.assertNotIn('fixture-deprecated', text)
            self.assertIn("Confirm the retirement in the vendor's deprecation notes before removing it;", text)
            self.assertIn('a key without access to a model also hides it.', text)
            self.assertIn('TO VERIFY', text)
            self.assertIn('https://docs.example.invalid/' + v.name, text)
            self.assertIn('https://prices.example.invalid/' + v.name, text)
        self.assertIn('| OpenAI | checked | 1 | 1 | 1 | 0 |', out)

    def test_no_changes_exit_zero_complete_true(self):
        code, _, err, opener = self.run_watch(responses=self.matching_routes())
        self.assertEqual(code, 0, err)
        self.assertFalse((self.root / 'candidates').exists())
        self.assertEqual(len(opener.calls), 6)
        self.assertIn('complete=true', (self.root / 'outputs').read_text())
        self.assertTrue((self.root / 'out/body.md').is_file())

    def test_resolved_known_worksheet_removed_unknown_untouched(self):
        directory = self.root / 'candidates'
        directory.mkdir()
        (directory / 'openai.md').write_text('prior generated worksheet')
        (directory / 'unknown.md').write_text('unrelated user file')
        self.run_watch(responses=self.matching_routes())
        self.assertFalse((directory / 'openai.md').exists())
        self.assertEqual((directory / 'unknown.md').read_text(), 'unrelated user file')

    def test_absent_secret_skips_preserves_and_marks_possibly_stale(self):
        directory = self.root / 'candidates'
        directory.mkdir()
        (directory / 'openai.md').write_text('previous worksheet')
        code, out, err, opener = self.run_watch(env={}, responses=self.matching_routes())
        self.assertEqual(code, 0, err)
        self.assertEqual([u for u, _ in opener.calls], [vendor('openrouter').list_url])
        self.assertEqual(self.worksheet('openai'), 'previous worksheet')
        self.assertIn('possibly stale', out)
        outputs = (self.root / 'outputs').read_text()
        self.assertIn('complete=false', outputs)
        self.assertIn('skipped=openai anthropic gemini xai deepseek', outputs)

    def test_error_exit_one_preserves_all_prior_worksheets(self):
        directory = self.root / 'candidates'
        directory.mkdir()
        (directory / 'openai.md').write_text('preserve prior evidence')
        data = routes()
        data[vendor('deepseek').list_url] = {'unexpected': []}
        code, out, err, _ = self.run_watch(responses=data)
        self.assertEqual(code, 1)
        self.assertIn('DeepSeek failed', err)
        self.assertEqual(self.worksheet('openai'), 'preserve prior evidence')
        self.assertEqual(list(directory.iterdir()), [directory / 'openai.md'])
        self.assertNotIn(SENTINEL, self.captured(out, err))

    def test_registry_bytes_never_modified(self):
        before = {str(p): p.read_bytes() for d in ('providers', 'models') for p in (self.root / d).iterdir()}
        self.run_watch()
        self.assertEqual(before, {p: Path(p).read_bytes() for p in before})

    def test_proposals_cover_required_model_and_pricing_fields(self):
        self.run_watch()
        schema = json.loads((ROOT / 'schema/models.schema.json').read_text())
        text = self.worksheet('openai')
        for field in schema['$defs']['model']['required']:
            if field != 'pricing':
                self.assertIn('`' + field + '` | TO VERIFY', text)
        for field in schema['$defs']['pricing']['required']:
            self.assertIn('`pricing.' + field + '` | TO VERIFY', text)
        self.assertNotIn('```json', text)


class Selection(WatchCase):
    def test_exclusion_families_per_vendor(self):
        for v in mw.VENDORS:
            for model_id in ['fixture-embedding', 'fixture-image', 'fixture-audio', 'fixture-tts',
                    'fixture-whisper', 'fixture-moderation', 'fixture-realtime', 'fixture-ocr',
                    'fixture-transcribe', 'fixture-video']:
                prefix = 'openai/' if v.name == 'openrouter' else ''
                with self.subTest(vendor=v.name, model_id=model_id):
                    self.assertFalse(mw.is_text_candidate(v, prefix + model_id))
            self.assertTrue(mw.is_text_candidate(v, ('openai/' if v.name == 'openrouter' else '') + 'fixture-vision-text'))

    def test_vendor_specific_non_text_names(self):
        for name, ids in {'openai': ['dall-e-fixture', 'sora-fixture'],
                          'gemini': ['imagen-fixture', 'veo-fixture']}.items():
            for model_id in ids:
                self.assertFalse(mw.is_text_candidate(vendor(name), model_id))

    def test_openrouter_prefix_batch_filters(self):
        self.run_watch()
        text = self.worksheet('openrouter')
        for prefix in ['anthropic', 'google', 'deepseek', 'z-ai', 'x-ai']:
            self.assertIn(prefix + '/fixture-new', text)
        for excluded in ['other/fixture-unwanted', ':batch', 'gpt-image-fixture']:
            self.assertNotIn(excluded, text)
        self.assertFalse(mw.is_text_candidate(vendor('openrouter'), 'openai-spoof/fixture-new'))

    def test_gemini_generate_content_and_name_filters(self):
        self.run_watch()
        text = self.worksheet('gemini')
        self.assertNotIn('fixture-embed', text)
        self.assertNotIn('gemini-fixture-image', text)

    def test_listed_non_generating_id_is_not_missing(self):
        data = self.matching_routes()
        data[vendor('gemini').list_url]['models'][0]['supportedGenerationMethods'] = ['countTokens']
        code, _, err, _ = self.run_watch(responses=data)
        self.assertEqual(code, 0, err)


class PagingAndShapes(WatchCase):
    def test_both_vendors_paginate(self):
        code, _, err, opener = self.run_watch()
        self.assertEqual(code, 3, err)
        urls = [u for u, _ in opener.calls]
        self.assertIn(vendor('anthropic').list_url + '&after_id=fixture-old', urls)
        self.assertIn(vendor('gemini').list_url + '&pageToken=fixture-page-2', urls)
        self.assertEqual(len(urls), 8)

    def test_too_many_pages_refused(self):
        for name in ('anthropic', 'gemini'):
            data = self.matching_routes()
            v = vendor(name)
            if name == 'anthropic':
                page = {'data': [{'id': 'fixture-cursor'}], 'has_more': True, 'last_id': 'fixture-cursor'}
                next_url = v.list_url + '&after_id=fixture-cursor'
            else:
                page = {'models': [], 'nextPageToken': 'fixture-loop'}
                next_url = v.list_url + '&pageToken=fixture-loop'
            data[v.list_url] = data[next_url] = page
            code, _, err, opener = self.run_watch(responses=data)
            self.assertEqual(code, 1)
            self.assertIn('exceeds 10 pages', err)
            self.assertEqual(sum(u.startswith(v.list_url) for u, _ in opener.calls), 10)

    def test_entry_budget_across_pages(self):
        data = self.matching_routes()
        entries = [{'id': 'fixture-' + str(i)} for i in range(1100)]
        v = vendor('anthropic')
        data[v.list_url] = {'data': entries, 'has_more': True, 'last_id': entries[-1]['id']}
        data[v.list_url + '&after_id=' + entries[-1]['id']] = {'data': entries, 'has_more': False}
        code, _, err, _ = self.run_watch(responses=data)
        self.assertEqual(code, 1)
        self.assertIn('exceeds 2000 entries', err)

    def test_byte_budget_across_pages(self):
        data = self.matching_routes()
        v = vendor('gemini')
        padding = ' ' * (mw.MAX_RESPONSE_BYTES // 2)
        data[v.list_url] = (json.dumps({'models': [], 'nextPageToken': 'fixture-p2'}) + padding).encode()
        data[v.list_url + '&pageToken=fixture-p2'] = (json.dumps({'models': []}) + padding).encode()
        code, _, err, _ = self.run_watch(responses=data)
        self.assertEqual(code, 1)
        self.assertIn('bytes', err)

    def test_unexpected_shapes_fail_without_guessing(self):
        for name, payload in [('anthropic', {'data': []}), ('deepseek', {'models': []}),
                ('xai', {'models': []}), ('gemini', {'models': [{'name': 'models/fixture-new'}]})]:
            data = self.matching_routes()
            data[vendor(name).list_url] = payload
            code, _, err, _ = self.run_watch(responses=data)
            self.assertEqual(code, 1, name)
            self.assertIn('failed:', err)

    def test_hostile_page_cursors_not_echoed(self):
        hostile = 'fixture-cursor&key=SECRET-REFLECTION'
        for name in ('anthropic', 'gemini'):
            data = self.matching_routes()
            data[vendor(name).list_url] = ({'data': [], 'has_more': True, 'last_id': hostile}
                if name == 'anthropic' else {'models': [], 'nextPageToken': hostile})
            code, out, err, _ = self.run_watch(responses=data)
            self.assertEqual(code, 1)
            self.assertNotIn('SECRET-REFLECTION', self.captured(out, err))

    def test_single_listing_entry_budget(self):
        data = self.matching_routes()
        data[vendor('openrouter').list_url] = {'data': [{'id': 'other/fixture'}] * 2001}
        code, _, err, _ = self.run_watch(responses=data)
        self.assertEqual(code, 1)
        self.assertIn('2000 entries', err)


class CredentialsAndHostility(WatchCase):
    def test_headers_only_public_vendor_no_auth_and_no_output_leaks(self):
        _, out, err, opener = self.run_watch()
        for url, headers in opener.calls:
            self.assertNotIn(SENTINEL, url)
            if url.startswith(vendor('openrouter').list_url):
                self.assertNotIn('authorization', headers)
                self.assertFalse(any(v == SENTINEL for v in headers.values()))
            elif url.startswith(vendor('anthropic').list_url):
                self.assertEqual(headers['x-api-key'], SENTINEL)
                self.assertEqual(headers['anthropic-version'], '2023-06-01')
            elif url.startswith(vendor('gemini').list_url):
                self.assertEqual(headers['x-goog-api-key'], SENTINEL)
            else:
                self.assertEqual(headers['authorization'], 'Bearer ' + SENTINEL)
        self.assertNotIn(SENTINEL, self.captured(out, err))

    def test_surrounding_key_whitespace_stripped(self):
        _, _, _, opener = self.run_watch(env=dict(ALL_KEYS, OPENAI_MODELS_KEY=' \t' + SENTINEL + '\r\n'))
        headers = next(h for u, h in opener.calls if u == vendor('openai').list_url)
        self.assertEqual(headers['authorization'], 'Bearer ' + SENTINEL)

    def test_whitespace_only_key_skipped(self):
        _, out, _, opener = self.run_watch(env=dict(ALL_KEYS, OPENAI_MODELS_KEY=' \n\t'))
        self.assertIn('OPENAI_MODELS_KEY is not set', out)
        self.assertNotIn(vendor('openai').list_url, [u for u, _ in opener.calls])

    def test_invalid_keys_refused_by_name_not_value(self):
        for value in (SENTINEL + 'é', SENTINEL + '\nX', SENTINEL + ' X', SENTINEL + '\x00'):
            code, out, err, opener = self.run_watch(env=dict(ALL_KEYS, OPENAI_MODELS_KEY=value))
            self.assertEqual(code, 1)
            self.assertIn('OPENAI_MODELS_KEY contains invalid characters', err)
            self.assertNotIn(vendor('openai').list_url, [u for u, _ in opener.calls])
            self.assertNotIn(SENTINEL, self.captured(out, err))

    def test_hostile_ids_dropped_counted_never_echoed(self):
        hostile = ['../../HOSTILE', 'fake`HOSTILE`', 'fake\nHOSTILE', 'é-HOSTILE',
                   'fake..HOSTILE', 'HOSTILE' * 25, None, 42]
        data = self.matching_routes()
        data[vendor('openai').list_url]['data'] += [{'id': i} for i in hostile]
        code, out, err, _ = self.run_watch(responses=data)
        self.assertEqual(code, 0, err)
        self.assertIn('| OpenAI | checked | 0 | 0 | 2 | 8 |', out)
        self.assertNotIn('HOSTILE', self.captured(out, err))

    def test_transport_error_text_not_echoed(self):
        data = self.matching_routes()
        data[vendor('openai').list_url] = ValueError('reflected ' + SENTINEL)
        code, out, err, _ = self.run_watch(responses=data)
        self.assertEqual(code, 1)
        self.assertNotIn(SENTINEL, self.captured(out, err))

    def test_reflected_key_in_vendor_model_ids_fails_without_publication(self):
        for v in mw.VENDORS:
            with self.subTest(vendor=v.name):
                data = self.matching_routes()
                reflected = ('openai/' if v.name == 'openrouter' else '') + SENTINEL
                if v.name == 'gemini':
                    data[v.list_url]['models'].append({'name': 'models/' + reflected,
                        'supportedGenerationMethods': ['generateContent']})
                else:
                    data[v.list_url]['data'].append({'id': reflected})
                code, out, err, _ = self.run_watch(responses=data)
                self.assertEqual(code, 1)
                self.assertNotIn(SENTINEL, self.captured(out, err))
                self.assertFalse((self.root / 'candidates').exists())

    def test_reflected_keys_never_enter_pagination_urls(self):
        for name in ('anthropic', 'gemini'):
            with self.subTest(vendor=name):
                data = self.matching_routes()
                v = vendor(name)
                if name == 'anthropic':
                    data[v.list_url] = {'data': [{'id': SENTINEL}],
                        'has_more': True, 'last_id': SENTINEL}
                    data[v.list_url + '&after_id=' + SENTINEL] = {'data': [], 'has_more': False}
                else:
                    data[v.list_url] = {'models': [], 'nextPageToken': SENTINEL}
                    data[v.list_url + '&pageToken=' + SENTINEL] = {'models': []}
                code, out, err, opener = self.run_watch(responses=data)
                self.assertEqual(code, 1)
                self.assertTrue(all(SENTINEL not in url for url, _ in opener.calls))
                self.assertNotIn(SENTINEL, self.captured(out, err))
                self.assertFalse((self.root / 'candidates').exists())

    def test_output_flags_cannot_overwrite_registry(self):
        target = self.root / 'models/openai.json'
        before = target.read_bytes()
        code, _, _, opener = self.run_watch(extra=['--pr-body', str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(opener.calls, [])

    def test_candidates_symlink_refused(self):
        (self.root / 'candidates').symlink_to(self.root / 'models', target_is_directory=True)
        code, _, _, _ = self.run_watch()
        self.assertEqual(code, 1)
        self.assertFalse((self.root / 'models/openai.md').exists())


class Transport(unittest.TestCase):
    def fetch(self, body):
        opener = FakeOpener({'https://models.example.invalid/': body})
        with mock.patch.object(mw, '_OPENER', opener):
            return mw.fetch_json('https://models.example.invalid/', {})

    def test_redirects_refused(self):
        request = urllib.request.Request('https://api.openai.com/v1/models')
        for status in (301, 302, 303, 307, 308):
            with self.assertRaises(mw.WatchError):
                mw._RefuseRedirects().redirect_request(request, None, status, '', {}, 'https://hostile.example.invalid/')

    def test_non_https_refused_before_network(self):
        with mock.patch.object(mw, '_OPENER') as opener, self.assertRaises(mw.WatchError):
            mw.fetch_json('http://models.example.invalid/', {})
        opener.open.assert_not_called()

    def test_http_error_status_only(self):
        error = urllib.error.HTTPError('https://models.example.invalid/?' + SENTINEL, 401,
            SENTINEL, email.message.Message(), io.BytesIO(SENTINEL.encode()))
        with self.assertRaises(mw.WatchError) as caught:
            self.fetch(error)
        self.assertEqual(str(caught.exception), 'HTTP 401')
        self.assertIsNone(caught.exception.__cause__)

    def test_oversized_body_refused(self):
        with self.assertRaisesRegex(mw.WatchError, 'bytes'):
            self.fetch(b' ' * (mw.MAX_RESPONSE_BYTES + 1))

    def test_hostile_json_refused(self):
        for body in (b'[' * 100000, b'{"n":' + b'9' * 5000 + b'}',
                     b'{"data": [], "data": []}', b'{"n":NaN}', b'\xff'):
            with self.subTest(body=body[:20]), self.assertRaises(mw.WatchError):
                self.fetch(body)


if __name__ == '__main__':
    unittest.main()
