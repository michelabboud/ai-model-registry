"""Run the actual PR-job shell blocks against disposable local Git repositories.

Adapted from michelabboud/genie-registry scripts/model_watch.py (Michel's own repository), 2026-11-15.
The extraction/test approach comes from its tests/test_workflow_steps.py.
All Git remotes are temporary filesystem paths; ``gh`` is a fixture executable.
No network, vendor credentials, repository commits, or hosted PRs are involved.
"""
from __future__ import annotations
# unittest initializes these per-test fixtures in setUp, before every test.
# pyright: reportUninitializedInstanceVariable=false

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
WORKFLOW = REPO / '.github/workflows/model-watch.yml'
BRANCH = 'model-watch/auto'
BOT_EMAIL = '41898282+github-actions[bot]@users.noreply.github.com'
KNOWN = ('openai', 'anthropic', 'gemini', 'xai', 'deepseek', 'openrouter')


def step_script(name: str) -> str:
    """Extract one named literal shell block without a YAML dependency."""
    lines = WORKFLOW.read_text(encoding='utf-8').splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == f'- name: {name}')
    run = next(i for i in range(start, len(lines)) if lines[i].strip() == 'run: |')
    indent = len(lines[run + 1]) - len(lines[run + 1].lstrip())
    body = []
    for line in lines[run + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) < indent:
            break
        body.append(line[indent:])
    return '\n'.join(body) + '\n'


class WorkflowShell(unittest.TestCase):
    def setUp(self):
        if not shutil.which('bash') or not shutil.which('git'):
            self.fail('bash and git are required to exercise the real workflow shell')
        self.temp = tempfile.TemporaryDirectory(prefix='model-watch-workflow-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.origin = self.root / 'origin.git'
        self.runner = self.root / 'runner'
        self.artifact = self.runner / 'watch-in'
        (self.artifact / 'candidates').mkdir(parents=True)
        (self.artifact / 'pr-body.md').write_text('Fixture body; all values TO VERIFY.\n')
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        gh = self.bin / 'gh'
        gh.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with open(os.environ['GHLOG'], 'a') as handle:
    handle.write(json.dumps(args) + '\\n')
if args[:2] == ['pr', 'list']:
    print(os.environ.get('FAKE_PR', ''), end='')
elif '--body-file' in args:
    source = Path(args[args.index('--body-file') + 1])
    Path(os.environ['BODY_CAPTURE']).write_bytes(source.read_bytes())
if args[:2] == ['pr', 'create'] and os.environ.get('REFUSE_CREATE') == '1':
    sys.exit(1)
''', encoding='utf-8')
        gh.chmod(0o755)
        self.env = {
            **os.environ,
            'PATH': str(self.bin) + os.pathsep + os.environ.get('PATH', ''),
            'GIT_CONFIG_GLOBAL': os.devnull,
            'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_TERMINAL_PROMPT': '0',
            'GIT_AUTHOR_NAME': 'fixture bot',
            'GIT_AUTHOR_EMAIL': BOT_EMAIL,
            'GIT_COMMITTER_NAME': 'fixture bot',
            'GIT_COMMITTER_EMAIL': BOT_EMAIL,
            'GHLOG': str(self.root / 'gh.jsonl'),
            'BODY_CAPTURE': str(self.root / 'body.md'),
            'RUNNER_TEMP': str(self.runner),
            'GITHUB_REPOSITORY': 'fixture/ai-model-registry',
            'GITHUB_OUTPUT': str(self.root / 'outputs'),
            'GITHUB_STEP_SUMMARY': str(self.root / 'summary.md'),
            'WATCH_BRANCH': BRANCH,
            'BOT_EMAIL': BOT_EMAIL,
            'SKIPPED': '',
            'FAKE_PR': '',
        }
        self.git('init', '--bare', '--initial-branch=main', str(self.origin), cwd=self.root)
        initial = self.root / 'initial'
        self.git('init', '--initial-branch=main', str(initial), cwd=self.root)
        (initial / '.gitignore').write_text('candidates/\n')
        (initial / 'models').mkdir()
        (initial / 'models/fixture.json').write_text('{"fixture": true}\n')
        self.git('add', '.', cwd=initial)
        self.git('commit', '-m', 'Clearly invented workflow fixture', cwd=initial)
        self.git('remote', 'add', 'origin', str(self.origin), cwd=initial)
        self.git('push', 'origin', 'main', cwd=initial)
        self.main = self.git('rev-parse', 'refs/heads/main', cwd=self.origin).stdout.strip()
        self.runs = 0

    def command(self, args, *, cwd, env=None, check=True):
        result = subprocess.run(args, cwd=cwd, env=self.env if env is None else env,
                                text=True, capture_output=True, timeout=30)
        if check and result.returncode:
            self.fail(f'{args}: {result.returncode}\n{result.stdout}\n{result.stderr}')
        return result

    def git(self, *args, cwd=None, **kwargs):
        return self.command(['git', *args], cwd=cwd or self.root, **kwargs)

    def fixture(self, **worksheets):
        directory = self.artifact / 'candidates'
        for path in directory.iterdir():
            path.unlink()  # files produced by this test alone
        for vendor, content in worksheets.items():
            (directory / f'{vendor}.md').write_text(content, encoding='utf-8')

    def begin(self, *, skipped='', pr=''):
        """A fresh checkout matches actions/checkout on a new hosted runner."""
        self.runs += 1
        work = self.root / f'run-{self.runs}'
        self.git('clone', '--branch', 'main', str(self.origin), str(work))
        env = {**self.env, 'SKIPPED': skipped, 'FAKE_PR': pr}
        Path(env['GITHUB_OUTPUT']).write_text('')
        result = self.shell('Find the watch branch and its pull request', work, env=env)
        outputs = dict(line.split('=', 1) for line in Path(env['GITHUB_OUTPUT']).read_text().splitlines())
        return work, {**env, 'SHA': outputs['sha'], 'PR': outputs['pr']}, outputs, result

    def shell(self, name, work, *, env=None, check=True):
        return self.command(['bash', '-c', step_script(name)], cwd=work,
                            env=self.env if env is None else env, check=check)

    def reconcile(self, *, skipped='', pr=''):
        work, env, outputs, _ = self.begin(skipped=skipped, pr=pr)
        if outputs['foreign'] == 'false':
            self.shell('Open or update the pull request', work, env=env)
        self.assertEqual(self.git('rev-parse', 'main', cwd=self.origin).stdout.strip(), self.main)
        return work, env, outputs

    def remote_file(self, vendor):
        return self.git('show', f'refs/heads/{BRANCH}:candidates/{vendor}.md',
                        cwd=self.origin, check=False)

    def remote_sha(self):
        result = self.git('rev-parse', '--verify', f'refs/heads/{BRANCH}', cwd=self.origin, check=False)
        return result.stdout.strip() if not result.returncode else ''

    def gh_calls(self):
        return [json.loads(line) for line in (self.root / 'gh.jsonl').read_text().splitlines()]

    def test_creation_admits_all_six_known_worksheets_and_no_unknown_paths(self):
        self.fixture(**{vendor: f'Invented {vendor}' for vendor in KNOWN}, evil='must not reach Git')
        (self.artifact / 'models').mkdir()
        (self.artifact / 'models/fixture.json').write_text('hostile artifact replacement')
        self.reconcile()
        for vendor in KNOWN:
            self.assertEqual(self.remote_file(vendor).stdout, f'Invented {vendor}')
        self.assertNotEqual(self.remote_file('evil').returncode, 0)
        paths = self.git('diff', '--name-only', 'main', BRANCH, cwd=self.origin).stdout.splitlines()
        self.assertEqual(set(paths), {f'candidates/{vendor}.md' for vendor in KNOWN})
        self.assertEqual(sum(call[:2] == ['pr', 'create'] for call in self.gh_calls()), 1)

    def test_identical_rerun_preserves_sha_and_edits_existing_pr(self):
        self.fixture(openai='v1')
        self.reconcile()
        before = self.remote_sha()
        self.reconcile(pr='7')
        self.assertEqual(self.remote_sha(), before)
        self.assertTrue(any(call[:3] == ['pr', 'edit', '7'] for call in self.gh_calls()))
        self.assertEqual(sum(call[:2] == ['pr', 'create'] for call in self.gh_calls()), 1)

    def test_changed_worksheet_updates_same_branch_and_existing_pr(self):
        self.fixture(openai='v1')
        self.reconcile()
        before = self.remote_sha()
        self.fixture(openai='v2')
        self.reconcile(pr='7')
        self.assertNotEqual(self.remote_sha(), before)
        self.assertEqual(self.remote_file('openai').stdout, 'v2')
        self.assertTrue(any(call[:3] == ['pr', 'edit', '7'] for call in self.gh_calls()))

    def test_skipped_vendor_is_carried_forward_and_marked_stale(self):
        self.fixture(openai='old', xai='previous xai')
        self.reconcile()
        self.fixture(openai='fresh')
        self.reconcile(skipped='xai', pr='7')
        self.assertEqual(self.remote_file('xai').stdout, 'previous xai')
        self.assertEqual(self.remote_file('openai').stdout, 'fresh')
        self.assertIn('Carried forward, may be stale', (self.root / 'body.md').read_text())

    def test_skipped_vendor_carried_with_no_fresh_changes_and_resolved_sheet_removed(self):
        self.fixture(openai='resolved next run', xai='retain')
        self.reconcile()
        self.fixture()
        self.reconcile(skipped='xai', pr='7')
        self.assertEqual(self.remote_file('xai').stdout, 'retain')
        self.assertNotEqual(self.remote_file('openai').returncode, 0)
        self.assertIn('may be stale', (self.root / 'body.md').read_text())

    def test_no_worksheets_does_not_open_empty_pr(self):
        self.fixture()
        self.reconcile(skipped='openai')
        self.assertEqual(self.remote_sha(), '')
        self.assertFalse(any(call[:2] == ['pr', 'create'] for call in self.gh_calls()))

    def test_partial_empty_run_prunes_resolved_last_sheet_and_updates_existing_pr(self):
        self.fixture(openai='resolved on the next run')
        self.reconcile()
        self.fixture()
        current_report = 'Current incomplete report: xAI skipped; no worksheets remain.\n'
        (self.artifact / 'pr-body.md').write_text(current_report)
        self.reconcile(skipped='xai', pr='7')
        # A unique reconciliation commit keeps the branch above main; resetting
        # to main could let the host close an incomplete watch PR implicitly.
        self.assertNotEqual(self.remote_sha(), self.main)
        parent = self.git('rev-parse', f'{BRANCH}^', cwd=self.origin).stdout.strip()
        self.assertEqual(parent, self.main)
        self.assertEqual(self.git('diff', '--name-only', 'main', BRANCH,
                                  cwd=self.origin).stdout, '')
        self.assertNotEqual(self.remote_file('openai').returncode, 0)
        self.assertEqual((self.root / 'body.md').read_text(), current_report)
        self.assertTrue(any(call[:3] == ['pr', 'edit', '7'] for call in self.gh_calls()))
        self.assertFalse(any(call[:2] == ['pr', 'close'] for call in self.gh_calls()))
        self.assertEqual(sum(call[:2] == ['pr', 'create'] for call in self.gh_calls()), 1)

    def test_partial_empty_run_refreshes_pr_when_existing_branch_already_matches_main(self):
        # An earlier partial run has already pruned the last worksheet.
        self.fixture(openai='resolved on the next run')
        self.reconcile()
        self.fixture()
        self.reconcile(skipped='xai', pr='7')
        before = self.remote_sha()
        current_report = 'Updated incomplete report: xAI is still skipped.\n'
        (self.artifact / 'pr-body.md').write_text(current_report)
        self.reconcile(skipped='xai', pr='7')
        self.assertEqual(self.remote_sha(), before)
        self.assertEqual(sum(call[:3] == ['pr', 'edit', '7'] for call in self.gh_calls()), 2)
        self.assertEqual((self.root / 'body.md').read_text(), current_report)
        self.assertFalse(any(call[:2] == ['pr', 'close'] for call in self.gh_calls()))
        self.assertEqual(sum(call[:2] == ['pr', 'create'] for call in self.gh_calls()), 1)

    def test_partial_empty_run_lease_refuses_race_without_pr_update(self):
        self.fixture(openai='resolved on the next run')
        self.reconcile()
        self.fixture()
        work, env, _, _ = self.begin(skipped='xai', pr='7')
        other = self.root / 'empty-racer'
        self.git('clone', '--branch', BRANCH, str(self.origin), str(other))
        (other / 'candidates/gemini.md').write_text('racing update')
        self.git('add', '-f', 'candidates/gemini.md', cwd=other)
        self.git('commit', '-m', 'invented racing bot', cwd=other)
        self.git('push', 'origin', BRANCH, cwd=other)
        moved = self.remote_sha()
        result = self.shell('Open or update the pull request', work, env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.remote_sha(), moved)
        self.assertRegex(result.stderr, 'stale info|rejected')
        self.assertFalse(any(call[:2] in (['pr', 'edit'], ['pr', 'close'])
                             for call in self.gh_calls()))

    def test_complete_empty_run_closes_existing_pr_and_keeps_branch(self):
        self.fixture(openai='v1')
        self.reconcile()
        before = self.remote_sha()
        self.fixture()
        work, env, _ = self.reconcile(pr='7')
        self.shell('Close a pull request that no longer applies', work, env=env)
        self.assertEqual(self.remote_sha(), before)
        self.assertTrue(any(call[:3] == ['pr', 'close', '7'] for call in self.gh_calls()))

    def test_lease_refuses_racing_update_without_overwriting_it(self):
        self.fixture(openai='v1')
        self.reconcile()
        self.fixture(openai='v2')
        work, env, _, _ = self.begin(pr='7')
        other = self.root / 'racer'
        self.git('clone', '--branch', BRANCH, str(self.origin), str(other))
        (other / 'candidates/gemini.md').write_text('racing update')
        self.git('add', '-f', 'candidates/gemini.md', cwd=other)
        self.git('commit', '-m', 'invented racing bot', cwd=other)
        self.git('push', 'origin', BRANCH, cwd=other)
        moved = self.remote_sha()
        result = self.shell('Open or update the pull request', work, env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.remote_sha(), moved)
        self.assertRegex(result.stderr, 'stale info|rejected')

    def test_human_commit_is_detected_and_neither_updated_nor_closed(self):
        self.fixture(openai='v1')
        self.reconcile()
        human = self.root / 'human'
        self.git('clone', '--branch', BRANCH, str(self.origin), str(human))
        (human / 'candidates/openai.md').write_text('human edit')
        self.git('add', '-f', 'candidates/openai.md', cwd=human)
        human_env = {**self.env, 'GIT_AUTHOR_EMAIL': 'human@example.invalid',
                     'GIT_COMMITTER_EMAIL': 'human@example.invalid'}
        self.git('commit', '-m', 'invented human edit', cwd=human, env=human_env)
        self.git('push', 'origin', BRANCH, cwd=human)
        before = self.remote_sha()
        _, _, outputs = self.reconcile(pr='7')
        self.assertEqual(outputs['foreign'], 'true')
        self.assertEqual(self.remote_sha(), before)
        self.assertFalse(any(call[:2] in (['pr', 'edit'], ['pr', 'close']) for call in self.gh_calls()))

    def test_ls_remote_failure_is_an_error_and_no_write_occurs(self):
        work, env, _, _ = self.begin()
        self.git('remote', 'set-url', 'origin', str(self.root / 'absent.git'), cwd=work)
        result = self.shell('Find the watch branch and its pull request', work, env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ls-remote failed', result.stdout)
        self.assertEqual(self.remote_sha(), '')

    def test_worksheet_and_artifact_parent_symlinks_are_refused(self):
        self.fixture(openai='safe')
        outside = self.root / 'outside'
        outside.write_text('must never be copied')
        (self.artifact / 'candidates/xai.md').symlink_to(outside)
        work, env, _, _ = self.begin()
        result = self.shell('Open or update the pull request', work, env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.remote_sha(), '')
        (self.artifact / 'candidates/xai.md').unlink()
        (self.artifact / 'candidates').rename(self.root / 'real-candidates')
        (self.artifact / 'candidates').symlink_to(self.root / 'real-candidates', target_is_directory=True)
        result = self.shell('Open or update the pull request', work, env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.remote_sha(), '')

    def test_body_and_artifact_root_symlinks_are_refused(self):
        self.fixture(openai='safe')
        (self.artifact / 'pr-body.md').rename(self.root / 'real-body.md')
        (self.artifact / 'pr-body.md').symlink_to(self.root / 'real-body.md')
        work, env, _, _ = self.begin()
        result = self.shell('Open or update the pull request', work, env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.remote_sha(), '')
        (self.artifact / 'pr-body.md').unlink()
        (self.artifact / 'pr-body.md').write_text('body')
        self.artifact.rename(self.root / 'real-artifact')
        self.artifact.symlink_to(self.root / 'real-artifact', target_is_directory=True)
        result = self.shell('Open or update the pull request', work, env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.remote_sha(), '')

    def test_unknown_skipped_vendor_is_refused(self):
        self.fixture(openai='safe')
        work, env, _, _ = self.begin(skipped='../models')
        result = self.shell('Open or update the pull request', work, env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unexpected skipped vendor', result.stdout)
        self.assertEqual(self.remote_sha(), '')

    def test_pr_creation_refusal_names_setting_after_branch_push(self):
        self.fixture(openai='safe')
        work, env, _, _ = self.begin()
        result = self.shell('Open or update the pull request', work,
                            env={**env, 'REFUSE_CREATE': '1'}, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.remote_sha())
        self.assertIn('Allow GitHub Actions to create and approve pull requests', result.stdout)


class WorkflowBoundary(unittest.TestCase):
    def test_write_job_has_no_keys_or_vendor_code_and_no_untrusted_trigger(self):
        workflow = WORKFLOW.read_text(encoding='utf-8')
        watch, write = workflow.split('\n  pull-request:\n', 1)
        self.assertNotIn('pull_request:', workflow)
        self.assertNotIn('pull_request_target:', workflow)
        self.assertIn('permissions: {}', watch)
        self.assertIn('contents: read', watch)
        self.assertNotIn('contents: write', watch)
        self.assertIn('contents: write', write)
        self.assertIn('pull-requests: write', write)
        self.assertNotIn('secrets.', write)
        self.assertNotIn('MODELS_KEY', write)
        self.assertNotIn('scripts/model_watch.py', write)
        # The no-fresh-change path must still reconcile skipped worksheets.
        self.assertIn("needs.watch.outputs.result == 'none'", write)
        close = write.split('- name: Close a pull request that no longer applies', 1)[1]
        self.assertIn("needs.watch.outputs.complete == 'true'", close)
        self.assertIn("steps.branch.outputs.foreign == 'false'", close)


if __name__ == '__main__':
    unittest.main()
