# R4 local release-tooling validation

Current state: repaired candidate 2 passes **187 tests**, the validator, four help
commands and the unsigned dry build. Focused mechanical/deep repair reviews are
accepted; the deep reviewer also accepted the final recovery-command docs.
Candidate 1 and its failures/reviews below remain historical evidence.

Date: 2026-11-15. Dev mode: mvp. Source baseline: `main` at `08d9fcb`, version
`0.4.0`. The checkout and all four data paths were clean at lane start. R4 changes
remain uncommitted by explicit instruction. No network, GitHub operation, real
key creation, version bump, commit, tag or push was performed. Temporary tests
generate and remove only run-owned throwaway Ed25519 keys.

## Initial candidate 1 and check matrix

The source under review is pinned by
`.research/r4-84a2411b/evidence/candidate-1-sha256.json`. It includes all four
CLI wrappers, shared format/verifier, release tests, ignore rules and release/key
guides. Data and schemas are unchanged. The final Git-status receipt will name
the remaining documentation and review artifacts. The two reviewers share this
receipt; it is one execution, not independent execution by both reviewers.

| Changed area | Check | Result |
| --- | --- | --- |
| Deterministic packaging/canonical manifest | Byte-identical tar after source mtime/mode changes; independent expected path/hash/size records and exact canonical bytes | Passed |
| Build admission | Real local-clone Git modified, staged and untracked data; validator failure; nonempty/symlink/data-path output; absent public key | Passed |
| Signing/key metadata | Throwaway sign→verify; wrong signing/verification key; 0644, symlink, internal path/alias, directory key; absent public key; existing signature preserved | Passed |
| Reference verification | Tampered manifest/tar; signed extra/missing/duplicate/traversal/absolute/link/device members; wrong member hash/size; PAX header; appended content; canonical/duplicate/invalid JSON; old/missing OpenSSL; symlink asset | Passed |
| Publication | Fake `gh` only: all-page consecutive numbering, existing tag, verify before CLI, exact upload assets, download bytes/corruption and extra remote asset | Passed |
| Secret exclusion | `git check-ignore` matches root and `keys/` private PEM filenames; committed public PEM name remains admissible | Passed |
| Integrated registry | `python3 scripts/validate.py` | 31 files checked; 0 problems; clean; exit 0 |
| Integrated tests | `python3 -m unittest discover -s tests -v` | 180 tests in 35.088s; OK; exit 0 |
| Four release CLIs | Each script's `--help` | All exit 0 |
| Unsigned build with clean data paths | `build_release.py --registry 1 --out <temporary-new-directory>` | 34 files; source version 0.4.0; exit 0 |

Dry-build archive: **245,760 bytes**. SHA-256:
`e7952e0e2b4f2fc3261a9e9800de8740c9e6f184c06a8cac783764cbdb2e1a8e`.
The 34 files are 31 data records and 3 schemas. The smoke build used no key;
its temporary archive was disposable, and its exact public manifest is retained.
The entire implementation checkout is dirty, while `git status --porcelain --
providers models harnesses schema` remains empty, matching build admission.

## Raw receipts and failed attempts retained

All paths below are local ignored evidence under
`.research/r4-84a2411b/evidence/`:

- `registry-r4-initial-tests.txt`: 31 expected failing tests before release CLIs
  existed; this is the initial red test-first run.
- `registry-r4-implemented-tests.txt`: 23 failures from running while a multi-file
  edit was still applying; build existed but later CLI files were not yet written.
  This run was not an acceptance candidate. Subsequent runs waited for edits.
- `registry-r4-focused-tests.txt`: 31 tests in 14.267s, OK, after all scripts existed.
- `full-suite-1.txt`: final expanded 39 release tests plus 141 existing tests;
  180 in 35.088s, OK.
- `cli-smoke-1.json`: exact command lists, exit statuses, stdout and stderr for
  validator, all four help commands and dry build.
- `smoke-manifest.json`: exact unsigned manifest from the smoke build.
- `candidate-1-sha256.json`: per-file source identity of the reviewed candidate.

Original failed/focused logs also remain at `/tmp/registry-r4-*.txt`; copying
receipts did not delete them. No private-key contents are in any receipt.
Editor diagnostics initially flagged unittest initialization annotations and
implicit relative imports; those were corrected. No separate linter or type
checker acceptance is claimed. `git diff --check` passed on tracked changes.

Before the broad suite, the host measured 1-minute load 12.53 on 28 cores,
42,203 MiB available memory, empty `/dev/shm`, and 24 MiB in `/run`. Admission was
green; no resource wait or foreign-process action was needed. Existing shared
dashboard state is outside writable roots; no reporting write was attempted.

## Initial independent review and remaining acceptance

Mechanical and deep initial reviews ran in fresh native contexts, requested
`gpt-6.1-sol` at `high` and `xhigh`. They share the filesystem and these receipts,
with separate owned scratch/report paths and no sibling-review reads before
their cold-read notes. Actual provider identity, tokens and queue latency are
unavailable; no cross-family independence is claimed. Initial findings and
repair dispositions and accepted focused reviews are recorded below.

The real public PEM is intentionally absent. Sign/verify clean refusals are
tested; the coordinator/Michel still owns first-key creation, public-key
distribution and source acceptance/checkpoint. Live GitHub CLI/API compatibility,
publication and real download acceptance are not established by fake-CLI tests.
Consumer integration and a real rotation drill remain separate work.

## Publication review findings and repairs

Both reviewers preserved an immutable cold-read note before sharing findings.
Their original reports remain at
[mechanical findings](../reviews/r4-mechanical/findings.md) and
[deep findings](../reviews/r4-deep/findings.md). The exact baseline is
`08d9fcb03744a188fe7f26b8305efe21ee8dc125`.

1. **Literal asset operands:** the coordinator noticed that `gh release create`
   interprets `filename#label` and glob patterns even with `shell=False`. The
   installed CLI's local help confirmed both syntaxes; the deep reviewer also
   checked primary installed manuals. A supported directory with `#` can select
   a different prefix file, failing publication or conditionally disclosing that
   file before post-upload checks. Disclosure requires an existing readable
   sensitive prefix file and publication permissions; a hostile contributor's
   control of Michel's output path was not established. This was supplied to
   both reviewers after their cold reads, not independent discovery twice.
   **Repair:** copy only the three authenticated public assets into private
   temporary staging, verify the copy, and upload fixed basenames from its cwd.
   Private keys are never copied. The literal `#`/glob regression now succeeds
   while the unrelated prefix file remains absent from uploaded assets.
2. **Destination binding:** the deep review independently found that inherited
   `GH_REPO`, host and configured default repository selection could contradict
   the guide's `origin` destination promise. **Repair:** parse a credential-free
   GitHub.com HTTPS/SSH origin; pin API hostname and owner/repository, and pass
   explicit `--repo` for creation/download. Unsupported/local hosts and embedded
   credentials fail before any `gh` call. This intentionally supports GitHub.com
   only, matching this repository's actual origin; enterprise hosts are refused.
3. **Malformed API fields:** mechanical review reproduced a null asset-name
   `TypeError`, with no realistic GitHub API attack path established. **Repair:**
   type-check asset names before sorting and tag references before creation;
   preserve subprocess failure purposes instead of relabeling them JSON errors.

Regression proof is retained at `publish-regression-red.txt`: 13 focused tests,
8 failures including subtest failures before the production repair. The repair
run is `publish-regression-green.txt`: 13 tests in 6.811s, OK. Both are in the
same local evidence directory. Tests emulate gh's operand grammar with a fake
executable; they do not execute real gh. The coordinator's sole real gh call was
read-only `gh release create --help`, without a network request.

The initial candidate-1 test/source drift while preparing regression tests is
explicitly noted by the deep reviewer; the 180-test receipt was never transferred
to those new bytes. No initial report, red log, or cold-read note was overwritten.

## Repaired candidate 2 acceptance checks

The exact 13 reviewed source/doc paths are pinned in
`candidate-2-sha256.json`. Their hashes were identical before and after all final
checks. That receipt and the files below live under
`.research/r4-84a2411b/evidence/`.

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests` | **187 tests in 31.158s; OK; exit 0** |
| `python3 scripts/validate.py` | **31 files checked; 0 problems; clean; exit 0** |
| Four release scripts' `--help` | All exit 0 |
| Dry build, `--registry 1 --out <temporary-new-directory>` | **34 files; 245760-byte tar; exit 0** |

The tar SHA-256 remains
`e7952e0e2b4f2fc3261a9e9800de8740c9e6f184c06a8cac783764cbdb2e1a8e`.
The exact manifest is `smoke-manifest-2.json`. `full-suite-2.txt` retains the raw
suite output; `full-suite-2-result.json` records argv, cwd, UTC start, elapsed
time, Python version and exit status. `candidate-2-checks.json` records the full
remaining command/output/exit matrix. There are 46 release tests and 141 existing
tests; all ran, without an OpenSSL skip on this host. Before the final run the
host measured 1-minute load 9.12/28 cores and 40,951 MiB available memory; no wait.

Focused mechanical/deep reviews accepted these repair bytes and receipts. Real-key
signing, network publication/download and consumer acceptance remain outside
this offline lane regardless of local review outcome.

## Final review dispositions and documentation-only candidate 3

| Reviewer | Exact scope | Final result |
| --- | --- | --- |
| Mechanical, requested `gpt-6.1-sol high` | Candidate-2 code/tests/docs, 13 matching hashes; independently mocked staged upload, malformed response and failure-purpose checks | Accepted repairs; no remaining blocker. [Fix review](../reviews/r4-mechanical/fix-review.md). |
| Deep, requested `gpt-6.1-sol xhigh` | Candidate-2 code/tests plus final candidate-3 recovery/auth-status documentation; all 13 hashes match; independent 18-case mocked origin parser check | Confirmed D1/D2 and diagnostic-doc follow-up fixed; no remaining blocker. [Fix review](../reviews/r4-deep/fix-review.md). |

The deep reviewer found one final low-priority manual-command gap: recovery
`gh release view` and auth-status instructions needed explicit destination flags
too. `docs/releasing.md` now pins both; it is the only changed path between
candidate 2 and candidate 3. `candidate-3-sha256.json` and
`candidate-3-docs-only.json` preserve that proof and the exact reason the 187-test
execution remains applicable. No Python, tests, build input, payload, CLI
behavior or format changed, so another broad suite would add no evidence.

The initial publication confidentiality finding is recorded locally in ignored
`security-finding-local.json`, including prerequisites, severity/likelihood,
source, baseline, due-now status, fixed source hash and red/green receipts. Its
state is repaired locally, awaiting coordinator source acceptance/checkpoint;
there is no invented fix commit. Original reports, inconclusive/failed runs and
both immutable cold-read notes remain intact. Reviewers reused the shared broad
receipt and ran their own focused checks, not independent copies of the suite.
Actual provider identity, tokens and queue latency remain unavailable. The line
carried one R4 batch; it never reached the three-batch ceiling.

No build/test/service or review lane remains running. No cleanup was performed;
small ignored receipts are retained and disposable temporary test trees/keys
were removed by their owning `TemporaryDirectory` contexts. Final Git status,
unchanged HEAD/version/data paths and retained evidence sizes are captured in
the final local state receipt.

## Close-out retention snapshot

Read-only `du -s -B1` measured allocated bytes at 02:34 UTC: coordinator evidence
`.research/r4-84a2411b` **167936 bytes**, mechanical review evidence
`.research/r4-mechanical-only` **36864 bytes**, and deep review evidence
`.research/r4-deep-only` **36864 bytes**. Total: **241664 allocated bytes** at that
snapshot, before the final state receipt. The R4 owner and named review lanes
retain these for source acceptance/checkpoint; historical failures and review
provenance cannot be recreated by a new green test run. Review retention at the
coordinator's source checkpoint. Original `/tmp/registry-r4-*.txt` evidence also
remains, with its separate accounting in the final state receipt.

Repository Python caches occupy 118784 bytes under `scripts/__pycache__` and
245760 under `tests/__pycache__`. Those shared pre-existing directories include
other tasks' modules; this lane does not claim their total as newly generated
data or remove them without established ownership/idleness. They regenerate
through the documented validator/tests; their next review belongs to the
coordinator's repository hygiene pass. Temporary clone/key/smoke directories
were run-owned disposable fixtures and removed by their contexts. No retained
large generated build tree or private key was created, no manual deletion was
performed, and no physical-space saving is claimed. At that check the working
filesystem had 40 GiB available, memory had 41639 MiB available, and memory-backed
filesystems were empty `/dev/shm` and 24 MiB `/run`; no resource intervention.
