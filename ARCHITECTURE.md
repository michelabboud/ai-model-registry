# Architecture

Dev mode: mvp

## Repository contract

The repository is a shared data source, not an application or launcher. Each data
object uses `schema_version: 1` and a closed `kind`. Objects reject unknown keys.
`providers/<id>.json` describes a provider and its HTTPS base endpoint, supported
protocols, and authentication mechanism. `models/<provider-id>.json` describes
1–500 models for an existing provider. `harnesses/<id>.json` describes a coding-CLI
integration using a bare command name and an explicitly supported adapter.
`media/` is reserved for Genie and is outside R1 validation.

Every provider, model entry, and harness has official source URLs and a verification
date. Dates and sources provide provenance, not automatic vendor verification. A
human contributor must check every value against an official vendor page. Examples
live only under tests and documentation and are explicitly invented.

## Validation boundary

Python 3.11+ and the standard library are the entire validator toolchain. No
network request, vendor API call, credential read, package install, or command
execution is part of data validation.

Before checking data, the loader checks the schemas' keyword vocabulary and
rejects unsupported keywords. It implements only the contract in
[ADR 0001](docs/adr/0001-standard-library-validator.md).

Supported keywords: `$schema`, `$id`, `title`, `description`, `type`, `properties`, `required`, `additionalProperties: false`, `enum`, `const`, `pattern`, `minLength`, `maxLength`, `minimum`, `maximum`, `items`, `minItems`, `maxItems`, `uniqueItems`, `not`, `$defs`, local `$ref`, `if`, and `then`.

1. The structural pass applies the published schemas: closed objects, required
   properties, types, lengths and counts, numeric limits, closed enums, patterns,
   local references, and the supported conditional and negation rules.
2. The semantic pass checks relationships across records and constraints that need
   parsing or cross-field comparison. Filenames must match IDs; model collections
   require their provider; model and environment names must be unique. Cache-write
   TTLs must be unique within each standard or long-context array, even when their
   prices differ. Each model
   file has exactly one GA probe and one GA default. The probe's known input price
   is no greater than every other GA model's known price. Status controls shutdown
   dates. Verification dates must be real and between 2024-01-01 and today in UTC.
   URLs are parsed, not trusted solely because they match a pattern. Version-match
   regexes must compile and contain a capture group. Harness protocol arrays
   must be empty if and only if their adapter is `detect_only`.

Input handling rejects files larger than 1 MiB, invalid UTF-8, duplicate JSON keys,
NaN/Infinity, and nesting deeper than 32. Data directories accept only their direct
JSON files and reserved `.gitkeep` markers. Stray files, subdirectories, and symlinks
are errors. JSON pointers identify errors; diagnostic value previews are limited to
80 characters. Text and JSON reports share the same result and exit status.

## Trust model

A hostile contributor or release attacker can change a price, model ID, endpoint,
or launcher binding. CI validates the candidate before it can be released. Closed
protocol, auth, tier, modality, adapter, and role enums prevent arbitrary extensions
from becoming executable launcher instructions.

A base URL permits HTTPS only, a real parsed host, no userinfo, query, or fragment,
and only `{region}` or `{project}` placeholders. Other source and documentation
URLs also require HTTPS and a host and forbid userinfo. The validator does not
contact endpoints or prove the vendor controls them; official-source review is
still required.

Environment entries carry `name`, `role`, and `note`, with no `value` field. Tokens,
API keys, and gateway URL values originate in the consuming app. A name denylist
blocks shell, loader, interpreter, Git, and SSH control variables. Bare command
syntax and environment restrictions are enforced in both the schemas and the
semantic pass, so changing a schema alone does not open that boundary. The closed
adapter enum lets consumers decide what integrations they implement. An icon is
an embedded-asset identifier that the app resolves; this registry ships no icons.

All token prices are USD per million tokens. `null` means unknown or not published;
zero means free. Cache reads and per-token writes remain distinct. Required
`cache_writes` is a bounded array (0–6) of closed TTL/price objects; TTL strings
match `^[1-9][0-9]{0,3}[mh]$`. Uniqueness by TTL is enforced semantically, since
JSON Schema `uniqueItems` alone would allow a repeated TTL with a different price.
An empty array means no per-token write rate is published. Optional
`cache_storage_per_mtok_hour` uses USD per million cached tokens per hour and
never substitutes for a token-write rate. Both standard and long-context objects
use this shape; the old `cache_write_5m` and `cache_write_1h` keys are rejected.
[ADR 0003](docs/adr/0003-cache-pricing-shape.md) records the pre-release change;
`schema_version` remains 1. Long-context prices carry an explicit token threshold.
Long-context prices apply when the prompt's input tokens are strictly greater than `threshold_tokens`.
Normalize over/above/> N and short-context <= N to N; normalize >= N or "N or more"
to N - 1. K means 1,000 tokens unless the source defines it otherwise.
Clients
must not silently coerce `null` to zero, infer unsupported cache prices, or treat a
missing vendor fact as free service.

Harness `protocols` is required: zero to four unique entries from
`anthropic_messages`, `openai_chat`, `openai_responses`, `gemini_generate`, and
`gemini_interactions`. Empty means detection only and is permitted exactly when
`adapter` is `detect_only`; the semantic pass rejects both empty configurable
adapters and nonempty detection-only records. An adapter describes the config
mechanism, not the wire format: `env_generic` and `config_snippet` span several
protocols. Consumers select an ingress from the explicit protocol list. Unknown
custom-endpoint protocols stay out of the list and in the source audit/backlog.
See [ADR 0004](docs/adr/0004-harness-protocols-field.md), which replaces R2's
optional harness field before release while keeping `schema_version: 1`.

Provider protocols keep their broader closed vocabulary and existing bounds,
including cloud-native APIs. Both vocabularies include `gemini_generate` and
`gemini_interactions` for distinct Gemini APIs. Endpoint-specific model
restrictions remain in notes; there is no per-model protocol override in schema v1.

## Proposal-only model watch

The R5 watch is a separate maintenance command, `scripts/model_watch.py`; it
does not run during offline data validation. Its fixed `VENDORS` table lists
OpenAI, Anthropic, Gemini, xAI, DeepSeek, and public OpenRouter endpoints,
authentication headers, pagination, and non-text family exclusions. Gemini must
support `generateContent`; OpenRouter is limited to six named vendor prefixes
and excludes `:batch` routes. Z.ai, Vertex, and Bedrock listing integrations are
outside R5 because no verified key-scoped endpoint was supplied.

The script compares listings with `models/<provider>.json`. New admitted IDs and
missing active (`ga`/`preview`) records become only `TO VERIFY` Markdown
worksheets under `candidates/`, citing the provider's `docs_url` and existing
model/pricing sources. An omission is a prompt to check vendor deprecation notes,
not proof of retirement. Deprecated records do not become missing proposals.
Neither provider/model records nor their schema contracts are changed by a
watch run.

The CI boundary is two jobs. `watch` has vendor keys and a read-only token;
`pull-request` has a write token but no vendor keys or vendor-facing code. Only
the six known regular worksheet filenames are admitted from the artifact.
`candidates/` remains ignored on `main` and named worksheets are force-added only
on `model-watch/auto`. One PR is updated in place; branch rewrites use
`--force-with-lease` against the observed remote SHA, and human commits prevent
automation from overwriting or closing the branch's PR. Skipped vendors retain
their existing branch worksheets as possibly stale, including successful runs
with no fresh changes. Closure requires a complete no-difference check.

Keys are optional environment inputs, stripped of surrounding whitespace and
restricted to visible ASCII; invalid-key errors name only the secret. Requests
use header authentication and refuse redirects. Untrusted IDs are admitted by a
bounded grammar or dropped and counted without being echoed. A listing exceeding
4 MiB cumulatively, 2,000 entries, or 10 pages fails rather than truncating.
Unexpected shapes fail the affected vendor and the run. Anthropic, DeepSeek,
and xAI shapes remain **UNVERIFIED** until the coordinator checks a live run.

The workflow triggers only on the weekly schedule or manual dispatch, never on
`pull_request` or `pull_request_target`. No signing key is in CI. The watch never
signs, creates a release, or pushes `main`; human verification and R4's local
release procedure remain separate. See [the guide](docs/model-watch.md) for the
full threat sketch and [ADR 0005](docs/adr/0005-model-watch.md) for the design.

## Signed numbered releases

R4 supplies four local Python CLIs and `scripts/release_common.py`, sharing the
format and verification boundary. `registry/<N>` is a positive consecutive data
release sequence, independent of source `VERSION`. Every release has exactly
`registry.tar`, `manifest.json`, and `manifest.json.sig` as uploaded assets.

The build runs the existing validator first and refuses Git changes under
`providers/`, `models/`, `harnesses/`, and `schema/`. Only their JSON files are
packaged in sorted relative-path order. Python `tarfile` writes POSIX ustar with
regular files only, mode 0644, zero mtime/uid/gid, empty uname/gname, no directory
entries, and canonical zero padding. Source metadata cannot change archive bytes.
The output directory must be new or empty, outside the data paths and not itself
a symlink. Exclusive file creation preserves any competing existing artifact.

Canonical manifest JSON uses sorted keys, compact separators, UTF-8 without
ASCII escaping, and a trailing newline. Its closed format 1 records `registry`,
UTC `created` date, source `repo_version`, `min_client` with The Operator 0.17.0,
per-file SHA-256/byte lengths, and complete-tar SHA-256/byte length. The manifest,
signature and tar are not recursively included in `files`.

OpenSSL >= 3.0 signs the exact manifest bytes with Ed25519; the detached signature
is exactly 64 raw bytes. All subprocesses use argument lists and `shell=False`.
Python inspects private-key metadata only: regular file, current-user ownership,
mode exactly 0600, no final symlink, and resolved location outside the repository.
Only OpenSSL reads the private key. The signer checks unsigned artifacts, signs
into a disposable signature path, immediately verifies against the repository's
public PEM, then exclusively creates the final signature. It never overwrites an
existing signature or prints OpenSSL error output. Signing never runs in CI.

Verification reads manifest bytes once and checks the trusted signature over
that private snapshot before parsing the same bytes as JSON, then checks its
closed/canonical shape, tar hash/size, each member's hash/size, exact sorted file
membership, safe relative JSON paths, canonical ustar headers and all padding.
Absolute paths, `..`, backslashes/drive paths, links, devices, duplicate members,
hidden extension headers and trailing content are rejected. The opened archive's
size must match the signed byte count before hashing starts. No extraction occurs.
Clients **MUST** verify the signature before parsing manifest JSON and all signed
hashes and byte lengths before parsing registry data. They **MUST** validate the
authenticated data, enforce minimum-client versions, and refuse downgrades using
persisted registry-number state. Before activation, clients **MUST** show the diff
and require a person's explicit confirmation. Endpoint changes (`base_url`, auth,
protocols) and launcher changes (`harnesses/`) **MUST** be shown separately from
each other and from other data changes, and **MUST NOT** be applied automatically.
Clients own safe staging and transactional activation. An authentic signature
proves publisher identity and unchanged bytes,
not vendor fact accuracy or freshness.

Only publication invokes `gh`. After verification it queries all release pages,
requires highest `registry/N` plus one, and refuses an existing target tag. It
pins a credential-free GitHub.com HTTPS/SSH `origin` explicitly for every API,
create and download operation, ignoring gh's inherited host/repository defaults.
Before creation, it copies only the three public assets to a private temporary
directory and re-verifies them. Fixed basename upload operands from that cwd
prevent gh's `filename#label` or glob parsing from changing literal file binding.
It creates the remote tag/release against current local HEAD with those assets,
checks the remote asset list, downloads them and byte-compares staged originals.
It never moves/deletes tags or releases, including on partial failure. A single
maintainer serializes publication; CLI preflight and creation are not atomic.
The target source commit must already exist at the destination. Destination,
failure recovery and operator responsibilities are documented in
[releasing.md](docs/releasing.md).

No real key or release exists yet. Validation/build tests do not require one.
Sign/verify refuse cleanly while `keys/registry-signing-key.pub.pem` is absent.
[The key history](keys/README.md) will carry current and historical public PEMs,
raw 32-byte public keys as base64, and registry-number ranges. Key creation,
encrypted offline backup, restore checks and rotation/client sequencing are
manual procedures. See [ADR 0006](docs/adr/0006-signing-with-openssl.md).
