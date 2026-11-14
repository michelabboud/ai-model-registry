# 0002: JSON data, CC0, and signed numbered releases

Date: 2026-11-14

## Context

The Operator, a Rust LLM gateway, is the first consumer. Genie and other
applications should be able to consume the same provider, model, price, tier, and
coding-CLI integration records. Genie's existing registry uses TOML; this shared
registry has a different requirement: easy interchange across applications and
languages without requiring a TOML parser.

Registry updates can alter endpoints and launcher configuration. Release
authenticity and exact file integrity must be checked before consumers parse data.

## Decision

Store records as JSON with JSON Schema draft 2020-12 contracts. Michel chose the
CC0-1.0 dedication on 2026-11-14 for this public registry; the coordinator-provided
`LICENSE` is authoritative and remains unchanged.

The release design uses monotonically numbered `registry/<N>` releases containing
`manifest.json`, `manifest.json.sig`, and `registry.tar`. The manifest records
SHA-256 hashes of the released payload files. The detached signature is Ed25519
over the exact manifest bytes. Clients verify the signature and hashes before
parsing payload data. Manifest and archive details, trust-key distribution, and
publication are R4 work; no release exists yet. Signing never runs in CI.

## Alternatives rejected

- TOML: suitable for Genie's local registry but adds a parser requirement for
  otherwise JSON-capable consumers of this shared source.
- An unsigned moving branch or archive as the client trust anchor: it cannot
  establish the approved publisher and exact released payload independently of
  the transport and hosting account.
- Restrictive data licensing: would hinder reuse across independent consumers;
  CC0 permits broad reuse without per-application licensing arrangements.

## Consequences

Applications can use widely available JSON readers. They must preserve the
distinction between unknown (`null`) and free (`0`) prices, supply environment
values locally, and perform semantic validation in addition to parsing.
Signatures authenticate a release; they do not establish that vendor facts are
correct or current. Official-source review and dates remain necessary. R4 must
define the canonical release payload and exclude self-referential manifest,
signature, or archive hashing before implementing the release format.

## Status

Accepted.
