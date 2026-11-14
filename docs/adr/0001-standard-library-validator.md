# 0001: A standard-library-only validator

Date: 2026-11-14

## Context

This is a public data repository. Contributors and CI need to validate it offline
with Python 3.11 or newer. The public JSON Schemas must not describe constraints
that the repository's validator silently ignores. A malicious data edit can affect
downstream endpoints, prices, and coding-CLI launcher configuration.

## Decision

Use Python's standard library only. Implement the exact JSON Schema draft 2020-12
keyword subset used by the three published schemas, followed by a semantic pass
for file relationships, dates, parsed URLs, model selection, and launcher rules.
Refuse to load a schema with an unsupported keyword. Treat the supported keyword
subset as a contract: adding a keyword requires validator support and tests in the
same change.

Patterns use Python `re.fullmatch`; schema patterns are anchored with `^` and `$`
so ordinary JSON Schema validators agree for the grammar used here. The validator
does not claim to implement the entire JSON Schema specification.

## Alternatives rejected

- The `jsonschema` package: a third-party dependency to vet and pin, with an
  additional PyPI installation step in CI. The required vocabulary is small enough
  to implement and test without it.
- A Rust validator: a compilation toolchain and dependency/build overhead are
  heavier than this data repository needs.

## Consequences

Validation works without downloading packages. The maintainers own correctness of
the keyword interpreter and its tests. The loader guard prevents schema edits from
quietly promising more validation than the implementation performs. Semantic
constraints are documented separately; consumers that use a general JSON Schema
engine still need equivalent semantic checks.

## Status

Accepted.
