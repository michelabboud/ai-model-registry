# ai-model-registry

One public source of AI provider, model, price, tier, and coding-CLI integration
data. [The Operator](https://github.com/michelabboud/the-operator), a Rust LLM
gateway, is the first consumer; Genie is a later consumer. This repository contains
data, schemas, validation tooling, and documentation, with no application runtime,
credentials, or keys.

**No release exists yet.** Provider and text-model seed data is verified against
official pages archived on 2026-11-14. Thirteen coding-CLI harness records use the
coordinator's official-source and installed-binary research from that date. See the
[source and omission report](docs/reports/2026-11-14-seed-data-sources.md) for the
provider inventory, unknown values, endpoint restrictions, and pricing conditions;
the [harness report](docs/reports/2026-11-14-harness-records.md) records CLI fields,
sources and unverified omissions. These are archived research claims, not live
vendor or endpoint checks performed by validation.

## Data directories

| Directory | Contents |
| --- | --- |
| `providers/` | One provider object per `<id>.json`: endpoint, protocols, and authentication role. |
| `models/` | One model collection per `<provider-id>.json`: status, tier, capabilities, and USD-per-million-token prices, including prompt-cache prices. |
| `harnesses/` | One coding-CLI integration per `<id>.json`: command, adapter, required wire protocols, and environment roles. |
| `media/` | Reserved for Genie. Ignored by this validator; no media contract is defined by R1. |

Every real value must be verified against an official vendor page and dated.
Every provider, model entry, and harness carries `verified` and `sources`.
`verified` is the date the values were checked, not the release date. Example
records below and in `tests/fixtures/` are invented test data, not verified vendor
claims. They must never be copied into the published data as vendor facts.

## File examples

These are complete invented examples. Save them only in a fixture tree, with the
shown filenames. `schema_version` versions the data contract independently of
`VERSION`, which versions repository development.

`providers/example-provider.json`:

```json
{
  "schema_version": 1,
  "kind": "provider",
  "id": "example-provider",
  "display_name": "Example Provider (invented)",
  "base_url": "https://api.example.com/v1",
  "protocols": ["openai_chat"],
  "auth": "bearer",
  "docs_url": "https://example.com/docs",
  "verified": "2026-11-14",
  "sources": ["https://example.com/docs"],
  "note": "Invented example only; not vendor data."
}
```

`models/example-provider.json`:

```json
{
  "schema_version": 1,
  "kind": "models",
  "provider": "example-provider",
  "models": [
    {
      "id": "example-small",
      "display_name": "Example Small (invented)",
      "status": "ga",
      "tier": "low",
      "context_window": 8192,
      "max_output_tokens": 2048,
      "input_modalities": ["text"],
      "probe": true,
      "default": true,
      "pricing": {
        "input": 0.1,
        "output": 0.2,
        "cache_read": null,
        "cache_writes": [],
        "batch_discount_percent": null
      },
      "verified": "2026-11-14",
      "sources": ["https://example.com/pricing"],
      "note": "Invented prices for illustration only."
    }
  ]
}
```

`harnesses/example-cli.json`:

```json
{
  "schema_version": 1,
  "kind": "harness",
  "id": "example-cli",
  "display_name": "Example CLI (invented)",
  "command": "example-cli",
  "aliases": [],
  "adapter": "env_generic",
  "protocols": ["openai_chat"],
  "config_style": null,
  "env": [
    {"name": "EXAMPLE_API_KEY", "role": "api_key", "note": "Supplied by the consuming app."}
  ],
  "profile_flag": null,
  "model_flag": "--model",
  "version_probe": ["--version"],
  "version_match": {"major_pattern": "^([0-9]+)\\..*$"},
  "docs_url": "https://example.com/cli",
  "icon": "example-cli",
  "verified": "2026-11-14",
  "sources": ["https://example.com/cli"],
  "note": "Invented integration; the registry supplies no executable or icon."
}
```

A `null` price means not published or unknown. A numeric zero means free; never
replace an unknown price with zero. Token prices use USD per million tokens.
Required `cache_writes` contains zero to six `{ "ttl": "5m", "price": 1.25 }`
objects. TTLs match `^[1-9][0-9]{0,3}[mh]$` and are unique within each array.
An empty array means no per-token cache-write price was published; a null price
means a known TTL with an unknown rate. Preserve the vendor's duration: Anthropic
5m/1h and OpenAI 30m/12h are different offers. The old fixed cache-write fields
are rejected. Optional `cache_storage_per_mtok_hour` is USD per million cached
tokens per hour, separate from cache access or writes. Omission or null means
unknown; zero means explicitly free.

`batch_discount_percent` summarizes a published batch input/output discount.
It does not establish batch availability or a discount for every cache category,
storage tariff, or context band. Read the model notes: some batch cache prices
remain Standard, are rounded, or are unpublished. A null discount may also flag
an inconsistent batch tariff that cannot be summarized by one percentage.

`long_context`, when present, provides `threshold_tokens` and the same input,
output, cache-read, cache-write array, and optional hourly storage prices.
Long-context prices apply when the prompt's input tokens are strictly greater than `threshold_tokens`.
Source thresholds are normalized to this strict comparison: over/above/> N and
short-context <= N become N; >= N or "N or more" become N - 1.
K means 1,000 tokens unless the source defines it otherwise.
Long-context pricing does not carry a second batch discount. Notes retain other
vendor conditions that schema v1 cannot express. See
[the cache-pricing decision](docs/adr/0003-cache-pricing-shape.md).
A deprecated model requires a `shutdown` date; other statuses forbid that field.
Each model file has exactly one GA probe and one GA default. The probe must have a
known input price no greater than any other GA model's known input price.

Harnesses declare roles, never environment values. The consuming application
supplies API keys, tokens, gateway endpoints, and other local values.
`config_style` is a short format label (`toml`, `json`, `jsonc`, `yaml`, `json5`,
`env`) or null; notes retain prerequisites that span formats. Commands are
bare names, adapters come from a closed enum, and dangerous environment names are
rejected in both schemas and the semantic validator. Icons are embedded-asset IDs
resolved by the app, not files shipped by the registry.

Providers declare supported `protocols`. Harnesses require a unique `protocols`
array with zero to four entries from `anthropic_messages`, `openai_chat`,
`openai_responses`, `gemini_generate`, and `gemini_interactions`. The array is empty
if and only if `adapter` is `detect_only`; every configurable adapter needs at
least one verified custom-endpoint protocol. Adapters describe configuration,
so consumers must use `protocols` to select the gateway ingress instead of
inferring it from `env_generic` or `config_snippet`. Detection-only records do not
establish gateway compatibility. See [ADR 0004](docs/adr/0004-harness-protocols-field.md).

`gemini_generate` describes generateContent; `gemini_interactions` describes the
separate Interactions API. Provider protocols retain their broader vocabulary,
including cloud-native APIs. A provider-level protocol list is not a claim that
every model supports every endpoint; read model notes for exceptions, including
runtime-only Bedrock models.

## Icons

The registry never ships images. Apps map these app-neutral `icon` IDs to their
own embedded assets:

`claude-code`, `openai`, `opencode`, `aider`, `github-copilot`, `openhands`,
`openclaw`, `hermes-agent`, `antigravity`, `xai`, `meta`, `cursor`.

An ID identifies an application or vendor; it is not an asset URL, a brand-use
license, or a claim that a similarly named icon library entry is the same brand.

## Tiers

Tiers describe vendor family positioning, not measured quality or interchangeable
capability. `low` is the small/fast family (Haiku, Luna, Flash, Lite, Mini, Nano,
and `-flash` variants); `high` is the flagship family (Opus, Fable, Astra, Pro,
and the vendor's top Grok); `medium` is the rest. Small/fast markers take priority
over a `pro` suffix on that small family. OpenRouter entries inherit their matched
vendor model's tier. Neither price nor preview status alone determines tier.

## Validate locally

Use Python 3.11 or newer. No package installation or network access is needed.

```sh
python3 scripts/validate.py
python3 scripts/validate.py --root tests/fixtures/valid
python3 scripts/validate.py --json
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/validate.py
```

`--root DIR` selects the data tree to check; the script uses its repository's
schemas. An empty data tree validates clean. Validation reads only direct JSON
files in `providers/`, `models/`, and `harnesses/`; `.gitkeep` is the reserved empty
directory marker. Other files, nested directories, and symlinks there are errors.
`media/` is ignored. Errors include a file and JSON pointer. Exit codes are 0 for a
clean tree, 1 for validation problems, and 2 for command-line usage errors.

The schemas use a guarded subset of JSON Schema draft 2020-12; they are not a
claim that the Python validator implements the complete standard. See
[the architecture](ARCHITECTURE.md) and [ADR 0001](docs/adr/0001-standard-library-validator.md).

## Weekly model watch

The scheduled [model-watch workflow](.github/workflows/model-watch.yml) checks
OpenAI, Anthropic, Gemini, xAI, DeepSeek, and public OpenRouter listings on
Mondays at 06:23 UTC or manual dispatch. It proposes only ignored
`candidates/<provider>.md` worksheets on `model-watch/auto`, with one updated
pull request and every proposed field marked `TO VERIFY`. A missing listing
entry is a prompt to investigate, never proof that a model retired.

Vendor keys stay in a read-only job; the PR job has write access but no keys or
vendor-facing code. The watch never edits provider/model records, signs, releases,
or pushes `main`. Missing secrets skip that vendor and preserve its prior
worksheet as possibly stale. See [the setup and human verification guide](docs/model-watch.md)
for the five key names, text-family filters, strict listing limits, and threat
sketch. Anthropic, DeepSeek, and xAI endpoint shapes remain **UNVERIFIED** until
the coordinator's first live run. `python3 scripts/model_watch.py --help` and the
fixture tests work offline; running a real watch contacts the vendors.

## Releases and licensing

Releases are **not yet published**. R4 will implement numbered `registry/<N>`
releases containing `manifest.json` with SHA-256 payload hashes,
`manifest.json.sig` with an Ed25519 signature over the exact manifest bytes, and
`registry.tar`. Clients must verify the signature and every payload hash before
parsing registry data. Signing never runs in CI. Key distribution and the exact
release payload are R4 work; R1 does not provide a trust key or release tooling.

This registry is dedicated under **CC0-1.0**; see [LICENSE](LICENSE). Contributions
must follow [CONTRIBUTING.md](CONTRIBUTING.md). Report security problems through
[SECURITY.md](SECURITY.md). The current task state is in [PROGRESS.md](PROGRESS.md),
the approved task index in [PLAN.md](PLAN.md), and the current seam in
[HANDOFF.md](HANDOFF.md).
