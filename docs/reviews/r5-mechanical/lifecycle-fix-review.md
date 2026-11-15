# R5 mechanical focused repair review — partial empty reconciliation

CONFIRMED: initial finding M2 is fixed on the pinned workflow/test bytes below; no new blocker found in this focused repair boundary.

REFUTED: the original partial-empty reproduction no longer leaves the resolved checked-vendor worksheet or stale PR body published.

UNVERIFIED: hosted GitHub behavior remains outside the no-network review. Local Git/CLI fixtures do not establish hosted PR or token acceptance. Credential reflection is covered separately by `fix-review.md`.

Date: 2026-11-15. Dev mode: `mvp`. Base remains `8a2a00c434aba3885bb4195699e5621da20d694c`; candidate is frozen working bytes. Initial M2 findings and `partial-empty-check.json` remain preserved.

| Input | SHA-256 |
| --- | --- |
| `.github/workflows/model-watch.yml` | `a7ff8878a01c91a5e879e44a824d3a9ba5483e443d4a44bef80d729fd749f2e4` |
| `tests/test_model_watch_workflow.py` | `3da76f1fc53e75a559260241900b08c18f97be9b6c478bb9390c1a9164d5e63f` |

## Source assessment

The existing-branch partial-empty path at workflow line 207 now compares the desired candidate index with the observed branch. A changed candidate tree receives an empty reconciliation commit above `main` and a push protected by the observed SHA lease. The old resolved worksheet is absent from that tree; no extra filename or fabricated vendor proposal is introduced. The path updates an existing PR body even when the desired tree already matches, without creating another commit, branch, or PR. A failing lease aborts before PR editing.

The path requires both skipped vendors and an existing branch. Keyless first runs with no prior worksheets retain the existing no-empty-branch/PR behavior. Skipped vendors with previous worksheets still use the existing byte-preserving carry-forward path; the empty reconciliation case is reached only when no admitted or carried worksheet remains. The complete-only close condition and foreign-author exclusion remain unchanged.

## Independently executed focused checks

Command:

```sh
PYTHONPATH=tests python3 -m unittest -v \
  test_model_watch_workflow.WorkflowShell.test_partial_empty_run_prunes_resolved_last_sheet_and_updates_existing_pr \
  test_model_watch_workflow.WorkflowShell.test_partial_empty_run_refreshes_pr_when_existing_branch_already_matches_main \
  test_model_watch_workflow.WorkflowShell.test_partial_empty_run_lease_refuses_race_without_pr_update
```

Result: exit 0; **3 tests in 2.233s; OK**. These execute the actual workflow shell against disposable local filesystem Git remotes and a stub `gh`. They verify final-sheet removal, a unique head whose parent is `main`, zero tree diff against `main`, existing-PR edit without create/close, unchanged repeat SHA/body refresh, and lease rejection without PR editing after a racing update.

The original M2 sequence was also replayed with the existing fixture harness: publish only an OpenAI worksheet, then clear fresh worksheets and run with xAI skipped and existing PR 7, then repeat. `lifecycle-fix-check.json` records branch changed, resolved OpenAI removed, no unknown worksheet added, one commit ahead of `main`, existing PR updated, no close call, and unchanged SHA on the repeat. All assertions passed.

## Shared gate and evidence limits

The final root receipt at `.research/r5-validation-final-xx35nmjd/receipt.json` pins these same workflow/tests and the previously reviewed credential-repair hashes. It records exit 0 for validator, full unittest discovery, CLI help, whitespace check, and the data/schema/harness/version/license preservation check. The coordinator reports **31 files / 0 problems** and **141 tests in 19.006s; OK**. This is shared broad-gate evidence, not another independent full-suite execution by this lane.

Same-family fresh-context reviewer, shared filesystem, stable source during this focused review. No sibling review outputs read, network, real credentials, source edits, installation, repository Git writes, or subagents. Git operations occurred only inside disposable test fixtures. Hosted automatic PR behavior with the empty reconciliation commit still requires the separately acknowledged hosted acceptance boundary; the local tests establish the generated branch/history and emitted CLI calls.
