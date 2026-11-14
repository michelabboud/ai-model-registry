"""Pre-release cache contract tests; all values are invented."""
import copy
import importlib.util
import json
from datetime import date
from pathlib import Path
from typing import Any
import unittest


REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cache_validator', REPO / 'scripts/validate.py')
assert spec is not None and spec.loader is not None
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CachePricingTests(unittest.TestCase):
    schema: dict[str, Any] = {}
    data: dict[str, Any] = {}
    pricing: dict[str, Any] = {}

    def setUp(self):
        self.schema = json.loads((REPO / 'schema/models.schema.json').read_text())
        self.data = json.loads((REPO / 'tests/fixtures/valid/models/example-provider.json').read_text())
        self.pricing = self.data['models'][0]['pricing']

    def errors(self):
        validator.check_schema(self.schema)
        return (validator.schema_problems(self.data, self.schema)
                + validator.semantic_problems(self.data, 'models', 'example-provider',
                                              {'example-provider'}, date(2026, 11, 14)))

    def locations(self) -> tuple[dict[str, Any], dict[str, Any]]:
        # Exercise the same contract at standard and long-context rates.
        return (self.pricing, dict(threshold_tokens=100000,
                                  **{key: copy.deepcopy(self.pricing[key])
                                     for key in ('input', 'output', 'cache_read', 'cache_writes')}))

    def test_long_context_threshold_description_defines_strict_input_boundary(self):
        threshold = self.schema['$defs']['pricing']['properties']['long_context']['properties']['threshold_tokens']
        self.assertIn(
            "Long-context prices apply when the prompt's input tokens are strictly greater than threshold_tokens.",
            threshold.get('description', ''),
        )

    def test_vendor_ttls_and_storage_accept_null_and_zero(self):
        self.pricing.pop('cache_write_5m', None)
        self.pricing.pop('cache_write_1h', None)
        self.pricing['cache_writes'] = []
        standard, long_context = self.locations()
        standard['long_context'] = long_context
        for prices in (standard, long_context):
            prices.update(cache_writes=[{'ttl': '5m', 'price': 0},
                                       {'ttl': '1h', 'price': None},
                                       {'ttl': '30m', 'price': 0.5},
                                       {'ttl': '12h', 'price': 2}],
                          cache_storage_per_mtok_hour=0)
        for storage in (0, 0.25, None):
            standard['cache_storage_per_mtok_hour'] = storage
            long_context['cache_storage_per_mtok_hour'] = storage
            self.assertEqual(self.errors(), [])

    def test_old_cache_fields_rejected_at_both_price_levels(self):
        for key in ('cache_write_5m', 'cache_write_1h'):
            for long in (False, True):
                with self.subTest(key=key, long=long):
                    pricing = copy.deepcopy(self.pricing)
                    pricing['cache_writes'] = []
                    pricing.pop('cache_write_5m', None)
                    pricing.pop('cache_write_1h', None)
                    if long:
                        pricing['long_context'] = dict(threshold_tokens=100000,
                            input=1, output=2, cache_read=None, cache_writes=[], **{key: None})
                    else:
                        pricing[key] = None
                    self.data['models'][0]['pricing'] = pricing
                    at = '/models/0/pricing/' + ('long_context/' if long else '') + key
                    self.assertIn(at, [p for p, _ in self.errors()])

    def test_invalid_write_and_storage_shapes(self):
        cases = [([], 'cache_writes', None, '/cache_writes'),
                 ([], 'cache_writes', [{'ttl': '5m'}], '/cache_writes/0/price'),
                 ([], 'cache_writes', [{'ttl': '5m', 'price': -1}], '/cache_writes/0/price'),
                 ([], 'cache_writes', [{'ttl': '5m', 'price': True}], '/cache_writes/0/price'),
                 ([], 'cache_writes', [{'ttl': '5m', 'price': 1, 'extra': 0}], '/cache_writes/0/extra'),
                 ([], 'cache_writes', [{'ttl': f'{i}m', 'price': 1} for i in range(1, 8)], '/cache_writes'),
                 ([], 'cache_storage_per_mtok_hour', -1, '/cache_storage_per_mtok_hour'),
                 ([], 'cache_storage_per_mtok_hour', True, '/cache_storage_per_mtok_hour'),
                 ([], 'cache_storage_per_mtok_hour', '0', '/cache_storage_per_mtok_hour')]
        for ttl in ('0m', '01h', '10000m', '1d', '5M', ' 5m', '5m\n', '', 5):
            cases.append(([], 'cache_writes', [{'ttl': ttl, 'price': 1}], '/cache_writes/0/ttl'))
        for long in (False, True):
            for _, field, value, suffix in cases:
                with self.subTest(long=long, field=field, value=value):
                    self.data['models'][0]['pricing'] = copy.deepcopy(self.pricing)
                    target = self.data['models'][0]['pricing']
                    if long:
                        target['long_context'] = dict(threshold_tokens=100000, input=1,
                                                     output=2, cache_read=None, cache_writes=[])
                        target = target['long_context']
                    target[field] = value
                    prefix = '/models/0/pricing' + ('/long_context' if long else '')
                    self.assertIn(prefix + suffix, [p for p, _ in self.errors()])

    def test_ttl_uniqueness_even_when_prices_differ(self):
        for long in (False, True):
            self.data['models'][0]['pricing'] = copy.deepcopy(self.pricing)
            prices = self.data['models'][0]['pricing']
            if long:
                prices['long_context'] = dict(threshold_tokens=100000, input=1,
                                             output=2, cache_read=None, cache_writes=[])
                prices = prices['long_context']
            prices['cache_writes'] = [{'ttl': '5m', 'price': 1}, {'ttl': '5m', 'price': None}]
            prefix = '/models/0/pricing/' + ('long_context/' if long else '')
            self.assertIn(prefix + 'cache_writes/1/ttl', [p for p, _ in self.errors()])

    def test_missing_cache_writes_rejected_at_both_price_levels(self):
        self.pricing.pop('cache_writes', None)
        self.assertIn('/models/0/pricing/cache_writes', [p for p, _ in self.errors()])
        self.pricing['cache_writes'] = []
        self.pricing['long_context'] = dict(threshold_tokens=100000, input=1, output=2, cache_read=None)
        self.assertIn('/models/0/pricing/long_context/cache_writes', [p for p, _ in self.errors()])

    def test_malformed_cache_shapes_never_crash_semantics(self):
        for writes in (None, 1, [None, {}, {'ttl': []}, {'ttl': '5m'}, {'ttl': '5m'}]):
            self.pricing['cache_writes'] = writes
            self.pricing['long_context'] = {'cache_writes': writes}
            self.assertTrue(self.errors())


class ProtocolTests(unittest.TestCase):
    def test_provider_and_optional_harness_protocols_are_closed(self):
        for kind, filename in (('provider', 'providers/example-provider.json'),
                               ('harness', 'harnesses/example-cli.json')):
            schema = json.loads((REPO / f'schema/{kind}.schema.json').read_text())
            data = json.loads((REPO / 'tests/fixtures/valid' / filename).read_text())
            validator.check_schema(schema)
            data['protocols'] = ['gemini_generate', 'gemini_interactions']
            self.assertEqual(validator.schema_problems(data, schema), [])
            data['protocols'] = ['gemini_interactions', 'custom']
            self.assertIn('/protocols/1', [p for p, _ in validator.schema_problems(data, schema)])
            data['protocols'] = ['gemini_interactions', 'gemini_interactions']
            self.assertIn('/protocols/1', [p for p, _ in validator.schema_problems(data, schema)])
