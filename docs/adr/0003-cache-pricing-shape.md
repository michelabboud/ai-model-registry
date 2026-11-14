# 0003 — Cache prices by TTL and hourly storage

## Context

Vendors sell different cache time-to-live (TTL) periods and storage by the hour.
Anthropic publishes 5-minute and 1-hour cache-write rates; OpenAI publishes
30-minute and 12-hour writes. Gemini publishes hourly cache storage separately
from token processing. Two fixed cache-write fields cannot describe these offers
without changing their meaning. No registry release exists yet.

## Decision

Keep `schema_version: 1` and replace `cache_write_5m` and `cache_write_1h` in
both `pricing` and `long_context` with required `cache_writes`. It is an array of
zero to six closed `{ "ttl": "5m", "price": 1.25 }` objects. TTLs match
`^[1-9][0-9]{0,3}[mh]$` and must be unique within each array. The validator checks
uniqueness by TTL, including entries with different prices. An empty array means
no per-token cache-write price is published. A null entry price means the TTL is
known but its price is unknown; zero means explicitly free.

Add optional `cache_storage_per_mtok_hour` to both price objects, a nonnegative
number or null, denominated in USD per million cached tokens per hour. It is
independent of per-token cache-write prices. Omission or null communicates no
published storage rate; neither means free. Token prices remain USD per million
tokens. Long-context thresholds retain their existing meaning.

## Alternatives rejected

Fixed fields per TTL were rejected: they break on every new vendor TTL and
encourage mapping unrelated durations into existing fields. A generic unbounded
price map was rejected because a bounded, closed object keeps validation and
consumer handling explicit. Encoding hourly storage as a cache write was rejected
because its units and billing trigger differ.

## Consequences

Consumers must iterate cache writes and preserve TTLs, distinguish storage from
token processing, and retain unknown prices without coercing them to zero.
Schemas reject the old field names; fixtures, documentation, and validation tests
move together before the first release. The six-entry bound permits the sourced
offers while bounding data size. The chosen TTL spelling is the identity: `60m`
and `1h` are different strings; contributors should use the vendor's duration.

## Status

Accepted 2026-11-14 under the R2 resumption decisions; no compatibility migration
or released payload is involved.
