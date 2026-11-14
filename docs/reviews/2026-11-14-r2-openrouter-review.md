# R2 openrouter review and repair adjudication — 2026-11-14

Dev mode: mvp. No release or live API qualification. Fresh-context native same-family reviewer; source snapshots were content-hashed because the lane forbids commits. Runtime provider identity, token use and independently measured queue latency are unavailable.

Requested configuration: gpt-6.1-sol / high.

Coordinator disposition: confirmed actionable finding repaired and independently rechecked. Source limitations remain documented in the seed report/backlog; they are not fabricated as resolved. All final validation input hashes match the reviewed original and repair snapshots.

## Original independent report (preserved)

# CONFIRMED — OR-01: Older DeepSeek V4 Pro snapshot included outside the allowed matched subset

Severity: medium; disposition: correct before accepting this data batch.

Location: `models/openrouter.json:2367`, entry `deepseek/deepseek-v4-pro` (whole model entry / identity correspondence). The entry is named `DeepSeek: DeepSeek V4 Pro 0423` and has input/output prices 0.9/1.5 USD per million tokens. The matching direct-vendor entry at `models/deepseek.json:34` is named `DeepSeek V4 Pro 0813`.

Official archived evidence:

- `sources/openrouter-models.json`, JSON pointer `/data/234` (ID `deepseek/deepseek-v4-pro`): `"name": "DeepSeek: DeepSeek V4 Pro 0423"`, `"canonical_slug": "deepseek/deepseek-v4-pro-20260423"`.
- `sources/deepseek-pricing.html`, Model Details table: MODEL columns `deepseek-flash` and `deepseek-v4-pro`; corresponding MODEL VERSION columns `DeepSeek-V4.1-Flash-1017` and `DeepSeek-V4-Pro-0813`.
- `sources/openrouter-models.json`, entry ID `deepseek/deepseek-v4-pro-0813`: name `DeepSeek: DeepSeek V4 Pro 0813`, canonical slug `deepseek/deepseek-v4-pro-20260813`, description `This is the GA release of DeepSeek V4 Pro.` This correct match is already included separately in the candidate.
- Provenance URLs are mapped by `sources/SOURCES.md`: https://openrouter.ai/api/v1/models and https://api-docs.deepseek.com/quick_start/pricing.

Impact: a consumer treating this registry as the requested cross-provider subset can select the April model and its different price/output limit while expecting the August direct-vendor model. Equal generic API ID spelling does not establish identical underlying versions when both official archives explicitly distinguish them. This is the prohibited predecessor/date-family match. Remove the 0423 OpenRouter entry from this subset unless a separately authorized direct-vendor 0423 entry and its official provenance are added. Keep the already present `deepseek/deepseek-v4-pro-0813` row.

# REFUTED — No additional mapped-value defects found

The following hypotheses were checked independently against the sealed archive and were refuted:

- Missing or misspelled OpenRouter model IDs: all 135 candidate IDs exist verbatim in the 471-entry official archive.
- Base price conversion or unit errors: every input, output, cache-read and explicit one-hour cache-write amount matches archived per-token decimal strings multiplied by 1,000,000 and rounded to no more than six decimals. Unqualified cache-write amounts are retained as converted note values rather than assigned an unsupported TTL or hourly storage unit.
- Long-context errors: all 41 `long_context` objects match archived `pricing.overrides`, including `min_prompt_tokens`, input/output/cache-read prices, explicit one-hour writes, and inheritance of unmodified base fields. No extra or missing long-context objects were found.
- Incorrect context/output/modality mappings: every candidate context equals catalog `context_length`; every output limit equals `top_provider.max_completion_tokens`; every mapped input modality equals the catalog set after excluding ambiguous `file`. No unsupported PDF assumption was found.
- Lifecycle/date mapping errors: all 14 non-null catalog `expiration_date` values map to `shutdown` with deprecated status; no unsupported shutdown date was found. Preview entries match direct-vendor preview status. Claude Sonnet 4.5 correctly does not copy direct-host retirement dates into an OpenRouter shutdown field.
- Batch routing and discount errors: all 57 `:batch` entries are explicitly listed official batch-only IDs, carry the batch-route note and null additional discount; every non-null standard-row discount agrees across archived token-priced components. Nonuniform route prices remain undiscounted rather than forcing one percentage.
- Tier mismatches: all included rows inherit a matching direct-vendor tier under exact ID/name matching plus the explicitly documented aliases, subject to OR-01's false identity match.
- Missing eligible exact matches: exhaustive casefolded exact direct ID / direct display-name matching across all six origin datasets and all text-input/text-output OpenRouter catalog entries found no omissions. Manual alias checks support Anthropic catalog slugs, DeepSeek Flash 1017, xAI Grok 4.20, and OpenAI Chat Latest. Unversioned DeepSeek Flash points to a September snapshot and is correctly excluded; Pro/dated/predecessor family resemblance was not treated as sufficient matching evidence.
- Probe/default errors: `z-ai/glm-5.2` is the unique probe at 0.007 USD/MTok input, the cheapest eligible GA text candidate; `openai/gpt-6.1-sol` is the unique default. The low GLM prompt price is present verbatim in the official archive (`0.000000007` per token).
- Provider endpoint/auth errors: `providers/openrouter.json` base URL `https://openrouter.ai/api/v1`, bearer auth, Responses support and Chat Completions support are supported by the archived quickstart and catalog endpoint lists. The batch-only exception is explicitly described in the provider note.

# Evidence boundary

Cold independent read completed without reading coordinator audits or other review notes. Read-only review of snapshot `/home/michel/projects/ai-model-registry/.research/r2-openrouter-review-852ee9b6`; manifest SHA-256 `d97298fce0be734e8797aeedd48dbcba8d6c61f3a1bee2c352fd8a44e376412b` verified, along with all 26 manifest members, both before review and before report creation. Official archive was fetched 2026-11-14 as declared by SOURCES.md. No network, source changes, Git mutations, installs, recursive agents, or full-suite rerun. Independent focused checks were ad hoc Python JSON/Decimal comparisons; the coordinator owns final integrated validation. Runtime, credentials, live routing, and live pricing were outside this sealed-source review. No unsupported security-hardening quota was applied. Token usage is unavailable; shell-startup latency materially delayed reads.

UNVERIFIED: no additional unresolved source acceptance question identified within this review's sealed archive and scope. This is a review finding report, not runtime or release acceptance.

## Independent repair recheck (preserved)

# CONFIRMED — Repair accepted; OR-01 closed

The repaired immutable snapshot removes exactly the older `deepseek/deepseek-v4-pro` (0423) entry identified in the independent review. No new finding or affected correspondence regression was found.

- Final model count: **134**.
- Older `deepseek/deepseek-v4-pro` ID: absent.
- Correct `deepseek/deepseek-v4-pro-0813` ID: present exactly once and unchanged.
- Byte comparison confirms `models/openrouter.json` differs only by removal of the complete older JSON entry, starting at original line 2366. Every surviving row, field, price, note, ordering, formatting byte, and model-file top-level value is unchanged.
- `providers/openrouter.json` is byte-for-byte unchanged.
- Unique probe remains `z-ai/glm-5.2`; unique default remains `openai/gpt-6.1-sol`.

The retained 0813 row continues to correspond to the direct-vendor model: original pinned `sources/openrouter-models.json` entry `deepseek/deepseek-v4-pro-0813` has canonical slug `deepseek/deepseek-v4-pro-20260813` and name `DeepSeek: DeepSeek V4 Pro 0813`; original pinned `sources/deepseek-pricing.html` identifies direct API `deepseek-v4-pro` as `DeepSeek-V4-Pro-0813`. Removal of the unrelated 0423 row does not change any retained match or pricing data and does not alter the previously verified cheapest probe or default.

# Scope and evidence

Repair snapshot: `/home/michel/projects/ai-model-registry/.research/r2-openrouter-repair-852ee9b6`.

Manifest SHA-256 verified: `8eb9c7dfede0e5b37e555a4f7faf124cd22bc8b79f322a506312e09a25579141`. Both member hashes verified. Original review snapshot manifest SHA-256 `d97298fce0be734e8797aeedd48dbcba8d6c61f3a1bee2c352fd8a44e376412b` and all 26 original members reverified before using the original pinned sources.

This was one bounded identity-repair review with independent Python assertions for manifest hashes, exact byte removal, model list equality after removal, retained 0813 correspondence, count and flags. No moving working tree, network, source edits, Git mutations, installs, or full-suite repeat. The parent reports 80 passing tests and the initial integrated 18-file validator result; those are coordinator-owned evidence and were not independently rerun here. The parent's final data validator remains separate from this repair verdict.

Requested review configuration: **gpt-6.1-sol / high**. Runtime model/effort identity and token measurements: **unavailable**, so the requested configuration is not represented as independently attested runtime identity.

REFUTED: concern that the repair altered surviving data or provider metadata.

UNVERIFIED: no additional unresolved acceptance question within this bounded repair scope. This verdict establishes the source-data repair only; it does not claim live API or release acceptance.
