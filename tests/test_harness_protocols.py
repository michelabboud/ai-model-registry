"""Harness ingress contract tests; all integration values are invented."""
import copy
import importlib.util
import json
from datetime import date
from pathlib import Path
from typing import Any
import unittest


REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('harness_validator', REPO / 'scripts/validate.py')
assert spec is not None and spec.loader is not None
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class HarnessProtocolTests(unittest.TestCase):
    schema: dict[str, Any] = {}
    data: dict[str, Any] = {}

    def setUp(self):
        self.schema = json.loads((REPO / 'schema/harness.schema.json').read_text())
        self.data = json.loads((REPO / 'tests/fixtures/valid/harnesses/example-cli.json').read_text())
        self.data['protocols'] = ['openai_chat']

    def structural_errors(self):
        validator.check_schema(self.schema)
        return validator.schema_problems(self.data, self.schema)

    def semantic_errors(self):
        return validator.semantic_problems(self.data, 'harness', 'example-cli', set(),
                                           date(2026, 11, 14))

    def test_protocols_are_required(self):
        del self.data['protocols']
        self.assertIn('/protocols', [at for at, _ in self.structural_errors()])

    def test_detect_only_accepts_empty_protocols(self):
        self.data.update(adapter='detect_only', protocols=[])
        self.assertEqual(self.structural_errors() + self.semantic_errors(), [])

    def test_every_integration_adapter_rejects_empty_protocols_semantically(self):
        for adapter in ('claude_env', 'codex_config', 'opencode_v1', 'opencode_v2',
                        'env_generic', 'config_snippet'):
            with self.subTest(adapter=adapter):
                self.data.update(adapter=adapter, protocols=[])
                self.assertIn('/protocols', [at for at, _ in self.semantic_errors()])

    def test_detect_only_rejects_nonempty_protocols_semantically(self):
        for protocol in ('anthropic_messages', 'openai_chat', 'openai_responses',
                         'gemini_generate', 'gemini_interactions'):
            with self.subTest(protocol=protocol):
                self.data.update(adapter='detect_only', protocols=[protocol])
                self.assertIn('/protocols', [at for at, _ in self.semantic_errors()])

    def test_integrations_accept_each_protocol_and_four_distinct_protocols(self):
        protocols = ['anthropic_messages', 'openai_chat', 'openai_responses',
                     'gemini_generate', 'gemini_interactions']
        for selected in [[protocol] for protocol in protocols] + [protocols[:4]]:
            with self.subTest(protocols=selected):
                self.data['protocols'] = selected
                self.assertEqual(self.structural_errors() + self.semantic_errors(), [])

    def test_wrong_types_duplicates_unknown_and_provider_only_protocols_rejected(self):
        for value, at in ((None, '/protocols'), ('openai_chat', '/protocols'),
                          ([None], '/protocols/0'), (['custom'], '/protocols/0'),
                          (['openai_chat', 'openai_chat'], '/protocols/1'),
                          (['bedrock_converse'], '/protocols/0'),
                          (['vertex_anthropic'], '/protocols/0'),
                          (['vertex_gemini'], '/protocols/0'),
                          (['anthropic_messages', 'openai_chat', 'openai_responses',
                            'gemini_generate', 'gemini_interactions'], '/protocols')):
            with self.subTest(protocols=value):
                self.data['protocols'] = value
                self.assertIn(at, [location for location, _ in self.structural_errors()])

    def test_malformed_protocols_do_not_crash_semantics(self):
        for value in (None, 0, {}, 'openai_chat', [None]):
            with self.subTest(protocols=value):
                self.data['protocols'] = value
                self.semantic_errors()
                self.assertTrue(self.structural_errors())

    def test_provider_protocol_contract_is_unchanged(self):
        schema = json.loads((REPO / 'schema/provider.schema.json').read_text())
        data = json.loads((REPO / 'tests/fixtures/valid/providers/example-provider.json').read_text())
        data['protocols'] = ['bedrock_converse', 'vertex_anthropic', 'vertex_gemini',
                             'anthropic_messages', 'openai_chat', 'openai_responses',
                             'gemini_generate', 'gemini_interactions']
        self.assertEqual(validator.schema_problems(data, schema), [])
        missing = copy.deepcopy(data)
        missing['protocols'] = []
        self.assertIn('/protocols', [at for at, _ in validator.schema_problems(missing, schema)])
