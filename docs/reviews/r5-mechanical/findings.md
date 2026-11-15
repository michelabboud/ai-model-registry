# R5 mechanical review — initial frozen candidate

CONFIRMED: 2 blocking findings (M1 credential reflection; M2 partial empty reconciliation).

REFUTED: no additional blocking findings established in the reviewed boundaries; the checks listed below support their stated scope only.

UNVERIFIED: live vendor response compatibility, hosted Actions/permissions/PR behavior, and cryptographic assurance of bot authorship. These remain explicit task limitations, not offline acceptance claims.

Date: 2026-11-15. Dev mode: `mvp`. Base supplied: `8a2a00c434aba3885bb4195699e5621da20d694c`. The reviewed candidate is the frozen working files, not a new commit. This report preserves the initial findings even when later repairs change those files.

| Primary input | SHA-256 |
| --- | --- |
| `scripts/model_watch.py` | `bd2bdeb3edd75bd1221c976b696d1af5b83491d34ad5375559e6781ac7611ac7` |
| `.github/workflows/model-watch.yml` | `d9329b572254fc0cfd595497c7a01c9f46db310b7d2f829331315e5ed16d1846` |
| `tests/test_model_watch.py` | `2963d58f32420fa84553bd23210da587053a24b89f16c9d7e9e7e8fcabaa2730` |
| `tests/test_model_watch_workflow.py` | `325c14c978ee94ca9d6c05352876d833439c48f0859bef07248f44fe2e8f016a` |

## M1 — Credential reflection reaches worksheet artifacts and cursor URLs

**Blocking, high severity, due now.** Locations in the pinned script: lines 218–235 (`_next_url`), 267–282 (`parse_listing`), and the new-ID rendering in `candidate_markdown`.

Attack story: a hostile or compromised vendor list endpoint returns the API key it just received as a valid-looking model ID or pagination cursor; the watcher then publishes that key in a worksheet/PR branch or sends it in the next request URL.

Syntax validation does not establish that an ID or cursor is safe to publish. A token such as the invented `fixture-secret-reflection-only` satisfies both ID and page-token grammars. No comparison against credentials occurs before IDs enter `listing.text_ids`, before new-ID worksheets are rendered, or before pagination URLs are constructed. URL quoting leaves this token unchanged. This violates the stated requirement that vendor keys stay only in headers and never reach URLs, files, artifacts, or output.

**Offline reproduction:** load `scripts/model_watch.py` through `importlib`; select OpenAI; mock `fetch_pages` to return `[{"data": [{"id": key}]}]`; call `check_vendor(ROOT, openai, {openai.env_key: key})`, then `candidate_markdown(result)`. The result is `checked`, the added IDs contain the key, and the worksheet contains it. `focused-checks.json` records those booleans. The same file records that `_next_url` returns a URL containing the key for Anthropic `{"data":[{"id":key}],"has_more":true,"last_id":key}` and Gemini `{"models":[],"nextPageToken":key}`.

**Whole-run confirmation:** use `tests/test_model_watch.py`'s invented `WatchCase` root, `matching_routes`, and mocked `FakeOpener`; append `{"id": SENTINEL}` to OpenAI's listing, where `SENTINEL` is also the supplied fake key, and call `run_watch(responses=data)`. `run-reflection-check.json` records `exit_code: 3`, `leaked_worksheet_names: ["openai.md"]`, and `pr_body_created: true`. No network or real credential was used. The workflow copies this named worksheet into the artifact and subsequently the write job's branch; GitHub log masking does not sanitize repository file bytes.

Required repair boundary: refuse reflected known credentials before rendering or cursor URL construction with a safe diagnostic; regression coverage must include IDs and both cursor types. Do not silently drop the credential and continue a potentially incomplete listing.

## M2 — Partial empty reconciliation retains resolved checked-vendor worksheets

**Blocking specification violation, medium severity.** Location in pinned workflow: `.github/workflows/model-watch.yml:207–209`, with the complete-only close condition at lines 231–234.

Reachable sequence: a prior bot branch contains only `candidates/openai.md`; the next successful run finds OpenAI resolved, skips xAI because its key is absent, has no prior xAI worksheet to carry, and finds no fresh changes. Rebuilding from `main` produces zero worksheets. The `count == 0` early return occurs before the branch is updated and before the PR body is edited. The later close step is correctly ineligible for an incomplete run, leaving the resolved OpenAI worksheet and old PR body in place indefinitely.

The guide and handoff promise that successful partial runs remove worksheets resolved by checked vendors while preserving skipped worksheets, and that skipped status is visible. This case does neither for the published branch/PR. It must preserve the incomplete-run semantics without retaining checked-vendor proposals that have resolved.

**Offline reproduction:** instantiate `WorkflowShell` from `tests/test_model_watch_workflow.py`, run `setUp()`, seed `fixture(openai='was missing, now resolved')`, call `reconcile()`, then clear the fixture and call `reconcile(skipped='xai', pr='7')`. All Git remotes and the `gh` executable are disposable local fixtures. `partial-empty-check.json` records `branch_unchanged: true`, `resolved_openai_worksheet_still_present: true`, `branch_foreign: "false"`, and `pr_write_calls: []`. This focused check was launched before the coordinator informed this lane of a matching symptom from another review; no sibling report was opened or compared.

## Checked scope and evidence

- Read `CLAUDE.md`, the model-watch guide and ADR 0005 as the specification; reviewed the script, workflow, both test modules, every invented vendor fixture, fixture README, changed tracked documentation, and the new R5 handoff/validation report. `cold-read.md` was written after source reading and before the broader material/reproductions.
- Independently calculated the four primary hashes above. They match the root validation receipt at `.research/r5-validation-hcetow5k/receipt.json`.
- Independently executed no-network `load_registry(ROOT, vendor)` against all six real provider/model files: OpenAI 31, Anthropic 15, Gemini 15, xAI 8, DeepSeek 2, OpenRouter 72 records; all loaded successfully. The counts and focused reflection results are preserved in `focused-checks.json`.
- Reviewed fixed endpoints/auth headers, optional secret handling, OpenRouter's public path, filters, active/missing versus deprecated behavior, all-IDs completeness, cumulative byte/entry/page limits, malformed response handling, redirect refusal, safe transport errors, known worksheet-name admission, symlink checks, trigger/permission separation, lease protection, cooperative human-author preservation, skipped carry-forward, and complete-only closure. No further reachable blocker was established in that scope.
- The root's shared exact-candidate receipt reports validator exit 0 (31 files, 0 problems), 136 unit tests OK in 19.480s, help exit 0, `git diff --check` exit 0, and no diff in provider/model/schema/harness/version/license paths. This lane verified receipt identity and scope; it did not independently repeat that broad suite. The green suite omitted the two reproduced cases above.

## Independence and limits

Fresh-context review, shared filesystem, same model family. No sibling review output was read. The coordinator supplied the initial brief and root validation receipt and later disclosed a matching lifecycle symptom after this lane had already launched its own reproduction. This is not cross-family review and the shared test receipt is not a second execution.

No source, fixture, workflow, registry record, or repository metadata was changed by this lane. Writes are confined to this review directory. No network, installs, real keys, repository commits, tags, pushes, signing, releases, or subagents were used. Disposable workflow-test Git operations occurred only against temporary filesystem repositories. Runtime token usage and queue/latency measurements are unavailable from this review environment.
