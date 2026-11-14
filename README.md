# ai-model-registry

One public source of AI provider, model, price, tier, and coding-CLI integration
data. [The Operator](https://github.com/michelabboud/the-operator), a Rust LLM
gateway, is the first consumer; Genie is a later consumer. This repository contains
data, schemas, validation tooling, and documentation, with no application runtime,
credentials, or keys.

**No release exists yet.** R1 supplies the contracts and validation infrastructure;
provider, model, and harness directories are intentionally empty pending later data tasks.

## Data directories

| Directory | Contents |
| --- | --- |
| `providers/` | One provider object per `<id>.json`: endpoint, protocols, and authentication role. |
| `models/` | One model collection per `<provider-id>.json`: status, tier, capabilities, and USD-per-million-token prices, including prompt-cache prices. |
| `harnesses/` | One coding-CLI integration per `<id>.json`: command, adapter, and environment roles. |
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
        "cache_write_5m": null,
        "cache_write_1h": null,
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
replace an unknown price with zero. All prices use USD per million tokens.
`long_context`, when present, provides a threshold and the same five token prices.
A deprecated model requires a `shutdown` date; other statuses forbid that field.
Each model file has exactly one GA probe and one GA default. The probe must have a
known input price no greater than any other GA model's known input price.

Harnesses declare roles, never environment values. The consuming application
supplies API keys, tokens, gateway endpoints, and other local values. Commands are
bare names, adapters come from a closed enum, and dangerous environment names are
rejected in both schemas and the semantic validator. Icons are embedded-asset IDs
resolved by the app, not files shipped by the registry.

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
