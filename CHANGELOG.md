# Changelog

All notable changes are recorded here, following Keep a Changelog. Repository
versions follow Semantic Versioning. Numbered registry data releases are a
separate future sequence, `registry/<N>`.

## Unreleased

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
