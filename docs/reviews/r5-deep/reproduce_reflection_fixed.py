"""Focused invented-key probes beyond the shared-sentinel regressions; offline."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('r5_reflection_fixture', ROOT / 'tests/test_model_watch.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
keys = {v.env_key: 'invented-' + v.name + '-distinct-key' for v in fixture.mw.VENDORS if v.env_key}
env = {name: ' \t' + key + '\r\n' for name, key in keys.items()}
results = []
for v in fixture.mw.VENDORS:
    for malformed in (False, True):
        case = fixture.WatchCase(methodName='runTest')
        case.setUp()
        try:
            data = case.matching_routes()
            source_name = 'DEEPSEEK_MODELS_KEY' if v.name == 'openai' else 'OPENAI_MODELS_KEY'
            reflected = ('bad`' if malformed else 'wrapped-') + keys[source_name] + '-suffix'
            if v.name == 'gemini':
                entry = {'name': 'models/' + reflected, 'supportedGenerationMethods': ['generateContent']}
                data[v.list_url]['models'].append(entry)
            else:
                data[v.list_url]['data'].append({'id': ('openai/' if v.name == 'openrouter' else '') + reflected})
            code, out, err, opener = case.run_watch(env=env, responses=data)
            captured = case.captured(out, err)
            results.append({
                'response_vendor': v.name, 'reflected_key_source': source_name,
                'malformed_id': malformed, 'exit_error': code == 1,
                'safe_diagnostic': 'response reflects a credential' in err,
                'no_known_key_in_output_files': all(key not in captured for key in keys.values()),
                'no_known_key_in_urls': all(key not in url for key in keys.values() for url, _ in opener.calls),
                'no_pr_body': not (case.root / 'out/body.md').exists(),
                'no_candidates': not (case.root / 'candidates').exists(),
            })
        finally:
            case.doCleanups()
print(json.dumps(results, indent=2))
assert all(all(row[k] for k in ('exit_error', 'safe_diagnostic', 'no_known_key_in_output_files',
                              'no_known_key_in_urls', 'no_pr_body', 'no_candidates')) for row in results)
