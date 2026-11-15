# R4 focused repair review — candidates 2 and 3

CONFIRMED FIXED: D1 (GitHub CLI asset operand parsing), D2 (publication destination binding), and the recovery-command documentation follow-up. No remaining blocking finding was identified in the repaired scope.

Created: 2026-11-15T02:29:44.007584+00:00
Dev mode: mvp. Baseline/HEAD confirmed: `08d9fcb03744a188fe7f26b8305efe21ee8dc125`.
Final reviewed candidate: `.research/r4-84a2411b/evidence/candidate-3-sha256.json` (13 paths; manifest SHA-256 `2c91df3d32e0a7b6d9b85700be1f8014757a4a924937a356b15a7ff836036a15`). Candidate 3 changes only `docs/releasing.md` relative to candidate 2; all production/test bytes retain the candidate-2 tested hashes.
Reviewer configured by coordinator: gpt-6.1-sol, xhigh. Actual provider/model identity, token usage and queue time are unavailable. This is the same independently dispatched review context as the initial deep review, within the same model family and a shared filesystem; no process/filesystem isolation claim. No sibling review was inspected.

The immutable cold read and initial findings remain preserved. Their hashes at final provenance verification were `ae06006868531bea2d9810556aa4cb32fe35a4715ffdf6ccbba338146288bdae` and `33a8ae224f549ad3e4e94e304e65af7d6a755d49b6d64149c8c623e6338de137` respectively. The original findings remain valid historical defects; they are resolved by the reviewed repair, not refuted retrospectively.

## Dispositions

| Finding | Disposition | Evidence |
| --- | --- | --- |
| D1: resolved absolute asset paths exposed to gh's filename-label/glob parser | CONFIRMED FIXED | `scripts/release_common.py:438`–455 stages only the three fixed public assets, re-verifies the staged set at 451, and supplies literal fixed `ASSETS` basenames from `cwd=upload`. |
| D2: gh environment/default repository can override the documented origin | CONFIRMED FIXED | `scripts/release_common.py:383`–407 parses a credential-free GitHub.com origin; 374 and 417/430/456 use explicit host and full owner/repository API paths; 452 and 463 supply explicit host-qualified `--repo` for creation and download. |
| D3: manual recovery inspection still inherited the wrong repository context | CONFIRMED FIXED in candidate 3 | `docs/releasing.md:125` pins authentication status to `github.com`; 175–178 pins recovery inspection to `github.com/OWNER/REPO` and says to substitute the validated origin. |

D1's conditional disclosure story was: an operator supplying an otherwise-valid release directory containing `#` could cause gh to upload an existing private prefix file before post-upload checks. The repair removes that path from every upload operand. A private temporary parent contains only `upload/` and `download/`; only `registry.tar`, `manifest.json`, and `manifest.json.sig` are copied into upload. Its fixed operand names contain neither label delimiters nor pattern characters. Original `--dir` characters, and characters in the temporary directory's absolute path, are no longer parsed as asset operands. Ordinary valid special-character paths remain supported.

The staged files are authenticated again before the first remote mutation. `verify_release(upload)` still obtains the trust key from the repository's fixed `ROOT / PUBLIC_KEY`, not from the staging directory or artifact contents. No private-key parameter is added to publishing, no key file is copied, and the signer remains the sole private-key path (metadata in Python, bytes read only by OpenSSL). Download comparison at 468–476 uses the exact verified staged upload bytes, so later changes to the original release directory do not redefine the comparison baseline.

D2's repair retains the source checkout's Git operations through the command helper's default cwd while explicitly binding GitHub operations. Moving only release creation's cwd into upload therefore does not require Git repository inference there. API calls pin `--hostname github.com` and literal `repos/OWNER/REPO/...` endpoints; creation and download each pin `--repo github.com/OWNER/REPO`. A hostile-looking or stale `GH_REPO`/`GH_HOST` value is no longer the destination selector. Supported origin forms and the GitHub.com restriction are accurately recorded in the guide, architecture and signing decision.

Other repaired interactions were checked: malformed tag-reference names are refused before creation at 431–434; malformed asset names are refused cleanly at 458–462; JSON response parsing no longer catches and relabels an underlying command failure because `gh_json` executes its command outside the JSON try block (365–370). Existing verify-before-gh, all-page numbering, existing-tag refusal, exact remote assets, download comparison and preservation of partial remote state remain in place.

## Verification and provenance

Independent work performed by this reviewer:

- Read the complete repaired shared release implementation, changed publication tests/fake gh, release guide, signing decision and architecture changes. Verified all 13 candidate-2 hashes and all 13 final candidate-3 hashes against the actual files.
- Confirmed the only candidate-2 to candidate-3 scope change is `docs/releasing.md` (from `d84393131ba165fb27a86bad687c0ac2e51d6732b4d73585ec6233f2ce9232fb` to `74429be4d6e62516f6e7d002e57e286fbd0b865fc6d5e8d0d1a0f18ff7367326`). Python/test/payload/format bytes did not change for that correction. The retained candidate-2 test receipts therefore apply to those same production/test bytes; no repeat suite is warranted for the documentation-only correction.
- Ran a bounded 18-case offline check of `github_repository` using mocked git responses only: accepted intended HTTPS/SCP/SSH forms and explicit standard ports, and rejected wrong hosts/ports, embedded credentials, query/fragment, dot traversal, encoded separators and extra path components. All 18 expected outcomes passed. This made no actual git, gh or network call and generated no key.
- Rehashed all 34 current payload files against the candidate-2 smoke manifest; every hash/size matched. The smoke manifest is byte-identical to the candidate-1 smoke manifest whose tar was independently reconstructed in memory by this reviewer: 245760 bytes, SHA-256 `e7952e0e2b4f2fc3261a9e9800de8740c9e6f184c06a8cac783764cbdb2e1a8e`.

Shared coordinator executions, inspected for scope/provenance and not independently rerun:

- `publish-regression-red.txt`: 13 publication tests, eight failing assertions including subtests before repair. The fake gh now implements the documented filename-label/pattern operand behavior; the old literal-`#` path test fails only after the wrong upload path has been consumed, and origin-binding assertions expose the missing selectors.
- `publish-regression-green.txt`: the same 13 publication tests all report `ok`, ending `Ran 13 tests in 6.811s` / `OK` after repair. Coverage includes literal special-character directories, explicit destination flags despite alternate gh environment, supported/invalid origins, null asset names, malformed refs, original numbering/tag checks, verify-before-gh and post-upload corruption checks.
- `full-suite-2-result.json` and matching raw `full-suite-2.txt`: argv `/usr/bin/python3 -m unittest discover -s tests`, cwd `/home/michel/projects/ai-model-registry`, start `2026-11-15T02:19:59.916072+00:00`, Python 3.12.3, exit 0; decisive output `Ran 187 tests in 31.158s` / `OK`. The raw progress line contains 187 success dots with no skip marker.
- `candidate-2-checks.json`: validator exit 0 / 31 files / 0 problems, all four help commands exit 0, and unsigned smoke build exit 0 / 34 files / the tar hash above.
- `candidate-3-docs-only.json`: records the exact documentation-only change and explicitly carries forward `full-suite-2-result.json`; independent hash comparison corroborates that scope justification.

Detailed independent outputs and receipt hashes are preserved at `.research/r4-deep-only/scratch/candidate-2-focused-checks.json` and `candidate-3-provenance.json`. This review reused the broad suite receipt as one execution, not as a second independent run.

## Limits

This focused review closes the recorded defects and affected publication interactions on the final hashed source set. It does not establish live GitHub API/create/download behavior, a real key ceremony, signed real publication, or consumer integration; those were intentionally outside the authorized review. No network, real gh executable, real keys, source edits, commits, tags or pushes were used by this reviewer. No performance improvement is claimed. Prior hardening-only concerns remain bounded by the original MVP trust sketch rather than being expanded into new requirements.
