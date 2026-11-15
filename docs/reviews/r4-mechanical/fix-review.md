# R4 candidate-2 focused mechanical re-review

Status: CONFIRMED repairs; accepted for this focused review. No remaining blocker found in the repaired paths or their local interactions.

Baseline HEAD remains `08d9fcb03744a188fe7f26b8305efe21ee8dc125`. Target is the explicitly frozen uncommitted candidate identified by `.research/r4-84a2411b/evidence/candidate-2-sha256.json`; all 13 recorded source/doc hashes independently matched current bytes. Mode: mvp. Requested configuration: gpt-6.1-sol high. Provider runtime identity, tokens and queue measurements remain unavailable. Fresh same-family review context, shared filesystem, no sandbox-isolation claim. The original `cold-read.md` and `findings.md` were preserved unchanged during this follow-up; the coordinator-supplied finding remains attributed as such.

## Disposition of candidate-1 findings

1. **CONFIRMED FIXED: gh filename-label/pattern operand interpretation.** `scripts/release_common.py:438` creates private upload/download staging directories; lines 447-450 copy only the three public release assets through regular-file handles. Line 451 verifies the staged copy before upload. Lines 452-455 pass exactly the fixed asset basenames with the upload directory as cwd. The user-supplied directory, including any `#`, `[` or `*`, is therefore absent from gh's asset operands. Download comparisons use the same authenticated staged originals at lines 468-474. The unintended-readable-prefix-file path from the initial finding is closed.

2. **CONFIRMED FIXED: malformed remote asset-name types.** `scripts/release_common.py:458` validates the remote object/list/member shapes and requires string names at lines 459-460 before sorting at line 461. A null name now produces a clean operational refusal rather than uncaught `TypeError`.

## Affected interactions

- `scripts/release_common.py:383` parses an explicit GitHub.com `origin`, admitting credential-free HTTPS and Git SSH forms while rejecting other hosts, local remotes, malformed owner/repository paths, and query/fragment input. API calls at lines 374 and 456 pin the hostname and explicit repository path. Creation at line 452 and download at line 463 pin the fully qualified repository, so changing the upload cwd does not change destination selection through gh's inherited defaults.
- `scripts/release_common.py:431` rejects malformed tag-reference types before the existing-target check. Consecutive-number and existing-tag checks remain before creation; the repair introduces no delete, replacement or clobber path.
- `scripts/release_common.py:365` invokes the subprocess outside the JSON-decoding exception handler. A `ReleaseError` from a failed gh command retains the original command-failure purpose instead of being relabeled invalid JSON.
- The updated fake gh applies filename-label splitting and glob interpretation; the added regression uses a literal hash/glob directory with an existing unrelated prefix file, then checks exact uploaded names and bytes. Destination-environment, HTTPS/SSH origins, invalid origin, null asset-name and malformed tag-reference cases cover the affected branches. Release procedure, architecture and signing decision wording match staging and explicit destination binding.

## Evidence and independent checks

Shared receipts inspected, without rerunning the broad suite:

- `publish-regression-red.txt`: `Ran 13 tests in 7.381s`, `FAILED (failures=8)` against the unrepaired implementation, including the original traceback edge.
- `publish-regression-green.txt`: `Ran 13 tests in 6.811s`, `OK` after repair.
- `full-suite-2.txt` and `full-suite-2-result.json`: `Ran 187 tests in 31.158s`, `OK`; exit 0, Python 3.12.3, repository cwd and UTC start recorded. This is shared validation evidence, not a second independent full-suite execution.
- `candidate-2-checks.json`: validator `31 files checked; 0 problems; clean`; four CLI helps exit 0; smoke build reports 34 files and unchanged tar SHA-256 `e7952e0e2b4f2fc3261a9e9800de8740c9e6f184c06a8cac783764cbdb2e1a8e`.

Independent checks run by this reviewer, with every subprocess boundary mocked:

- All 13 candidate hashes match; `smoke-manifest-2.json` is canonical and all 34 current payload hash/size records match. Its tar record remains 245760 bytes with the SHA-256 above; the smoke archive bytes were not independently rehashed.
- A literal `literal#release[1]*` source directory successfully traverses staging/upload/download checks with fixed basename operands, explicit repository arguments and two verification calls. No real gh was run.
- Null remote asset-name handling exits 1 cleanly, with no traceback; the staged copy is verified before the simulated creation.
- A failed inspection command preserves its original `published release inspection: command failed` diagnostic through `gh_json`.

Focused raw evidence: `.research/r4-mechanical-only/scratch/candidate-2/focused-checks.json`. Its tiny public fixture files are disposable reviewer-created material, retained with the receipt. No source file was changed by this review.

## Limits

No network, real gh, real signing key, commit, tag, push or publication occurred. This accepts the source repairs and offline evidence for the pinned candidate only; live GitHub CLI/API acceptance, first-key ceremony, publication and consuming-client acceptance remain unverified. No performance claim or broader new review is implied. Excluded paths remained all sibling review files and `.research/r4-deep-only/*`.
