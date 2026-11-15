"""Offline local-Git reproduction; no source changes or hosted/network calls."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('r5_workflow_fixture', ROOT / 'tests/test_model_watch_workflow.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
case = module.WorkflowShell(methodName='runTest')
case.setUp()
try:
    case.fixture(openai='Resolved OpenAI worksheet from the earlier run')
    case.reconcile()
    before_sha = case.remote_sha()
    before_calls = len(case.gh_calls())
    case.fixture()
    work, env, outputs, _ = case.begin(skipped='xai', pr='7')
    result = case.shell('Open or update the pull request', work, env=env)
    captured = {
        'scenario': 'OpenAI resolved; xAI skipped with no previous worksheet; no fresh worksheets',
        'workflow_result': 'none', 'workflow_complete': 'false',
        'shell_returncode': result.returncode,
        'shell_stdout': result.stdout,
        'shell_stderr': result.stderr,
        'before_branch_sha': before_sha,
        'after_branch_sha': case.remote_sha(),
        'retained_openai_worksheet': case.remote_file('openai').stdout,
        'new_gh_calls': case.gh_calls()[before_calls:],
        'close_step_condition': False,
        'root_repository_mutated': False,
    }
    print(json.dumps(captured, indent=2))
finally:
    case.doCleanups()
