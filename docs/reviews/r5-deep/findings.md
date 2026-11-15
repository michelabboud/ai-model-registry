# R5 independent deep review

CONFIRMED: 1 functional finding. REFUTED: 4 suspected boundary failures.
UNVERIFIED: live compatibility, hosted integration, and vendor key scopes.

Recommendation: repair the incomplete/empty worksheet reconciliation case before
accepting the documented R5 lifecycle behavior. No realistic credential leak,
code injection, or repository-write boundary bypass was found in the reviewed
vendor-response paths. This is an offline source review, not live acceptance.

## Candidate and independence

Date: 2026-11-15. Dev mode: `mvp`.
Base HEAD: `8a2a00c434aba3885bb4195699e5621da20d694c`.
The actual candidate is the frozen working files, pinned below. Hashes were read
at the initial inspection and again after the reproduction; they did not change.

| Frozen input | SHA256 |
| --- | --- |
| `scripts/model_watch.py` | `bd2bdeb3edd75bd1221c976b696d1af5b83491d34ad5375559e6781ac7611ac7` |
| `.github/workflows/model-watch.yml` | `d9329b572254fc0cfd595497c7a01c9f46db310b7d2f829331315e5ed16d1846` |
| `tests/test_model_watch.py` | `2963d58f32420fa84553bd23210da587053a24b89f16c9d7e9e7e8fcabaa2730` |
| `tests/test_model_watch_workflow.py` | `325c14c978ee94ca9d6c05352876d833439c48f0859bef07248f44fe2e8f016a` |

Read scope: `CLAUDE.md`, plan/progress/handoff records, the model-watch guide,
ADR 0005, script/workflow, both new test modules, every invented response fixture,
`.env.example`, and affected-document references. Michel's Genie design guide,
workflow, and relevant script structure were read only. The separate mechanical
review output was not opened. The initial impressions are in `cold-read.md`.

This is a fresh same-family review task on a shared filesystem with inherited
session context. It is not second-family independence or an isolated checkout.
Only this report directory was written. No source fixes, real network access,
installs, repository commits/tags/pushes, signing, or release operation ran.
The reproduction creates commits and pushes only inside disposable local-Git
fixtures, using the existing test harness and its stub `gh` executable.

## CONFIRMED — D1, P2: an incomplete empty run retains resolved proposals

Location: `.github/workflows/model-watch.yml:207-209`; the close condition at
lines 233-234 makes the retained state persistent while any vendor stays skipped.
Relevant missing case: `tests/test_model_watch_workflow.py` covers clearing a
checked worksheet when another stale worksheet remains, but not when none remains.

Trigger/impact story: the normal operator leaves xAI's optional secret absent,
while a previously reported OpenAI difference is resolved in the registry; a
successful run then retains the obsolete OpenAI worksheet and old PR summary
indefinitely, even though OpenAI was checked successfully. No attacker is needed.
This is a functional lifecycle defect, not a security-floor claim.

The update step reconstructs the desired tree from main, fresh artifacts, and
skipped-vendor carry-forward. If that tree contains zero worksheets, it exits
before publishing the removal or editing the existing PR body. With
`complete=false`, the close step is correctly ineligible. The previous published
branch and open PR therefore still show the resolved checked-vendor proposal.
That contradicts the guide's and handoff's explicit claim that successful partial
runs clear resolved checked-vendor worksheets.

Offline reproduction:

1. Run the real extracted workflow shell against the existing disposable local
   Git/stub-`gh` fixture with `openai.md` as the only old worksheet.
2. Supply an empty next artifact, `SKIPPED=xai`, and existing PR `7`.
3. The shell exits 0 with `No worksheets remain from this run.` The branch SHA
   remains identical, `openai.md` still contains the old resolved proposal, and
   the only new `gh` calls are authentication setup and PR lookup. No PR edit or
   close occurs.

Preserved reproduction: `reproduce_partial_empty.py`.
Raw result: `partial-empty-repro.json`.
Command: `python3 docs/reviews/r5-deep/reproduce_partial_empty.py`.

Expected behavior needs an explicit empty/incomplete reconciliation path that
removes resolved proposals and reports the current incomplete status, while
preserving the requirement that only a complete no-difference run closes a PR.
The current broad passing suite does not cover this branch.

## REFUTED — reviewed attack paths

1. **Vendor ID to shell/path/Markdown injection:** an attacker controlling a list
   response cannot inject shell syntax or select an output filename through an
   ID. `valid_model_id` rejects traversal, whitespace, quotes/backticks, extra
   slashes, and oversized IDs (`scripts/model_watch.py:190-197`); rejected values
   only increment a count (`:271-273`). Output filenames derive exclusively from
   the fixed vendor table (`:459-468`). The write job copies/stages only six fixed
   names and rejects artifact directory/file symlinks (workflow `:164-185`,
   `:199-204`). Model values are never evaluated as commands. Repro evidence:
   source trace plus the hostile-ID, symlink, and unknown-filename fixture tests;
   this lane did not repeat those passing tests.
2. **Credential reflection or cross-host redirect replay:** fixed HTTPS URLs,
   header-only authentication, redirect refusal, visible-ASCII validation after
   stripping whitespace, and non-reflective transport errors prevent the reviewed
   paths (`scripts/model_watch.py:126-187`, `:241-244`, `:330-340`). Request/header
   errors are reduced to safe messages, not exception bodies. Tests contain
   sentinel-key and redirect cases. No live redirect or key was used.
3. **Vendor handling obtains repository write authority or edits records:** the
   watch job has only `contents: read` and keys restricted to its vendor step;
   the separate write job has no vendor keys or vendor-facing script invocation
   (workflow `:19-46`, `:87-115`). It consumes fixed-path Markdown as data. The
   script's proposal writes and protected metadata targets do not edit the data
   trees (`scripts/model_watch.py:436-468`). No signing key, sign/release command,
   or main push is present. A compromised trusted main/runner remains outside
   the stated parsing boundary; the write token itself is not cryptographically
   restricted to candidate paths.
4. **Incomplete/error listings silently become retirement facts:** cumulative
   byte, raw-entry, and page bounds fail rather than truncate; malformed required
   envelopes/cursors fail (`scripts/model_watch.py:151-187`, `:208-283`). One
   vendor error prevents worksheet publication (`:493-498`). Missing detection
   uses every admitted listed ID, including IDs excluded from new text proposals
   (`:274`, `:341-346`), and only active GA/preview records. The worksheet calls
   absence a prompt to check access/deprecation, with every value TO VERIFY
   (`:385-390`). Fixture tests exercise these cases; no live retirement claim
   was accepted.

## UNVERIFIED — explicit acceptance boundaries

- **Live vendor behavior/capacity:** Anthropic, DeepSeek, and xAI response shapes
  remain UNVERIFIED. Invented fixtures establish parser behavior only. No current
  response proves all real listings fit 4 MiB/2,000 raw entries/10 pages, or that
  vendor visibility supplies an exhaustive account-independent inventory. A live
  limit failure is safe failure, not evidence of retirement. The coordinator owns
  this separately authorized live check.
- **Hosted GitHub behavior:** local shell simulations do not prove action SHA
  availability, the runner's installed tool versions, token/ruleset permissions,
  PR creation settings, or hosted PR lifecycle acceptance. The trusted workflow
  is statically pinned and has the intended triggers/permissions/timeouts.
- **Enforceable key scopes:** this offline review cannot establish current
  fine-grained list-only controls for Anthropic, Gemini, xAI, or DeepSeek. The
  guide explicitly records that API-service restrictions and spending caps do
  not create list-only permissions. The unresolved setup questions are retained
  instead of being presented as satisfied controls.

Human branch preservation is cooperative, as documented: a non-bot author
already present at branch discovery suppresses both update and closure, and a
racing push blocks a later lease-protected branch overwrite. The PR edit/close
operations themselves are not atomic with that earlier author check. No stronger
race-free human-work guarantee or cryptographic bot attribution is claimed here;
the supplied tests do not establish one. This is a residual coordination
limitation, not a demonstrated credential/data-loss attack or another blocker.

## Validation evidence

This lane independently executed the one targeted local-Git reproduction above.
It reproduced the defect with exit 0 and preserved the decisive branch/file/CLI
observations. The four primary hashes were rechecked unchanged afterward.

The parent reports the shared frozen-candidate acceptance run: validator 31 files,
0 problems; unittest 136 tests, OK in 19.480s; CLI help exit 0; diff-check exit 0;
no changes in providers/models/schema/harnesses/VERSION/LICENSE. Its receipt is
`.research/r5-validation-hcetow5k/receipt.json`. These are shared provenance,
not independent test execution by this lane, and do not refute the uncovered case.
No redundant full-suite run or network check was performed.
