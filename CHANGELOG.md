# Changelog

All notable changes are recorded here, following Keep a Changelog. Repository
versions follow Semantic Versioning. Numbered registry data releases are a
separate future sequence, `registry/<N>`.

## Unreleased

## [0.5.1] - 2026-11-15

### Fixed

- Accept model-watch downloads containing only `pr-body.md` when no worksheets
  remain; retain directory/symlink checks and known worksheet-name admission.
- Protect the validator's 1 MiB cap with otherwise valid oversized provider JSON,
  the size-specific diagnostic, and a passing file just under the limit.
- Require clients to verify signatures/hashes before parsing, refuse downgrades,
  show a diff and obtain explicit human confirmation before activation; display
  endpoint and launcher changes separately and never apply them automatically.
- Verify the exact manifest bytes read for parsing using a private snapshot, and
  reject an opened archive's signed-size mismatch before hashing it.
- Correct the current progress summary to 0.5.0, 177 models and 13 harnesses while
  preserving historical receipts.

## [0.5.0] - 2026-11-15

### Added

- R4 deterministic POSIX ustar builder and canonical hash/size manifest;
  validator-first builds refuse dirty data paths and nonempty output directories.
- Local OpenSSL >= 3.0 Ed25519 signing with strict external private-key metadata
  checks, immediate trusted-key verification, and no private-key reads in Python.
- Reference release verifier checking signatures before manifest parsing, exact
  hashes/sizes and safe canonical archive membership without extraction.
- Verified consecutive GitHub publication with exact uploaded assets and download
  byte comparison; offline fake-`gh` tests never publish or contact GitHub.
- Release/key ceremonies, backup/rotation instructions, deferred public-key
  directory, signing-backend ADR 0006, and private-PEM/dist ignore rules.
  No real key, numbered release, version bump, commit, tag or push is part of R4.

### Fixed

- Preserve literal release-directory paths through GitHub CLI's asset parser by
  staging verified public assets and uploading fixed basenames; `#`/glob
  characters cannot redirect uploads to another file.
- Pin all publication API/create/download operations to GitHub.com `origin`
  instead of inherited gh repository/host defaults; reject malformed response
  asset names and tag references without a traceback.

## [0.4.0] - 2026-11-15

### Added

- R5 proposal-only weekly text-model watch for OpenAI, Anthropic, Gemini, xAI,
  DeepSeek, and public OpenRouter listings, with explicit non-text exclusions,
  bounded pagination, hostile-ID handling, and `TO VERIFY` worksheets.
- Two-job model-watch workflow separating vendor keys from repository write
  access, one lease-protected watch branch/PR, known worksheet-name admission,
  and possibly-stale carry-forward for skipped vendors.
- Offline invented fixtures and mocked transport/workflow tests; key-name-only
  environment documentation, human source-verification guide, and ADR 0005.
  Anthropic, DeepSeek, and xAI endpoint shapes remain UNVERIFIED pending a live
  coordinator check. R5 does not sign or publish registry data.

### Fixed

- Refuse credential values reflected by a listing into otherwise valid model
  IDs or pagination cursors, before artifacts or query URLs can disclose them.
- Reconcile an existing watch branch and PR body when a partial run resolves
  its last worksheet; repeated incomplete runs do not add empty commits.

## [0.3.0] - 2026-11-15

### Added

- R3 coding-CLI records for Claude Code, Codex, OpenCode v1/v2, Aider, Copilot,
  OpenHands, OpenClaw, Hermes Agent, Antigravity, Grok Build, Muse Code and Cursor,
  with dated research sources and explicit detection-only/unknown limitations.
- Required harness wire protocols, with a unique zero-to-four-entry array and
  semantic enforcement that it is empty exactly for `detect_only`; fixtures,
  regression tests and ADR 0004 describe the pre-release contract change.
- App-neutral icon ID inventory and per-CLI field/source/omission audit; the
  registry ships no image assets. Unverified enrichment remains in the backlog.

## [0.2.0] - 2026-11-15

### Added

- R2 seed records for nine providers and their text models, with official source
  URLs, verification dates, price/limit unknowns, family tiers, probes, defaults,
  and explicit endpoint/pricing limitations.
- Per-TTL cache-write arrays and optional hourly cache-storage rates in standard
  and long-context pricing, with semantic TTL uniqueness checks and regression
  coverage; the old fixed cache-write keys are rejected before the first release.
- Gemini Interactions in the closed provider protocol enum and optional harness
  protocol declarations using the same vocabulary; schema version remains 1.
- Cache-pricing ADR and a full source, exclusion, null, and deviation report.

## [0.1.0] - 2026-11-14

### Added

- R1 repository skeleton with reserved provider, model, harness, and media paths.
- JSON Schema draft 2020-12 contracts for providers, model collections, and harnesses.
- Dependency-free Python validator with guarded schema vocabulary, semantic checks,
  strict JSON input handling, and text/JSON diagnostics.
- Invented positive and negative fixtures and unittest coverage for the data contract.
- Read-only CI validation with a pinned checkout action and the runner's system Python.
- Contributor, security, architecture, plan, handoff, and accepted decision records.

No provider data or numbered registry release is published by R1.
