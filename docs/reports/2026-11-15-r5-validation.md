# R5 offline validation — 2026-11-15

Dev mode: mvp. Base commit: `8a2a00c434aba3885bb4195699e5621da20d694c`.
Repository version remains `0.3.0`; no commit, tag, push, network request,
signature, or release is authorized in this lane.

## Initial integrated candidate

Validation owner: R5 lane `0469cbdc-d922-469a-81d5-95b5780ae812`.
Python: 3.12.3; implementation contract: Python 3.11+ standard library only.
Receipt time: 2026-11-15T01:08:57.167262+00:00.

| Changed boundary | Check | Result |
| --- | --- | --- |
| Registry records and validation remain intact | `python3 scripts/validate.py` | Exit 0; **31 files checked; 0 problems; clean** |
| Vendor parsing, hostile inputs, proposals, workflow lifecycle, prior contracts | `python3 -m unittest discover -s tests` | Exit 0; **136 tests in 19.480s; OK** (89 prior, 32 watcher, 15 workflow) |
| CLI help without network or credentials | `python3 scripts/model_watch.py --help` | Exit 0; documented options printed |
| Tracked patch whitespace | `git diff --check` | Exit 0; no diagnostics |
| Data and version preservation | `git diff --name-only -- providers models schema harnesses VERSION LICENSE` | Exit 0; empty output |

Focused runs before integration: watcher 32 tests in 0.241s, OK; workflow
worker 15 tests in 8.664s, OK. The test-first watcher run initially failed to
import the not-yet-created `scripts/model_watch.py`; the implementation then
satisfied those tests. An earlier discovery before the test file existed ran
zero tests (exit 5); neither initial result is a passing acceptance receipt.

Raw successful command stdout/stderr and machine-readable SHA256 receipt remain
under `.research/r5-validation-hcetow5k/` (ignored, retained locally). The exact
reviewed primary inputs were:

| Path | SHA256 |
| --- | --- |
| `scripts/model_watch.py` | `bd2bdeb3edd75bd1221c976b696d1af5b83491d34ad5375559e6781ac7611ac7` |
| `.github/workflows/model-watch.yml` | `d9329b572254fc0cfd595497c7a01c9f46db310b7d2f829331315e5ed16d1846` |
| `tests/test_model_watch.py` | `2963d58f32420fa84553bd23210da587053a24b89f16c9d7e9e7e8fcabaa2730` |
| `tests/test_model_watch_workflow.py` | `325c14c978ee94ca9d6c05352876d833439c48f0859bef07248f44fe2e8f016a` |

## Evidence limits

All vendor responses and keys in tests are invented. urllib is mocked; Git
workflow tests use only disposable local filesystem remotes and a stub `gh`.
These checks prove offline behavior, not hosted GitHub workflow settings, token
acceptance, vendor permissions, or live endpoint compatibility. Anthropic,
DeepSeek, and xAI shapes remain **UNVERIFIED** until the coordinator's live run.
No signing key is read or installed. Z.ai, Vertex, and Bedrock are unwatched.

Independent mechanical/deep reviews are in progress on these frozen input
hashes. Their final findings and any subsequent repaired-candidate receipts
will be recorded below; this initial green run does not pre-accept repairs.

## Repaired candidate — final local acceptance

Both defects were reproduced before repair. The credential regression recorded
8 failing subcases; its repaired focused watcher suite passed 34 tests in
0.326s. Three lifecycle regressions failed before repair (initial and refined
expectation runs retained); the repaired workflow suite passed 18 tests in
9.460s. Raw red/green files remain under `.research/r5-reflection-3m5z8olg/`
and `.research/r5-workflow-partial-empty-20261115T0117Z/`.

The final full commands on the repaired candidate all exited 0:

- `python3 scripts/validate.py`: **31 files checked; 0 problems; clean**.
- `python3 -m unittest discover -s tests`: **141 tests in 19.006s; OK**.
- `python3 scripts/model_watch.py --help`: documented options printed.
- `git diff --check`: no diagnostics.
- Protected data/schema/harness/version/license diff: empty.

Python 3.11 syntax parsing also passed for the new Python modules; execution
used Python 3.12.3, not an actual Python 3.11 runtime. Raw final gate outputs and
receipt are under `.research/r5-validation-final-xx35nmjd/`.

| Final primary input | SHA256 |
| --- | --- |
| `scripts/model_watch.py` | `6cb77ceb5a319ebe2014d81c5928b00f522876f8ff2822438e48a84e654d6d92` |
| `.github/workflows/model-watch.yml` | `a7ff8878a01c91a5e879e44a824d3a9ba5483e443d4a44bef80d729fd749f2e4` |
| `tests/test_model_watch.py` | `7e4f24aee532a9caff7203d320d63c1308e8a8fa42584a1c06d4440384b5d16f` |
| `tests/test_model_watch_workflow.py` | `3da76f1fc53e75a559260241900b08c18f97be9b6c478bb9390c1a9164d5e63f` |

### Review ruling

- Mechanical: credential reflection and incomplete-empty lifecycle were both
  independently reproduced; both fixes accepted by focused re-review.
- Deep: lifecycle independently reproduced; both final fixes accepted by focused
  re-review. Its original credential-safety refutation was incorrect and is
  explicitly superseded in its fix review. The initial report remains intact.
- Mechanical independently ran 2 reflection tests (0.039s), a six-vendor/direct
  cursor matrix, 3 lifecycle tests (2.233s), and the saved lifecycle reproduction.
  Deep independently ran 8 regression/neighbor tests (3.501s) and 12 distinct-key
  reflection probes. No additional blocker remained in those reviewed boundaries.

See [initial mechanical findings](../reviews/r5-mechanical/findings.md),
[credential repair](../reviews/r5-mechanical/fix-review.md),
[lifecycle repair](../reviews/r5-mechanical/lifecycle-fix-review.md),
[initial deep findings](../reviews/r5-deep/findings.md), and
[deep repair review](../reviews/r5-deep/fix-review.md).

Requested configurations: two implementation workers inherited the lane's
`gpt-6.1-sol` dispatch (effort unmeasured); mechanical review `gpt-6.1-sol/high`,
deep review `gpt-6.1-sol/xhigh`. Reviewers used fresh contexts, no parent
conversation history, a shared filesystem, and one model family. Actual provider
runtime identity, token usage, queue time, and precise review latency are
unavailable. Shared broad receipts are provenance, not independent execution.
This lane reviewed one R5 batch and admitted no subsequent task or batch.

### Decisions, concerns, and close-out

Use JSON/text worksheets with explicit placeholders rather than borrowing sibling
values; allow the schema-compatible safe routed ID grammar; retain all candidates
within cumulative listing limits; force-add only known ignored worksheets; refuse
credential reflection and artifact links; reconcile partial runs, including one
bounded empty commit only when clearing an existing branch's last worksheet.
These narrow or preserve Genie's authority boundary. No Python dependency added.

Remaining UNVERIFIED: Anthropic/DeepSeek/xAI live shapes, current fine-grained
vendor key restrictions, hosted permissions/actions/PR behavior (including an
empty-diff PR). They are explicit first-live-run boundaries, not passing offline
claims. Z.ai/Vertex/Bedrock stay unwatched with separate backlog entries. R4
waits on Michel's signing key. Source checkpointing belongs to the coordinator.

Docs, ADR, progress, plan, handoff, and backlog are updated. `VERSION` remains
0.3.0. Repository commits, tags, pushes, signing, release, deployment, and network
access were not performed, as explicitly required for this lane.

### Retention and hygiene

No worktree, server, container, or long-running service was created. Disposable
Git/registry fixtures were removed by their test harnesses; reclaimed fixture
bytes were not measured. No manual deletion or quarantine ran (0 bytes claimed
reclaimed). The pre-existing mixed Python cache directories were retained;
exclusive ownership/idleness outside the lane cannot be established here.

The R5 owner retains raw successful/failed receipts and review reproductions for
the coordinator's acceptance and first live run. `du -sh` measured a snapshot of
76 KiB across the four `.research/r5-*` evidence directories and 92 KiB in both
review directories before final close-out metadata. These are allocated-size
snapshots, not reclaimed space. The source fixtures and executable reproductions
remain in the repository; regeneration commands are the recorded tests/probes.
No large working-data tree remains. Next review event: coordinator acceptance
and first live vendor/workflow run; evidence is not authorized for deletion.
