# R5 focused repair review

CONFIRMED: both reported defects are repaired on the frozen inputs below.
REFUTED: no additional actionable blocker established in the affected paths.
UNVERIFIED: live vendor compatibility, hosted GitHub behavior, and key scopes.

Disposition: accept the credential-reflection and partial-empty lifecycle repairs
for offline source/test acceptance. This does not establish hosted or live
acceptance. The initial reports and failed reproductions remain unchanged.

## Correction to the initial review

The initial deep report's REFUTED item 2 was too broad. It correctly traced safe
transport-error messages and redirect refusal, but missed a different path:
syntactically valid model IDs and pagination cursors could contain a credential.
Those values were rendered into worksheets or constructed into query URLs on the
initial hashes. The mechanical lane's M1 and whole-run reproduction demonstrated
that defect. I did not independently find it in the initial review. The initial
claim that credential reflection was prevented must not be used as acceptance
of that old candidate; this focused disposition supersedes it.

The initial report also misstated inherited context. The dispatcher confirms
`fork_turns=none`: no parent conversation history was supplied. This was a fresh
review context that received the scoped brief, later coordinator messages, global
instructions, and a shared filesystem. It used the same model family and was not
an isolated checkout or cross-family review. For this fix review, the coordinator
explicitly authorized reading the mechanical report to establish repair scope;
that is not independent corroboration of the original credential finding.

## Repaired candidate

Date: 2026-11-15. Dev mode: `mvp`.
Base HEAD: `8a2a00c434aba3885bb4195699e5621da20d694c`.
The review applies to frozen working files, not a new commit.

| Input | SHA256 |
| --- | --- |
| `scripts/model_watch.py` | `6cb77ceb5a319ebe2014d81c5928b00f522876f8ff2822438e48a84e654d6d92` |
| `.github/workflows/model-watch.yml` | `a7ff8878a01c91a5e879e44a824d3a9ba5483e443d4a44bef80d729fd749f2e4` |
| `tests/test_model_watch.py` | `7e4f24aee532a9caff7203d320d63c1308e8a8fa42584a1c06d4440384b5d16f` |
| `tests/test_model_watch_workflow.py` | `3da76f1fc53e75a559260241900b08c18f97be9b6c478bb9390c1a9164d5e63f` |

## M1 — credential reflection: repaired

The original attack story remains valid for the old candidate: a compromised
vendor returns a key received in its request as a syntactically valid ID or
cursor, causing a public worksheet leak or a subsequent request URL containing
the key. Character validation alone did not stop it.

Current controls:

- `_known_secrets` collects all five configured keys after surrounding-whitespace
  stripping, retaining valid visible-ASCII values (`scripts/model_watch.py:225`).
- `_refuse_reflection` fails with a fixed diagnostic on any raw ID containing a
  known key, before Gemini prefix stripping, ID validation, admission, or rendering
  (`:218-227`, `:282-288`). This also checks malformed IDs and OpenRouter's public
  listing, including another vendor's configured key.
- Both cursor paths apply the same guard before URL quoting/construction
  (`:230-249`). `check_vendor` passes the complete known-key set to both pagination
  and parsing (`:346-358`). This is fail-closed vendor error handling, not silent
  removal of a potentially material listing entry.
- The existing whole-run error path still publishes no candidate/PR artifact,
  while diagnostic output is a safe constant. No new key-bearing metadata or
  write-job secret was introduced.

Independent focused execution: both new regression methods passed, including
six vendor-ID subcases and both pagination types. In addition,
`reproduce_reflection_fixed.py` exercised 12 whole-run cases using five distinct
invented keys with surrounding whitespace: all six vendors, each with valid
wrapped and malformed IDs reflecting a different vendor's configured key.
Every case returned error, used the safe diagnostic, left no key in captured
output/files or request URLs, and created no PR body or candidate directory.
Raw results: `reflection-fixed-repro.json`. Probe exit: 0.

This checks the stated direct credential-reflection paths. It is not a general
claim to recognize every possible encoded representation of a secret, nor a
claim that a compromised vendor itself cannot misuse a key it already receives.

## D1 / M2 — partial-empty lifecycle: repaired

The original reachable sequence was a resolved last OpenAI worksheet while xAI
remained skipped without an old worksheet. The old `count == 0` return retained
obsolete proposals and the old PR report.

The new zero-count branch (`.github/workflows/model-watch.yml:207-226`) now
reconciles only when there is a skipped vendor and an existing observed branch:

1. It compares the desired candidate index against the observed branch SHA.
   When different, one bot reconciliation commit based on current main removes
   the obsolete proposals, then pushes with the same exact-SHA lease. The
   distinct head stays above main even when its tree equals main.
2. It always refreshes the existing PR body with the current incomplete report.
   An unchanged desired candidate tree produces no new commit. An absent branch
   creates neither an empty branch nor a PR.
3. A rejected lease exits before PR editing. Existing non-bot-author detection
   still prevents entry into the update step. Complete/no-difference closure is
   unchanged and still gated on `complete == true` and no foreign author.

Independent focused execution passed all three new lifecycle regressions: prune
and refresh, repeat without commit churn, and racing-update lease refusal without
PR modification. The neighboring tests also passed for no empty new PR,
complete-only closure with branch retention, and human-commit preservation.
The assertions establish a one-commit-above-main empty tree, removal of the old
worksheet, current PR body, stable SHA on repeat, and no CLI close in incomplete
runs. These are local-Git/stub-CLI observations.

The empty reconciliation commit avoids resetting the PR head exactly to main.
Hosted handling of a PR whose unique head commit has zero file differences still
remains UNVERIFIED; the fixture does not model GitHub's automatic lifecycle.
No hosted-open-state guarantee is inferred from these offline passes.

## Independent checks and shared provenance

This lane independently ran eight named focused unittest methods, without a
full-suite repeat. Raw output: `fix-focused-stderr.txt`; stdout:
`fix-focused-stdout.txt`. Decisive output:

```text
Ran 8 tests in 3.501s
OK
```

The two reflection methods, three new lifecycle methods, no-empty-PR method,
complete-close method, and human-commit method are named in that raw output.
The separate 12-case invented-key probe also exited 0. These executions used
mocked HTTP responses, disposable filesystem Git remotes, and the fixture's
stub `gh`; no real endpoint, key, hosted PR, or project Git write was used.

I read the retained root repair evidence: credential regressions originally
failed eight subcases, then all 34 watcher tests passed; the refined lifecycle
regressions originally failed all three methods, then all 18 workflow tests
passed. Those runs are coordinator execution, not this lane's independent runs:
`.research/r5-reflection-3m5z8olg/` and
`.research/r5-workflow-partial-empty-20261115T0117Z/`.

The final root receipt at `.research/r5-validation-final-xx35nmjd/receipt.json`
was read and its four source/test hashes match this review. It records validator,
full unittest discovery, CLI help, and diff-check exit 0. The coordinator reports
31 validated files/0 problems and 141 tests OK in 19.006s. It also reports no diff
in providers/models/schema/harnesses/VERSION/LICENSE. This is shared broad-run
provenance, not a second full-suite execution by this lane.

Both initial finding records and `partial-empty-repro.json` are preserved. All
writes by this review are confined to `docs/reviews/r5-deep/`. No source edits,
network access, installs, project commits/tags/pushes, signing, or releases ran.
The original live endpoint/key-scope/hosted acceptance limits remain open under
the coordinator's scope; no new blocker was established by the focused review.
