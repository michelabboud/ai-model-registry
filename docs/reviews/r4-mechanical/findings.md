# R4 mechanical review

Status: CONFIRMED source and receipt checks; UNVERIFIED coordinator-supplied publication-path concern pending disposition. No independently identified floor blocker.

Baseline: `08d9fcb03744a188fe7f26b8305efe21ee8dc125`. Target: frozen uncommitted R4 candidate identified by `.research/r4-84a2411b/evidence/candidate-1-sha256.json`. All 13 recorded hashes matched this review's current source/doc bytes. Mode: mvp. Requested configuration: gpt-6.1-sol high; actual provider runtime and tokens unavailable. Same-family fresh context and shared filesystem, with no sandbox-isolation claim. Working-tree review was explicitly requested; ordinary commit-pinning requirements were not silently claimed satisfied.

The independent source assessment is preserved in `cold-read.md`, written before receipt inspection or any supplied concern. No other review, sibling scratch, or coordinator adjudication was read. Excluded paths: all other `docs/reviews/*` and `.research/r4-deep-only/*`. Sources remained read only; report files and `.research/r4-mechanical-only/scratch/focused-checks.json` are this lane's only intentional writes.

## Findings

1. **UNVERIFIED, later supplied by coordinator: gh filename-label parsing may upload an unintended local file.** `scripts/release_common.py:402` passes absolute asset paths derived from unrestricted `--dir` to `gh release create` at line 403, before remote inspection/download checks at lines 406-424. The coordinator supplied the concern after the cold read: `gh` interprets `#` within a file argument as a display-label delimiter. If confirmed, an attacker able to provide a signed release under a directory whose absolute path contains `#` could induce a publishing maintainer to upload an unrelated readable local file at the path prefix, disclosing it before the post-upload checks fail. This lane did not execute real gh or inspect its parser, so the exact delimiter behavior and reachable harm remain for coordinator evidence and ruling; this concern is not independent corroboration.

2. **CONFIRMED, informational robustness: malformed remote asset-name types bypass the clean diagnostic boundary.** `scripts/release_common.py:409` sorts names before validating they are strings. A mocked API response with `assets=[{"name":null},{"name":"registry.tar"}]` raises `TypeError`, which `cli_result` at line 437 does not catch. No realistic actor or current GitHub API path producing this response was established, so this is nonblocking robustness work, not a security blocker. The fake-gh suite covers an extra string-named remote asset at `tests/test_release.py:515`, but not this type error.

## Verified evidence

- Shared broad gate: `.research/r4-84a2411b/evidence/full-suite-1.txt` reports `Ran 180 tests in 35.088s` and `OK`. Reused receipt, not independent execution; this review does not claim a second full-suite run.
- Shared smoke receipt: validator reports `31 files checked; 0 problems; clean`; four CLI helps exit 0; clean-data build reports 34 files and tar SHA-256 `e7952e0e2b4f2fc3261a9e9800de8740c9e6f184c06a8cac783764cbdb2e1a8e`.
- Independent provenance check: all 13 candidate hashes match. Smoke manifest parses as canonical format 1 and all 34 file hash/size records match the current payload files; tar byte count is 245760. The original smoke tar was not independently available through this review's allowed receipt scope, so its bytes were not rehashed here.
- Independent focused checks: all actual subprocess boundaries were mocked. Injected release-create, remote-inspection and download failures each produced clean operational exit 1 and no delete/clobber command. The malformed-name `TypeError` above was independently reproduced. Details: `.research/r4-mechanical-only/scratch/focused-checks.json`.
- Source confirms the required dirty-data, nonempty-output and private-PEM-ignore negative tests; signature-before-JSON, wrong-key, raw signature length, missing public key, tampered tar/manifest, unsafe membership, duplicate members/JSON keys, malformed manifest fields, hidden PAX headers and appended content are covered.

## Limits and disposition

No network, real gh, real signing key, commit, tag, push or publication occurred. Real GitHub API/CLI conformance, first-key ceremony, live publication and consuming-client acceptance remain unverified. Same-user path replacement races and concurrent publication require operator control already documented; no attack window under another actor's control was established, so these are hardening concerns only. No performance improvement is claimed; the current archive is small and no benchmark was run.

The coordinator must rule on the supplied `#` concern before acceptance. Changes to affected candidate bytes require updated hashes, focused checks and review; this report applies only to the 13-file candidate recorded above.

## Final candidate-1 supplement

**CONFIRMED, repair required: supplied gh filename-label concern.** After the original report above was written, the coordinator reported installed `gh release create --help` evidence confirming `filename#label` interpretation and asset pattern handling. The reviewer did not execute real gh; the evidence attribution remains the coordinator's, and this is an ordinary finding added after cold read. The absence of a guard or upload staging at `scripts/release_common.py:402` allows valid signed artifacts in a directory containing `#` to reach different CLI filename semantics at line 403. At minimum this breaks publication from such a directory; when the prefix before `#` is an existing readable file, publication can upload that file's bytes before lines 406-424 detect an asset mismatch. Disclosure additionally requires that exact existing-prefix-file prerequisite. A supplied signed release directory can meet the signature check without controlling the signing key, so signature verification alone does not rule out this path. Fix and focused re-review are required before this candidate's acceptance.

Final candidate-1 disposition: one confirmed supplied publication-path defect requiring repair; one independently confirmed informational malformed-response diagnostic edge; no other independently identified blocking finding. The cold-read note and original assessment above remain preserved. Candidate-2 review is a separate, focused follow-up after the coordinator's repair and updated evidence.
