# R4 deep review findings — candidate 1

CONFIRMED: publication requires repairs before acceptance. One publication operand bug has conditional unintended-file disclosure; a separate repository-selection bug contradicts the documented destination. No additional blocking finding was confirmed in the archive/signature boundary.

Created: 2026-11-15T02:12:57.846412+00:00
Dev mode: mvp. Baseline/HEAD: `08d9fcb03744a188fe7f26b8305efe21ee8dc125`.
Candidate: uncommitted R4 sources identified by `.research/r4-84a2411b/evidence/candidate-1-sha256.json`; all 13 assigned paths independently matched it.
Configured reviewer: gpt-6.1-sol at xhigh. Actual provider/model identity, tokens and queue time: unavailable. Fresh same-family context, shared filesystem; no process/filesystem isolation claim. Cold read was recorded before receipts or coordinator findings in `cold-read.md` (SHA-256 `ae06006868531bea2d9810556aa4cb32fe35a4715ffdf6ccbba338146288bdae`). No sibling review was read.

## Findings

### D1 — CONFIRMED — high priority: gh reparses the verified asset path before upload

Location: `scripts/release_common.py:402`–405; the fake gh at `tests/test_release.py:449`–454 does not emulate this parsing. Coordinator-supplied after the immutable cold read, then independently assessed against source and locally installed primary GitHub CLI manuals. This is not an independently discovered cold-read finding.

The publisher verifies the three literal files under `--dir`, then supplies their resolved absolute paths directly to `gh release create`. GitHub CLI supports asset operands as patterns and `filename#label`; these are CLI-level interpretations and survive `shell=False`. Thus an accepted release directory containing `#` or glob metacharacters is not reliably the upload source. The current fake gh treats operands as literal pathlib paths, so its green upload tests miss this boundary.

For the concrete `#` case, a verified directory `/outside/private.pem#release` produces an operand `/outside/private.pem#release/registry.tar`. The documented label separator changes the source filename to `/outside/private.pem`. If that prefix is an existing private regular file and the operator has publication permission, its bytes can leave the machine during creation. Asset-list/download checks occur afterwards and cannot recover confidentiality. Without an existing prefix file, an otherwise valid path can instead fail publication. No actual private file or real GitHub publication was used in this review.

Security story: an operator publishing an otherwise valid release via a `--dir` containing `#` can cause gh's filename-label parser to upload an existing private file at the prefix path, disclosing it to the destination before post-publication checks fail.

Prerequisites are explicit: the directory must contain the special character, a sensitive regular prefix file must exist for disclosure, and the operator must be authorized at the selected GitHub destination. This does not establish that a hostile contributor can choose Michel's output path, and it does not rely on a same-user shell adversary or race. Treat the accepted-path confidentiality failure as a secret-handling floor defect; at minimum the ordinary valid-path publication defect is confirmed. Preserve literal byte/path binding before invoking gh, for example by staging verified public assets under fixed operand basenames. Quoting shell strings alone cannot fix gh's own grammar.

Primary local evidence: `/usr/share/man/man1/gh-release-create.1`, plus coordinator's read-only installed help result. Relevant excerpts and manual hashes are retained in `.research/r4-deep-only/scratch/installed-gh-manual-evidence.txt`. The real gh executable was never invoked by this reviewer.

### D2 — CONFIRMED — medium priority: publication destination is not pinned to origin

Location: `scripts/release_common.py:37`–42, 383, 396, 403, 406, 412; contradictory promise: `docs/releasing.md:7`–8 and its origin checks at 58–60/122.

All gh subprocesses inherit the process environment and omit an explicit repository/host. A checkout cwd does not guarantee origin: the installed GitHub CLI API manual states that `{owner}`/`{repo}` placeholders can use `GH_REPO`, and the installed default-repository manual describes a separately configured API destination. Therefore a stale `GH_REPO` or another configured default can redirect the numbering/tag preflight and release operation away from the origin Michel was told to inspect. If the destination also contains the target commit and permits creation, the command can create an unintended release; otherwise it can inspect unrelated release history or fail against the wrong repository.

This is a functional destination/precondition defect, not an asserted realistic attacker takeover: no actor's ability to edit the maintainer's environment is assumed. Pin the intended origin repository consistently for all API/create/download operations, or change the destination contract and make that destination explicit to the operator. A repair must also account for staging cwd changing repository inference.

Primary local evidence: `/usr/share/man/man1/gh-api.1:20`–22; `/usr/share/man/man1/gh-repo-set-default.1:13`–17; `/usr/share/man/man1/gh-release-create.1:115`–116. Preserved excerpts/hashes are in the same scratch evidence file. No real gh or network call was made.

## Refuted and bounded concerns

- REFUTED — unauthenticated manifest JSON use: `verify_release` reads a bounded byte buffer, calls signature verification at 315, and only parses JSON at 316. The shared receipt explicitly passes the invalid-JSON-before-signature test.
- REFUTED — tar traversal/hidden-header acceptance: 106–114 and 260–308 enforce safe JSON paths, complete and member digests/sizes, canonical actual ustar headers, exact sorted membership and zero padding/trailer without extraction. Signed adversarial archive cases in the shared receipt all report ok.
- REFUTED — wrong-key signing leaves an accepted final signature: 338–359 verifies a temporary signature with the current repository public PEM before exclusive final creation; the shared wrong-key/preservation tests pass.
- UNVERIFIED hardening — an attacker substituting a non-Ed25519 trusted public PEM could challenge algorithm strictness, but substituting the independently pinned repository/client trust key is the unavailable step at this mode; the ceremony explicitly generates Ed25519.
- UNVERIFIED hardening — changing manifest/signature/tar paths between reads requires concurrent local mutation controlled by a same-user shell adversary, excluded from the stated MVP trust model.

## Evidence and limits

Independently performed in this review:

- Read the complete assigned source, tests and documentation and confirmed baseline HEAD.
- Created the immutable cold-read note before opening any receipt or coordinator finding.
- Rehashed all 13 candidate-1 scope files: all matched the supplied candidate manifest.
- Rehashed all 34 current payload files against the supplied smoke manifest: all matched.
- Reconstructed the specified canonical POSIX ustar in memory from those exact payload bytes: 245760 bytes, SHA-256 `e7952e0e2b4f2fc3261a9e9800de8740c9e6f184c06a8cac783764cbdb2e1a8e`, matching the smoke receipt.
- Read primary installed GitHub CLI manuals as text only. No real gh invocation, network, real key, commit/tag/push, source edit or publication occurred.

Shared coordinator receipts, independently checked for scope/hash consistency but not rerun:

- `full-suite-1.txt`: 180 individual `... ok` results, `Ran 180 tests in 35.088s`, `OK`; signing/fake-gh paths are present and no actual skipped-result lines appear.
- `cli-smoke-1.json`: validator exit 0, 31 files/0 problems; four help exits 0; unsigned build exit 0, 34 files and the tar hash above.
- `smoke-manifest.json`: format 1, registry 1, repo_version 0.4.0, expected minimum-client map, per-file and full-tar hashes/sizes.

The full-suite text does not itself include argv, toolchain identity, timestamps or an explicit numeric process exit record; its execution provenance remains the coordinator's supplied receipt/attestation. Shared receipt reuse is not a second independent suite execution. Signing/publishing/client acceptance in a real deployment remains untested here; no real key currently exists by design. No performance claim is made.

Hash/provenance outputs are retained in `.research/r4-deep-only/scratch/provenance.json` and `provenance-clarification.json`. The clarification preserves and corrects a broad substring flag in the first record: test names contain the word skipped, but all 180 results are ok and there are no skipped-result lines. No evidence was replaced or erased.

Candidate-1 findings apply to the exact hashed source set only. Repaired publication paths, destination selection, and their interactions with create/download/verification need focused review and updated exact-candidate receipts. The archive/signature source conclusions carry only while those bytes remain unchanged.

## Post-report candidate drift notice

At 2026-11-15T02:13:52.927426+00:00, the coordinator notified this reviewer that the newly failing regression tests and fake-gh operand emulation had been appended after the cold read and provenance check. The prior 13/13 match was observed at `2026-11-15T02:10:12.440842+00:00`; it is historical evidence, not a claim that the current test file remains candidate 1. `tests/test_release.py` no longer matches the candidate-1 hash and its added tests have not yet been reviewed in this initial report. The old 180-case receipt does not cover those new bytes. Current differences at this notice:

- `tests/test_release.py`: candidate 1 `ec6442de39bc42c6f59b59ab914a37a24196238e12b01f680d1e927e58058781`, current `83b82b9a306d964d146eac144fe9725ed3de8f51e2ba06c2f4ba9ebfcbeb66fa`.

This notice does not revise the immutable cold-read note. Production repairs and the new regression tests require the requested focused review.
