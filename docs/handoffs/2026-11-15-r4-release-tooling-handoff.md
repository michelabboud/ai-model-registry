# R4 release-tooling handoff

Date: 2026-11-15. Dev mode: mvp. Repo:
`/home/michel/projects/ai-model-registry`, branch `main`, unchanged HEAD
`08d9fcb03744a188fe7f26b8305efe21ee8dc125`, unchanged `VERSION` `0.4.0`.
All R4 changes remain uncommitted, as explicitly requested. No network, commit,
tag, push, real key or publication was performed. Only temporary throwaway test
keys were generated. The real public PEM is intentionally absent.

## Verified implementation

- Four release CLIs plus `release_common.py`: validator-first clean-data build,
  deterministic ustar/canonical manifest, strict external-key OpenSSL signing,
  signature-first safe reference verification, and verified consecutive GitHub
  publication with exact assets and download comparison.
- Publication stages only the three verified public assets and passes fixed
  upload basenames, preserving literal `#`/glob directory names. Every API,
  create and download operation explicitly pins GitHub.com `origin`; inherited
  gh host/repository defaults cannot redirect it. Non-GitHub.com/local origins
  are refused. It never moves/deletes/reuses tags or releases.
- Offline tests cover deterministic bytes, metadata, key restrictions, missing
  public key, unsafe/tampered archives/manifests and mocked publication failures.
  Private PEMs are ignored at root and under `keys/`; public PEMs are admissible.
- [The release ceremony](../releasing.md),
  [key creation/backup/rotation](../../scripts/new_signing_key.md),
  [key history](../../keys/README.md),
  [ADR 0006](../adr/0006-signing-with-openssl.md), README, architecture, changelog
  and project records are updated. Rotation drill and transparency-log idea are
  explicitly retained in the backlog.

## Exact local checks

- `python3 scripts/validate.py`: **31 files; 0 problems; clean; exit 0**.
- `python3 -m unittest discover -s tests`: **187 tests in 31.158s; OK; exit 0**.
- Each release CLI's `--help`: exit 0.
- Dry unsigned build with clean data paths: **34 files; tar 245760 bytes**;
  SHA-256 `e7952e0e2b4f2fc3261a9e9800de8740c9e6f184c06a8cac783764cbdb2e1a8e`.
- Source/doc hashes identical before/after candidate-2 checks; tracked
  `git diff --check` clean. No data or schema changes.

Receipts, failed attempts, source identities and manifests are in
`.research/r4-84a2411b/evidence/`, summarized by
[the validation report](../reports/2026-11-15-r4-validation.md). The original
180-test candidate and initial review failures remain preserved.

## Reviews and next boundary

Initial mechanical/deep reviews confirmed publication operand/destination
defects and an informational malformed-response edge. All are repaired with
failing-then-passing focused tests; candidate 2 has the 187-test acceptance run.
Focused repair reviews accepted the repaired code with no remaining blocker.
Mechanical acceptance covers candidate 2; deep acceptance covers that identical
code/test set plus candidate-3 manual recovery/auth-status documentation. Only
`docs/releasing.md` changed after the broad checks, with a retained hash/scope
justification. See the [mechanical fix review](../reviews/r4-mechanical/fix-review.md)
and [deep fix review](../reviews/r4-deep/fix-review.md). They requested
`gpt-6.1-sol` at `high` and `xhigh`, in fresh same-family contexts on the shared
filesystem. Actual provider identity/tokens/queue times are unavailable. Shared
receipts are one execution, not two independent full-suite runs. No cross-family
or process/filesystem isolation is claimed.

The coordinator next accepts the source and performs any source checkpoint
under its own authority. Michel's first real key/public PEM plus compiled-client
key distribution and actual publication remain a separate manual ceremony.
Live GitHub CLI/API behavior and client integration are not proven by fake-gh
tests. A real key is not a blocker to this tooling handback.

The shared dashboard at
`/home/michel/.local/state/build-task-dashboard/tasks.html` was located but its
state lies outside writable roots. No alternative board bypass or write was
attempted. No build/test/service process or review lane is left running. Public
receipts and failed attempts remain in the ignored evidence directories; no
cleanup or source checkpoint was performed. The local security-finding record
is `.research/r4-84a2411b/evidence/security-finding-local.json` (relative to the
repository; source acceptance/checkpoint remains external, no fix commit claimed).
