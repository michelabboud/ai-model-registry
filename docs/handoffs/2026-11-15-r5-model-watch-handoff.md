# R5 model-watch handoff — 2026-11-15

Dev mode: mvp. Starting repository version: `0.3.0`.
Lane: `0469cbdc-d922-469a-81d5-95b5780ae812`.

## Current state

R5 is complete locally: validator clean (31 files, 0 problems), 141 tests pass,
CLI help passes, and both reproduced review defects have accepted focused
mechanical/deep re-reviews. Version remains 0.3.0. R4 is waiting on Michel's
signing key. No release exists yet.

The lane performs no network access, commit, tag, push, version bump, signing,
or release. The external coordinator retains final source acceptance, checkpointing, and
the first live endpoint compatibility run. Local fresh-context reviews are
recorded below; they do not establish hosted/runtime acceptance.

## Deliverable and ownership

- R5 owner: Python 3.11+ standard-library `scripts/model_watch.py`, clearly
  invented per-vendor fixtures, transport/selection/worksheet tests, and integrated
  acceptance commands.
- Workflow worker: `.github/workflows/model-watch.yml` and local workflow tests
  against disposable Git repositories and a stub GitHub CLI.
- Documentation worker: `docs/model-watch.md`, ADR 0005/index, `.env.example`,
  README, architecture, changelog, plan, progress, backlog, and this handoff.

The adaptation source is Michel's own `/home/michel/projects/genie-registry`,
read-only, inspected at `6411967e0a8f8da5ceed77f9c77e6d37f60292fe`.
Genie code reused in the script/workflow/tests carries the requested dated
adaptation header. This source reference is provenance, not independent review.

## Scope and retained safeguards

Watched providers are OpenAI, Anthropic, Gemini, xAI, DeepSeek, and public
OpenRouter. New eligible IDs and missing `ga`/`preview` IDs generate only
`candidates/<provider>.md`. Every proposed field is `TO VERIFY` and references
the provider's official documentation URL and sources already in its model
records. A missing model is a prompt to investigate, not proof of retirement.

The watch job has read-only repository access and vendor keys; the PR job has
write access but no vendor keys or vendor-facing code. It admits only six known
worksheet filenames. The watch never edits `providers/` or `models/`, signs,
releases, or pushes `main`. The signing key never enters CI.

One branch, `model-watch/auto`, and one PR are updated with a lease-protected
push. Human branch commits are preserved. Skipped vendors retain prior
worksheets with a possibly-stale note; successful partial runs also handle the
no-fresh-change case. PR closure requires a complete no-difference result.

Credentials stay only in headers, never in artifacts or output. Surrounding
whitespace is stripped; invalid visible-ASCII checks name only the secret.
Redirects are refused. Known key values reflected into IDs/cursors fail safely
before artifact or query construction. Hostile IDs are dropped and counted
without echoing them.
Each vendor listing is bounded to 4 MiB cumulatively, 2,000 entries, and 10 pages;
an unexpected response shape or limit violation fails the vendor and the run.

## Verification matrix

| Command / scope | Result |
| --- | --- |
| `python3 scripts/validate.py` | Exit 0; 31 files checked, 0 problems, clean |
| `python3 -m unittest discover -s tests` | Exit 0; 141 tests in 19.006s, OK (89 prior + 34 watcher + 18 workflow) |
| `python3 scripts/model_watch.py --help` | Exit 0; documented options printed without network |
| `git status --short` | R5-only tooling/docs/tests modifications; final inspection retained with the receipt |
| Hosted Actions execution and real vendor listing | Not run: offline task boundary |
| Local mechanical/deep repair review | Both findings fixed; focused re-reviews accepted |
| External coordinator source acceptance / checkpoint | Separate, pending |

Fixture tests do not prove live API compatibility. Local Git/GitHub-CLI-stub
tests do not prove hosted token settings or PR creation are enabled.

## UNVERIFIED and out-of-scope items

Anthropic, DeepSeek, and xAI endpoint response shapes remain **UNVERIFIED** until
the coordinator's first successful live run. A failed live run must retain the
label and failure evidence. Fine-grained list-only key restrictions beyond the
documented OpenAI setup are not established by this offline lane; the guide
distinguishes endpoint restriction from a low spending cap or API-service scope.

Z.ai, Vertex, and Bedrock are unwatched: no documented key-scoped list endpoint
verified for this task was supplied. Each has a separate backlog line. R4 waits
on Michel's signing key; R5 supplies no release or signature acceptance.

The existing shared dashboard is
`/home/michel/.local/state/build-task-dashboard/tasks.html`. Its state directory
is outside this lane's writable roots, so no dashboard publication is attempted
and no substitute state directory is invented. Lane/model attribution is the
dispatch envelope's `gpt-6.1-sol`; provider runtime identity and actual reasoning
effort are not measured by that envelope.

## Differences from Genie

- JSON text-model collections replace image TOML records; six vendors and the
  specified text-family, Gemini-method, and OpenRouter-prefix filters apply.
- IDs use the schema-v1 vocabulary and 128-character limit with `..` forbidden;
  direct vendors forbid slashes and OpenRouter requires exactly one. This
  admits the registry's routed IDs while keeping hostile Markdown/path input out.
- All admitted candidates are retained within listing bounds; Genie's
  image-specific candidate cap and sibling-value seeding do not apply.
- Byte limits are cumulative per vendor across pages, rather than permitting
  the per-response bound to multiply with pagination.
- Successful partial runs retain skipped worksheets even without fresh changes,
  and remove worksheets resolved by checked vendors. Candidates remain ignored
  on `main`, so the PR job explicitly force-adds only named worksheet files.
  Clearing the final worksheet during an incomplete run uses one empty
  reconciliation commit on the existing branch and refreshes the existing PR;
  identical repeats add no commit, and no empty branch or PR is created.
- Valid-looking credential reflection is explicitly rejected before IDs are
  rendered or cursors become URLs, closing a gap reproduced in review.

These adaptations preserve or narrow the original authority boundary. The guide
and [ADR 0005](../adr/0005-model-watch.md) describe their reasons.

## Coordinator's next action

Review the final offline evidence and candidate, then perform the first live
model-list run with approved restricted secrets. Keep the response-shape labels
until each affected vendor succeeds. Handle the source checkpoint separately;
this lane is explicitly uncommitted and unpublished.

## Exact evidence and review disposition

The [validation report](../reports/2026-11-15-r5-validation.md) pins the initial
and repaired source hashes and preserves failing as well as passing receipts.
Raw initial/final gates: `.research/r5-validation-hcetow5k/` and
`.research/r5-validation-final-xx35nmjd/`. Reflection red/green:
`.research/r5-reflection-3m5z8olg/`; lifecycle red/green:
`.research/r5-workflow-partial-empty-20261115T0117Z/`.

Mechanical review requested `gpt-6.1-sol` at `high`; deep review requested the
same model at `xhigh`. Both used fresh contexts without the parent conversation,
shared this filesystem, and belong to the same model family. Runtime identity,
token usage, and queue latency are unavailable. Initial notes and reproductions
remain under `docs/reviews/r5-mechanical/` and `docs/reviews/r5-deep/`; the deep
fix review explicitly corrects its initial overbroad credential-safety claim.
Both final findings were accepted by focused re-review on the final hashes.
The broad 141-test receipt is one root execution, not independent repetitions.

Hosted GitHub behavior of a zero-file-difference PR is UNVERIFIED. A unique
reconciliation commit avoids resetting its head to exactly main; the offline
fixture proves only local branch/commit/PR-command behavior, not host behavior.
No worktree or background service was created. Test fixture trees were disposable
and cleaned by their test harnesses; durable red/green/review evidence is retained.
