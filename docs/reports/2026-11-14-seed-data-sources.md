# R2 seed-data sources, omissions, and deviations

Pricing archive: 2026-11-14. Coordinator verification corrections: 2026-11-15. Dev mode: mvp. Resumed lane: `852ee9b6-7ca5-4cf2-826e-50dfa394080b`.

This is the final seed inventory, using only coordinator-supplied official response bodies in `.research/2026-11-14/` and URLs from `SOURCES.md`. No network, API calls, package installation, commit, tag, push, or release runs in this lane. `.research/` was already ignored and remains untracked. The earlier blocked audit is retained verbatim at the end. Source dates establish archive review, not current runtime availability.

Registry classification policy (tier, probe, default and unlabelled-current catalog GA) is a documented derivation, not a vendor quote. Null means unknown/unpublished, zero means explicitly free. Token prices are USD per million tokens; hourly storage has separate units. Empty cache-write arrays mean no published per-token TTL tariff. Omitted optional storage means no applicable sourced hourly rate, not free service.

## Final inventory

| Provider | Models | Probe | Default | Scalar nulls |
| --- | ---: | --- | --- | ---: |
| anthropic | 15 | `claude-haiku-5-5` | `claude-opus-5-5` | 0 |
| bedrock | 11 | `anthropic.claude-haiku-5-5` | `anthropic.claude-opus-5-5` | 9 |
| deepseek | 2 | `deepseek-flash` | `deepseek-flash` | 2 |
| gemini | 15 | `gemini-3.1-flash-lite` | `gemini-3.8-flash` | 38 |
| openai | 31 | `gpt-5-nano` | `gpt-6.1-sol` | 73 |
| openrouter | 72 | `z-ai/glm-5.2` | `openai/gpt-6.1-sol` | 37 |
| vertex | 14 | `claude-haiku-5-5` | `claude-opus-5-5` | 2 |
| xai | 8 | `grok-build-0.1` | `grok-4.7` | 9 |
| zai | 9 | `glm-5.3-flash` | `glm-5.3` | 27 |

Total: 177 models, 9 providers. Scalar-null counts include limits and all nested price fields, not absent optional fields or empty arrays.


## Pre-release schema decisions

ADR0003 replaces fixed 5m/1h fields with required cache_writes0..6 unique TTL/price objects in both standard and long_context pricing, adds optional hourly cache storage, and retains schema_version1. Old names are rejected. Gemini Interactions joins the provider enum. R1 had no harness protocol field, so R2 adds optional protocols with the same closed enum; no unrelated required harness field is invented. Existing command/environment restrictions are preserved.

The batch percentage summarizes published input/output discounts; it is not authority to derive cache/storage or unpublished context-band prices. GCP Opus5.5 deliberately remains null under the explicit coordinator decision. Notes and backlog retain pricing conditions that cannot be expressed.

## anthropic

Endpoint: `https://api.anthropic.com`; auth: `bearer`; protocols: `anthropic_messages`.

Files and official URLs:

- `ep-anthropic.md` — <https://platform.claude.com/docs/en/api/overview>
- `anthropic-models.md` — <https://platform.claude.com/docs/en/about-claude/models/overview>
- `anthropic-pricing.md` — <https://platform.claude.com/docs/en/about-claude/pricing>
- `anthropic-deprecations.md` — <https://platform.claude.com/docs/en/about-claude/model-deprecations>

Included exact IDs and lifecycle:

- `claude-fable-5-2`: ga.
- `claude-fable-5-1`: ga.
- `claude-fable-5`: ga.
- `claude-opus-5-5`: ga.
- `claude-opus-5`: ga.
- `claude-opus-4-8`: ga.
- `claude-opus-4-7`: ga.
- `claude-opus-4-6`: ga.
- `claude-opus-4-5-20251101`: ga.
- `claude-sonnet-5-5`: ga.
- `claude-sonnet-5`: ga.
- `claude-sonnet-4-6`: ga.
- `claude-sonnet-4-5-20250929`: deprecated; shutdown `2026-11-30`.
- `claude-haiku-5-5`: ga.
- `claude-haiku-4-5-20251001`: ga.

Source decisions, exclusions and deviations:

All 15 prices/limits are sourced. Sonnet 4.5 remains serving until 2026-11-30 and is deprecated. Haiku 5.5 uses the requested 100000-token threshold. Source 1M/200K/128K/64K counts are expanded in decimal. Cache writes retain 5m/1h. Batch tables establish 50% input/output discounts. The provider uses preferred Authorization: Bearer; x-api-key is the legacy fallback, not the selected auth.

Every null (fields relative to each model object):

- None.

Empty standard cache-write arrays: none.

## bedrock

Endpoint: `https://bedrock-mantle.{region}.api.aws/anthropic`; auth: `aws_sigv4`; protocols: `anthropic_messages`.

Files and official URLs:

- `ep-bedrock-claude.md` — <https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock>
- `anthropic-models.md` — <https://platform.claude.com/docs/en/about-claude/models/overview>
- `anthropic-pricing.md` — <https://platform.claude.com/docs/en/about-claude/pricing>
- `aws-bedrockfm-us-east-1.json` — <https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrockFoundationModels/20261109224312/us-east-1/index.json>

Included exact IDs and lifecycle:

- `global.anthropic.claude-fable-5-2`: ga.
- `anthropic.claude-fable-5-1`: ga.
- `anthropic.claude-fable-5`: ga.
- `anthropic.claude-opus-5-5`: ga.
- `anthropic.claude-opus-5`: ga.
- `anthropic.claude-opus-4-8`: ga.
- `anthropic.claude-opus-4-7`: ga.
- `anthropic.claude-sonnet-5-5`: ga.
- `anthropic.claude-sonnet-5`: ga.
- `anthropic.claude-haiku-5-5`: ga.
- `anthropic.claude-haiku-4-5`: ga.

Source decisions, exclusions and deviations:

Recommended route is mantle /anthropic with anthropic_messages and documented aws_sigv4 (signing service bedrock-mantle); no new auth enum is needed. The runtime Converse/InvokeModel endpoint is named in the provider note. Fable5.2 is explicitly runtime-only and its model note states it cannot use mantle; schema has no per-model endpoint override. Exact Bedrock IDs come from the archived endpoint/model tables, not guessed catalog-name conversions. Selected AWS global standard on-demand price dimensions all use 1M tokens (multiplier1); no regional fallback was needed. Haiku5.5 long_ctx rows supply the higher prices. Generic AWS cache-write operation maps to Anthropic documented default5m; explicit1h stays separate. Batch50 is sourced only for Opus5 and Haiku4.5, not copied from first-party Claude.

Every null (fields relative to each model object):

- `/pricing/batch_discount_percent`: `global.anthropic.claude-fable-5-2`, `anthropic.claude-fable-5-1`, `anthropic.claude-fable-5`, `anthropic.claude-opus-5-5`, `anthropic.claude-opus-4-8`, `anthropic.claude-opus-4-7`, `anthropic.claude-sonnet-5-5`, `anthropic.claude-sonnet-5`, `anthropic.claude-haiku-5-5`. No matching published global batch input/output pair exists in the selected AWS catalog scope for these models.

Empty standard cache-write arrays: none.

## deepseek

Endpoint: `https://api.deepseek.com`; auth: `bearer`; protocols: `openai_chat`, `openai_responses`.

Files and official URLs:

- `ep-deepseek.html` — <https://api-docs.deepseek.com/>
- `deepseek-pricing.html` — <https://api-docs.deepseek.com/quick_start/pricing>

Included exact IDs and lifecycle:

- `deepseek-flash`: ga.
- `deepseek-v4-pro`: ga.

Source decisions, exclusions and deviations:

The new official homepage supplies Authorization: Bearer. Both advertised OpenAI protocol families are present. Peak cache-miss rates populate input; peak hits populate cache_read. Off-peak is 50% lower. Peak hours are Monday-Friday 01:00-04:00 and 06:00-10:00 UTC except Chinese public holidays; all other times are off-peak. Source 1M/384K limits use decimal counts. Flash version is DeepSeek-V4.1-Flash-1017; legacy deepseek-v4-flash and deepseek-v4-flash-vision-exp names route to current Flash and are not separate retired versions. Anthropic format needs the separate /anthropic base noted on the provider.

Every null (fields relative to each model object):

- `/pricing/batch_discount_percent`: `deepseek-flash`, `deepseek-v4-pro`. The supplied vendor archive does not establish a standalone batch tariff for these IDs.

Empty standard cache-write arrays: `deepseek-flash`, `deepseek-v4-pro`.

## gemini

Endpoint: `https://generativelanguage.googleapis.com`; auth: `google_api_key`; protocols: `gemini_generate`, `gemini_interactions`.

Files and official URLs:

- `ep-gemini.md` — <https://ai.google.dev/gemini-api/docs/quickstart>
- `gemini-generate-content.md` — <https://ai.google.dev/api/generate-content>
- `gemini-models.md` — <https://ai.google.dev/gemini-api/docs/models>
- `gemini-pricing.md` — <https://ai.google.dev/gemini-api/docs/pricing>

Included exact IDs and lifecycle:

- `gemini-4-carbon`: ga.
- `gemini-4-argon`: ga.
- `gemini-4-hydrogen`: ga.
- `gemini-3.8-flash`: ga.
- `gemini-3.6-flash`: ga.
- `gemini-3.5-flash-lite`: ga.
- `gemini-3.1-flash-lite`: ga.
- `gemini-3.1-pro-preview`: preview.
- `gemini-3-flash-preview`: preview.
- `gemini-robotics-er-2-preview`: preview.
- `gemini-robotics-er-2-streaming-preview`: preview.
- `gemini-3.1-pro-preview-customtools`: preview.
- `deep-research-preview-04-2026`: preview.
- `deep-research-max-preview-04-2026`: preview.
- `antigravity-preview-09-2026`: preview.

Source decisions, exclusions and deviations:

The quickstart documents Interactions, not generateContent. The added generation reference establishes generateContent; both protocols are listed and their paths use /v1beta under the requested unversioned base URL. All existing-user-only Gemini 2.5 endpoints are excluded as gated, including deprecated Pro/Flash and GA Flash-Lite; the cheapest remaining GA probe is 3.1 Flash-Lite. An earlier lane interpretation included them; independent review caught the new-user probe failure and the final data removes all three plus their OpenRouter counterparts. Paid Standard prices are used, not free allowances. Hourly caching storage is separate from writes; no per-token write tariff is published. 4-family models use implicit caching only. The source maximum-output 64K / 1M becomes the published maximum 1000000 with a note. Other missing exact limits stay null. Managed-agent IDs remain included as explicit text agent entries with null standalone prices and Interactions-only notes. Robotics Streaming is Live-only, outside the protocol enum. Batch cache/storage exceptions, audio prices, future/promotion rates, tools and long-decode options are retained in notes/backlog; the scalar discount must not be applied to every price category.

Every null (fields relative to each model object):

- `/context_window`: `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-3.1-pro-preview`, `gemini-3-flash-preview`, `gemini-robotics-er-2-preview`, `gemini-robotics-er-2-streaming-preview`, `gemini-3.1-pro-preview-customtools`, `deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`, `antigravity-preview-09-2026`. The supplied official index/pricing archive does not establish an exact numeric limit for these IDs; no value is inferred from a name or third-party host.
- `/max_output_tokens`: `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-3.1-pro-preview`, `gemini-3-flash-preview`, `gemini-robotics-er-2-preview`, `gemini-robotics-er-2-streaming-preview`, `gemini-3.1-pro-preview-customtools`, `deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`, `antigravity-preview-09-2026`. The supplied official index/pricing archive does not establish an exact numeric limit for these IDs; no value is inferred from a name or third-party host.
- `/pricing/batch_discount_percent`: `gemini-robotics-er-2-streaming-preview`, `deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`, `antigravity-preview-09-2026`. No standalone batch tariff is established for the Live-only or managed-agent entry.
- `/pricing/cache_read`: `gemini-robotics-er-2-streaming-preview`, `deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`, `antigravity-preview-09-2026`. The relevant source column is a dash/absent or the managed-agent underlying model is unresolved; this is unknown, not free.
- `/pricing/input`: `deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`, `antigravity-preview-09-2026`. Managed agents are billed at underlying-model/tool rates; the archive does not publish one standalone model token-price tuple.
- `/pricing/output`: `deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`, `antigravity-preview-09-2026`. Managed agents are billed at underlying-model/tool rates; the archive does not publish one standalone model token-price tuple.

Empty standard cache-write arrays: `gemini-4-carbon`, `gemini-4-argon`, `gemini-4-hydrogen`, `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-3.1-pro-preview`, `gemini-3-flash-preview`, `gemini-robotics-er-2-preview`, `gemini-robotics-er-2-streaming-preview`, `gemini-3.1-pro-preview-customtools`, `deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`, `antigravity-preview-09-2026`.

## openai

Endpoint: `https://api.openai.com/v1`; auth: `bearer`; protocols: `openai_responses`, `openai_chat`.

Files and official URLs:

- `ep-openai.md` — <https://developers.openai.com/api/reference/overview>
- `openai-models.md` — <https://developers.openai.com/api/docs/models>
- `openai-pricing.md` — <https://developers.openai.com/api/docs/pricing>

Included exact IDs and lifecycle:

- `gpt-6-astra`: ga.
- `gpt-6.1-sol`: ga.
- `gpt-6.1-terra`: ga.
- `gpt-6-luna`: ga.
- `gpt-6-sol`: ga.
- `gpt-5.6-sol`: ga.
- `gpt-5.6-terra`: ga.
- `gpt-5.6-luna`: ga.
- `gpt-5.5`: ga.
- `gpt-5.5-pro`: ga.
- `gpt-5.4`: ga.
- `gpt-5.4-pro`: ga.
- `gpt-5.4-mini`: ga.
- `gpt-5.4-nano`: ga.
- `gpt-5.2`: ga.
- `gpt-5.2-pro`: ga.
- `gpt-5.1`: ga.
- `gpt-5`: ga.
- `gpt-5-mini`: ga.
- `gpt-5-nano`: ga.
- `gpt-5-pro`: ga.
- `gpt-4.1`: ga.
- `gpt-4.1-mini`: ga.
- `gpt-4o`: ga.
- `gpt-4o-mini`: ga.
- `o3-pro`: ga.
- `o3`: ga.
- `gpt-6-astra-law`: ga.
- `chat-latest`: ga.
- `gpt-5.3-codex`: ga.
- `gpt-5-search-api`: ga.

Source decisions, exclusions and deviations:

Read the extended Standard header as input, output, cached input, 30m write, 12h write, followed by the same long-context columns. Short context is <=272K and long context is >272K, so threshold_tokens is 272000 and the first higher-priced integer prompt is 272001. Only eight extended rows publish write TTLs. The model index supplies no exact token limits. GA is a classification from current priced non-preview API listings; prior-generation alone does not mean deprecated. The user-selected Sol default balances cost and quality; the source also recommends Astra for maximum capability. Batch percentage summarizes input/output: GPT-5.4 cached Batch is rounded to $0.13/MTok, GPT-5.5-Pro long-context Batch is unpublished, and several older Batch cached-input columns are dashes; notes do not infer those rates. Promotion windows and processing/residency uplifts are notes, not structured tariffs.

Every null (fields relative to each model object):

- `/context_window`: `gpt-6-astra`, `gpt-6.1-sol`, `gpt-6.1-terra`, `gpt-6-luna`, `gpt-6-sol`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, `gpt-5.5-pro`, `gpt-5.4`, `gpt-5.4-pro`, `gpt-5.4-mini`, `gpt-5.4-nano`, `gpt-5.2`, `gpt-5.2-pro`, `gpt-5.1`, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-pro`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini`, `o3-pro`, `o3`, `gpt-6-astra-law`, `chat-latest`, `gpt-5.3-codex`, `gpt-5-search-api`. The supplied official index/pricing archive does not establish an exact numeric limit for these IDs; no value is inferred from a name or third-party host.
- `/max_output_tokens`: `gpt-6-astra`, `gpt-6.1-sol`, `gpt-6.1-terra`, `gpt-6-luna`, `gpt-6-sol`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, `gpt-5.5-pro`, `gpt-5.4`, `gpt-5.4-pro`, `gpt-5.4-mini`, `gpt-5.4-nano`, `gpt-5.2`, `gpt-5.2-pro`, `gpt-5.1`, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-pro`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini`, `o3-pro`, `o3`, `gpt-6-astra-law`, `chat-latest`, `gpt-5.3-codex`, `gpt-5-search-api`. The supplied official index/pricing archive does not establish an exact numeric limit for these IDs; no value is inferred from a name or third-party host.
- `/pricing/batch_discount_percent`: `gpt-6-astra-law`, `chat-latest`, `gpt-5.3-codex`, `gpt-5-search-api`. The supplied vendor archive does not establish a standalone batch tariff for these IDs.
- `/pricing/cache_read`: `gpt-5.5-pro`, `gpt-5.4-pro`, `gpt-5.2-pro`, `gpt-5-pro`, `o3-pro`. The relevant source column is a dash/absent or the managed-agent underlying model is unresolved; this is unknown, not free.
- `/pricing/long_context/cache_read`: `gpt-5.5-pro`, `gpt-5.4-pro`. The relevant source column is a dash/absent or the managed-agent underlying model is unresolved; this is unknown, not free.

Empty standard cache-write arrays: `gpt-5.5`, `gpt-5.5-pro`, `gpt-5.4`, `gpt-5.4-pro`, `gpt-5.4-mini`, `gpt-5.4-nano`, `gpt-5.2`, `gpt-5.2-pro`, `gpt-5.1`, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-pro`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini`, `o3-pro`, `o3`, `gpt-6-astra-law`, `chat-latest`, `gpt-5.3-codex`, `gpt-5-search-api`.

## openrouter

Endpoint: `https://openrouter.ai/api/v1`; auth: `bearer`; protocols: `openai_chat`, `openai_responses`.

Files and official URLs:

- `ep-openrouter.md` — <https://openrouter.ai/docs/quickstart>
- `openrouter-models.json` — <https://openrouter.ai/api/v1/models>

Included exact IDs and lifecycle:

- `google/gemini-4-hydrogen`: ga.
- `google/gemini-4-carbon`: ga.
- `anthropic/claude-fable-5.2`: ga.
- `z-ai/glm-5.3-flashx-legal`: ga.
- `openai/gpt-6.1-terra`: ga.
- `deepseek/deepseek-v4.1-flash-1017`: ga.
- `google/gemini-4-argon`: ga.
- `anthropic/claude-haiku-5.5`: ga.
- `openai/gpt-6.1-sol`: ga.
- `anthropic/claude-sonnet-5.5`: ga.
- `openai/gpt-6-luna`: ga.
- `openai/gpt-6-sol`: ga.
- `anthropic/claude-opus-5.5`: ga.
- `x-ai/grok-4.7`: ga.
- `z-ai/glm-5.3-flashx`: ga.
- `openai/gpt-6-astra`: ga.
- `google/gemini-3.8-flash`: ga.
- `anthropic/claude-fable-5.1`: ga.
- `z-ai/glm-5.3-flash`: ga.
- `z-ai/glm-5.3`: ga.
- `deepseek/deepseek-v4-pro-0813`: ga.
- `x-ai/grok-4.6`: ga.
- `anthropic/claude-opus-5`: ga.
- `google/gemini-3.6-flash`: ga.
- `google/gemini-3.5-flash-lite`: ga.
- `openai/gpt-5.6-luna`: ga.
- `openai/gpt-5.6-terra`: ga.
- `openai/gpt-5.6-sol`: ga.
- `x-ai/grok-4.5`: ga.
- `anthropic/claude-sonnet-5`: ga.
- `z-ai/glm-5.2`: ga.
- `anthropic/claude-fable-5`: ga.
- `anthropic/claude-opus-4.8`: ga.
- `x-ai/grok-build-0.1`: ga.
- `google/gemini-3.1-flash-lite`: ga.
- `openai/gpt-chat-latest`: ga.
- `x-ai/grok-4.3`: ga.
- `openai/gpt-5.5-pro`: ga.
- `openai/gpt-5.5`: ga.
- `anthropic/claude-opus-4.7`: ga.
- `z-ai/glm-5.1`: deprecated; shutdown `2026-11-20`.
- `x-ai/grok-4.20-multi-agent`: ga.
- `x-ai/grok-4.20`: ga.
- `openai/gpt-5.4-nano`: ga.
- `openai/gpt-5.4-mini`: ga.
- `openai/gpt-5.4-pro`: ga.
- `openai/gpt-5.4`: ga.
- `google/gemini-3.1-pro-preview-customtools`: preview.
- `openai/gpt-5.3-codex`: ga.
- `google/gemini-3.1-pro-preview`: preview.
- `anthropic/claude-sonnet-4.6`: ga.
- `z-ai/glm-5`: ga.
- `anthropic/claude-opus-4.6`: ga.
- `z-ai/glm-4.7`: ga.
- `google/gemini-3-flash-preview`: preview.
- `openai/gpt-5.2-pro`: ga.
- `openai/gpt-5.2`: ga.
- `anthropic/claude-opus-4.5`: ga.
- `openai/gpt-5.1`: ga.
- `anthropic/claude-haiku-4.5`: ga.
- `openai/gpt-5-pro`: deprecated; shutdown `2026-12-11`.
- `z-ai/glm-4.6`: ga.
- `anthropic/claude-sonnet-4.5`: ga.
- `openai/gpt-5`: deprecated; shutdown `2026-12-11`.
- `openai/gpt-5-mini`: deprecated; shutdown `2026-12-11`.
- `openai/gpt-5-nano`: deprecated; shutdown `2026-12-11`.
- `openai/o3-pro`: deprecated; shutdown `2026-12-11`.
- `openai/o3`: deprecated; shutdown `2026-12-11`.
- `openai/gpt-4.1`: ga.
- `openai/gpt-4.1-mini`: ga.
- `openai/gpt-4o-mini`: ga.
- `openai/gpt-4o`: ga.

Source decisions, exclusions and deviations:

Only explicit same-model counterparts are included; the correspondence table below names them. All 57 `:batch` identifiers are excluded from chat selection; their retained base records each name the batch route and the models-list prices in one sentence. Existing base prices and batch discount metadata are unchanged. OpenRouter expiration_date controls its lifecycle; another host shutdown is not extrapolated. Generic file input cannot be narrowed to PDF. Unqualified input_cache_write lacks a TTL; its converted rate stays in notes, while explicit _1h stays structured. Partial context overrides inherit unchanged fields. One batch percentage is used only when all published categories/context bands agree. The `overrides[].min_prompt_tokens` inclusive minimum is converted to the registry's strict comparison by subtracting one; see the complete threshold table below. Direct-vendor tariffs are not copied into OpenRouter prices.

Removed unmatched Z.ai routes — **id not confirmed by API reference**:

- `z-ai/glm-4.7-flash` — id not confirmed by API reference; no retained direct-vendor counterpart.
- `z-ai/glm-4.6v` — id not confirmed by API reference; no retained direct-vendor counterpart.
- `z-ai/glm-4.5v` — id not confirmed by API reference; no retained direct-vendor counterpart.
- `z-ai/glm-4.5` — id not confirmed by API reference; no retained direct-vendor counterpart.
- `z-ai/glm-4.5-air` — id not confirmed by API reference; no retained direct-vendor counterpart.

Every null (fields relative to each model object):

- `/pricing/batch_discount_percent`: `google/gemini-4-hydrogen`, `google/gemini-4-carbon`, `z-ai/glm-5.3-flashx-legal`, `deepseek/deepseek-v4.1-flash-1017`, `google/gemini-4-argon`, `z-ai/glm-5.3-flashx`, `google/gemini-3.8-flash`, `z-ai/glm-5.3-flash`, `z-ai/glm-5.3`, `deepseek/deepseek-v4-pro-0813`, `google/gemini-3.6-flash`, `google/gemini-3.5-flash-lite`, `openai/gpt-5.6-luna`, `openai/gpt-5.6-terra`, `x-ai/grok-4.5`, `z-ai/glm-5.2`, `x-ai/grok-build-0.1`, `google/gemini-3.1-flash-lite`, `openai/gpt-chat-latest`, `z-ai/glm-5.1`, `x-ai/grok-4.20-multi-agent`, `x-ai/grok-4.20`, `google/gemini-3.1-pro-preview-customtools`, `openai/gpt-5.3-codex`, `google/gemini-3.1-pro-preview`, `z-ai/glm-5`, `z-ai/glm-4.7`, `google/gemini-3-flash-preview`, `z-ai/glm-4.6`, `openai/o3-pro`. No counterpart establishes one uniform ratio across published categories/context bands.
- `/pricing/cache_read`: `openai/gpt-5.5-pro`, `openai/gpt-5.4-pro`, `openai/gpt-5.2-pro`, `openai/gpt-5-pro`, `openai/o3-pro`. The catalog tariff has no input_cache_read field.
- `/pricing/long_context/cache_read`: `openai/gpt-5.5-pro`, `openai/gpt-5.4-pro`. The context override and base tariff have no input_cache_read field.

Empty standard cache-write arrays: `google/gemini-4-hydrogen`, `google/gemini-4-carbon`, `z-ai/glm-5.3-flashx-legal`, `openai/gpt-6.1-terra`, `deepseek/deepseek-v4.1-flash-1017`, `google/gemini-4-argon`, `openai/gpt-6.1-sol`, `openai/gpt-6-luna`, `openai/gpt-6-sol`, `x-ai/grok-4.7`, `z-ai/glm-5.3-flashx`, `openai/gpt-6-astra`, `google/gemini-3.8-flash`, `z-ai/glm-5.3-flash`, `z-ai/glm-5.3`, `deepseek/deepseek-v4-pro-0813`, `x-ai/grok-4.6`, `google/gemini-3.6-flash`, `google/gemini-3.5-flash-lite`, `openai/gpt-5.6-luna`, `openai/gpt-5.6-terra`, `openai/gpt-5.6-sol`, `x-ai/grok-4.5`, `z-ai/glm-5.2`, `x-ai/grok-build-0.1`, `google/gemini-3.1-flash-lite`, `openai/gpt-chat-latest`, `x-ai/grok-4.3`, `openai/gpt-5.5-pro`, `openai/gpt-5.5`, `z-ai/glm-5.1`, `x-ai/grok-4.20-multi-agent`, `x-ai/grok-4.20`, `openai/gpt-5.4-nano`, `openai/gpt-5.4-mini`, `openai/gpt-5.4-pro`, `openai/gpt-5.4`, `google/gemini-3.1-pro-preview-customtools`, `openai/gpt-5.3-codex`, `google/gemini-3.1-pro-preview`, `z-ai/glm-5`, `z-ai/glm-4.7`, `google/gemini-3-flash-preview`, `openai/gpt-5.2-pro`, `openai/gpt-5.2`, `openai/gpt-5.1`, `openai/gpt-5-pro`, `z-ai/glm-4.6`, `openai/gpt-5`, `openai/gpt-5-mini`, `openai/gpt-5-nano`, `openai/o3-pro`, `openai/o3`, `openai/gpt-4.1`, `openai/gpt-4.1-mini`, `openai/gpt-4o-mini`, `openai/gpt-4o`.


## vertex

Endpoint: `https://aiplatform.googleapis.com`; auth: `gcp_oauth`; protocols: `vertex_anthropic`.

Files and official URLs:

- `ep-vertex-claude.md` — <https://platform.claude.com/docs/en/build-with-claude/claude-models-on-google-cloud/google-managed>
- `anthropic-models.md` — <https://platform.claude.com/docs/en/about-claude/models/overview>
- `anthropic-deprecations.md` — <https://platform.claude.com/docs/en/about-claude/model-deprecations>
- `gcp-partner-pricing.txt` — <https://cloud.google.com/model-garden/partner-models/pricing>

Included exact IDs and lifecycle:

- `claude-fable-5-2`: ga.
- `claude-fable-5-1`: ga.
- `claude-fable-5`: ga.
- `claude-opus-5-5`: ga.
- `claude-opus-5`: ga.
- `claude-opus-4-8`: ga.
- `claude-opus-4-7`: ga.
- `claude-opus-4-6`: ga.
- `claude-opus-4-5@20251101`: ga.
- `claude-sonnet-5-5`: ga.
- `claude-sonnet-5`: ga.
- `claude-sonnet-4-6`: ga.
- `claude-haiku-5-5`: ga.
- `claude-haiku-4-5@20251001`: ga.

Source decisions, exclusions and deviations:

Use the first Google global table, before multi-region/regional tables. Lost model-name labels are attributed by row order and the Anthropic table only where unambiguous; repeated labelled Opus 4.8/4.7 rows agree. Exact Google-managed IDs come from the Anthropic overview/endpoint table. Global pricing stays separate from the documented 10% multi-region/regional premium for Sonnet4.5 and later; regional host template is in the provider note. Opus5.5 batch raw input/output $2.50/$12.50 are quoted, percentage null per decision. Opus4.5 standard1h cache-write remains null because its row is absent. Four explicitly deprecated Google IDs have no Google shutdown date in the archive and are omitted; Google says its lifecycle differs from first-party Claude, so first-party retired dates are not copied. Google Haiku threshold header/footnote equality differs; requested threshold100000 is retained without inventing a comparator.

Every null (fields relative to each model object):

- `/pricing/batch_discount_percent`: `claude-opus-5-5`. Opus 5.5 global batch input/output $2.50/$12.50 imply 37.5%, while its cache categories halve; explicit R2 decision requires null instead of one misleading percentage.
- `/pricing/cache_writes/1/price`: `claude-opus-4-5@20251101`. Google global Opus 4.5 standard 1h cache-write row is absent; the batch 1h row is not a standard price.

Empty standard cache-write arrays: none.

## xai

Endpoint: `https://api.x.ai/v1`; auth: `bearer`; protocols: `openai_chat`, `openai_responses`.

Files and official URLs:

- `ep-xai.md` — <https://docs.x.ai/developers/quickstart>
- `xai-models.md` — <https://docs.x.ai/docs/models>
- `xai-models.html` — <https://docs.x.ai/docs/models>

Included exact IDs and lifecycle:

- `grok-4.7`: ga.
- `grok-4.6`: ga.
- `grok-4.5`: ga.
- `grok-4.3`: ga.
- `grok-4.20-0309-reasoning`: ga.
- `grok-4.20-0309-non-reasoning`: ga.
- `grok-build-0.1`: ga.
- `grok-4.20-multi-agent-0309`: ga.

Source decisions, exclusions and deviations:

Text rates come from the Markdown table; embedded globalThis.__XAI_PUBLIC_MODELS__ in raw HTML supplies exact IDs, aliases, modalities, maxPromptLength, longContextThreshold, batchEnabled and batchDiscountPercent. Regional duplicate metadata is deduplicated. Source K/M limits are decimal. >=200k prompt rows use threshold_tokens=199999 and the higher rate applies to all request tokens. Seven explicitly enabled models publish 20% Batch; Build lacks batchEnabled and stays null. No maximum output is published. Grok 4.7 is the recommended most-capable code/chat model, hence default/high tier. Quickstart demonstrates Responses; archived raw models navigation also names Chat Completions (Legacy), supporting both listed protocol families with that evidence limit noted.

Every null (fields relative to each model object):

- `/max_output_tokens`: `grok-4.7`, `grok-4.6`, `grok-4.5`, `grok-4.3`, `grok-4.20-0309-reasoning`, `grok-4.20-0309-non-reasoning`, `grok-build-0.1`, `grok-4.20-multi-agent-0309`. The supplied official index/pricing archive does not establish an exact numeric limit for these IDs; no value is inferred from a name or third-party host.
- `/pricing/batch_discount_percent`: `grok-build-0.1`. Build metadata has a discount value but no explicit batchEnabled flag; batch availability is not inferred.

Empty standard cache-write arrays: `grok-4.7`, `grok-4.6`, `grok-4.5`, `grok-4.3`, `grok-4.20-0309-reasoning`, `grok-4.20-0309-non-reasoning`, `grok-build-0.1`, `grok-4.20-multi-agent-0309`.

## zai

Endpoint: `https://api.z.ai/api/paas/v4`; auth: `bearer`; protocols: `openai_chat`.

Files and official URLs:

- `ep-zai.md` — <https://docs.z.ai/guides/overview/quick-start>
- `zai-pricing.md` / `zai-pricing.html` — <https://docs.z.ai/guides/overview/pricing>
- `zai-chat-completion.md` — <https://docs.z.ai/api-reference/llm/chat-completion> (coordinator-supplied archive fetched 2026-11-15).

Included exact IDs and lifecycle:

- `glm-5.3`: ga.
- `glm-5.3-flash`: ga.
- `glm-5.3-flashx`: ga.
- `glm-5.3-flashx-legal`: ga.
- `glm-5.2`: ga.
- `glm-5.1`: ga.
- `glm-5`: ga.
- `glm-4.7`: ga.
- `glm-4.6`: ga.

Source decisions, exclusions and deviations:

The two Chat Completions `model` enums (lines 209–215 and 499–502) confirm exactly these nine lowercase API IDs. Display names retain the pricing-table labels; all retained model and provider sources include the API-reference URL. The cheapest retained GA input price is $0.15/MTok for `glm-5.3-flash`, now the probe; `glm-5.3` remains default. Prices are unchanged. Current priced unlabelled rows are classified GA. Limits remain unknown because the retained source evidence does not establish numeric context/output limits. The Flash quickstart's unspecified visual input formats remain a note rather than invented modalities. Limited-time free cache storage is zero, not a token-write rate; its hourly unit and end date are unpublished.

Removed pricing-table IDs — **id not confirmed by API reference**:

- `GLM-4.7-FlashX` — id not confirmed by API reference.
- `GLM-4.5` — id not confirmed by API reference.
- `GLM-4.5-X` — id not confirmed by API reference.
- `GLM-4.5-Air` — id not confirmed by API reference.
- `GLM-4.5-AirX` — id not confirmed by API reference.
- `GLM-4-32B-0414-128K` — id not confirmed by API reference.
- `GLM-4.7-Flash` — id not confirmed by API reference.
- `GLM-4.5-Flash` — id not confirmed by API reference.
- `GLM-4.6V` — id not confirmed by API reference.
- `GLM-4.6V-FlashX` — id not confirmed by API reference.
- `GLM-4.5V` — id not confirmed by API reference.
- `GLM-4.6V-Flash` — id not confirmed by API reference.

Every null (fields relative to each model object):

- `/context_window`: `glm-5.3`, `glm-5.3-flash`, `glm-5.3-flashx`, `glm-5.3-flashx-legal`, `glm-5.2`, `glm-5.1`, `glm-5`, `glm-4.7`, `glm-4.6`. The retained archive does not establish an exact numeric limit.
- `/max_output_tokens`: `glm-5.3`, `glm-5.3-flash`, `glm-5.3-flashx`, `glm-5.3-flashx-legal`, `glm-5.2`, `glm-5.1`, `glm-5`, `glm-4.7`, `glm-4.6`. The retained archive does not establish an exact numeric limit.
- `/pricing/batch_discount_percent`: `glm-5.3`, `glm-5.3-flash`, `glm-5.3-flashx`, `glm-5.3-flashx-legal`, `glm-5.2`, `glm-5.1`, `glm-5`, `glm-4.7`, `glm-4.6`. The archive does not establish a standalone batch tariff.

Empty standard cache-write arrays: `glm-5.3`, `glm-5.3-flash`, `glm-5.3-flashx`, `glm-5.3-flashx-legal`, `glm-5.2`, `glm-5.1`, `glm-5`, `glm-4.7`, `glm-4.6`.


## Exact exclusions and family boundaries


OpenAI:
- Gated Trusted Access: `gpt-6-cyber`, `gpt-5.6-cyber`, `gpt-5.5-cyber-preview`, `gpt-6-rosalind`, `gpt-rosalind-research`, `gpt-rosalind-discovery`.
- Open-weight self-hosted without documented OpenAI-hosted API price/endpoint: `gpt-oss-120b`, `gpt-oss-20b`.
- Nontext indexed products: `gpt-audio-1.5`, `gpt-image-2.5-flare`, `gpt-image-2.5-sunburst`, `gpt-image-2.6-flare`, `gpt-image-2.6-sunburst`, `gpt-live-1`, `gpt-live-transcribe`, `gpt-realtime-1.5`, `gpt-realtime-2`, `gpt-realtime-2.1`, `gpt-realtime-2.1-mini`, `gpt-realtime-translate`, `gpt-realtime-whisper`, `gpt-transcribe`, `omni-moderation-latest`, `text-embedding-3-large`, `text-embedding-3-small`, `text-embedding-ada-002`. Image generation, audio/realtime voice, transcription, embeddings, moderation are outside text-model scope.
- Additional pricing-only nontext families: gpt-image-* (2,1.5,1mini),chatgpt-image-latest,gpt-audio-mini,gpt-audio,gpt-realtime-mini,gpt-realtime,gpt-4o-mini-tts,tts-1,tts-1-hd,gpt-4o-transcribe,gpt-4o-mini-transcribe,gpt-4o-transcribe-diarize,Whisper. Fine-tuned dated base rows describe account-specific training/inference rather than ordinary current base model deployments.

Gemini:
- Gated existing-user-only: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`. They still serve some prior users but cannot be seeded as generally accessible models/probes under this brief.
- Explicitly shut down: `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-2.5-computer-use-preview-10-2025`, `gemini-3-pro-preview`, `gemini-3.1-flash-lite-preview`, `gemini-robotics-er-1.6-preview`, `imagen-4.0-generate`.
- Nontext audio/transcription,image/video,music,embedding,zero-output Decisions endpoints: `gemini-2.5-flash-image`, `gemini-2.5-flash-native-audio-preview-12-2025`, `gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-preview-tts`, `gemini-3-pro-image`, `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image`, `gemini-3.1-flash-live-preview`, `gemini-3.1-flash-tts-preview`, `gemini-3.5-live-translate-preview`, `gemini-3.5-transcribe`, `gemini-3.5-transcribe-live`, `gemini-3.8-flash-lite-tts`, `gemini-3.8-flash-tts`, `gemini-3.8-live`, `gemini-3.8-live-extended-thinking`, `gemini-decision-1`, `gemini-embedding-001`, `gemini-embedding-2`, `gemini-nano-banana-2.1`, `gemini-omni-1.1-flash`, `gemini-omni-1.2-flash`, `lyria-3-clip-preview`, `lyria-3-pro-preview`, `lyria-3.5`, `lyria-realtime-exp`.
- Naming-convention-only examples: `gemini-2.5-flash-preview-09-2025`, `gemini-flash-latest`. No active serving version established. Gemma4 is a free-tier family label without exact callable size/variant IDs in archive.

DeepSeek:
- `deepseek-v4-flash`,`deepseek-v4-flash-vision-exp`: accepted compatibility aliases; original models retired; requests now serve current deepseek-flash.
- Search/fetch,OCR/file parsing,TTS,ASR: separately billed tools or media services without additional text model IDs.

ZAI:
- `GLM-OCR`: image OCR specialization without evidenced text input. `GLM-Image`,`CogView-4`: images. `CogVideoX-3`: video. `GLM-ASR-2512`: speech recognition. GLM Slide/Poster Agent(beta),General-Purpose Translation,Popular Special Effects Video Templates: service labels without established callable model IDs.

xAI:
- Nontext image/video/voice/transcription/TTS: `grok-imagine-image`, `grok-imagine-image-2.0`, `grok-imagine-video`, `grok-imagine-video-1.5`, `grok-imagine-video-1.5-lite`, `grok-tts`, `grok-voice-2.0`, `grok-voice-3.0`, `grok-voice-transcribe-2.0`.
- Aliases deduplicated (not independent models): `grok-4.20`, `grok-4.20-0309`, `grok-4.20-beta`, `grok-4.20-beta-0309`, `grok-4.20-beta-0309-non-reasoning`, `grok-4.20-beta-0309-reasoning`, `grok-4.20-beta-latest`, `grok-4.20-beta-latest-non-reasoning`, `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-non-reasoning`, `grok-4.20-beta-reasoning`, `grok-4.20-experimental-beta-0304`, `grok-4.20-experimental-beta-0304-non-reasoning`, `grok-4.20-experimental-beta-0304-reasoning`, `grok-4.20-experimental-beta-latest`, `grok-4.20-experimental-beta-non-reasoning-latest`, `grok-4.20-experimental-beta-reasoning-latest`, `grok-4.20-multi-agent`, `grok-4.20-multi-agent-beta-0309`, `grok-4.20-multi-agent-beta-latest`, `grok-4.20-multi-agent-experimental-beta-0304`, `grok-4.20-multi-agent-experimental-beta-latest`, `grok-4.20-multi-agent-latest`, `grok-4.20-non-reasoning`, `grok-4.20-non-reasoning-gv2`, `grok-4.20-non-reasoning-latest`, `grok-4.20-reasoning`, `grok-4.20-reasoning-gv2`, `grok-4.20-reasoning-latest`, `grok-4.3-latest`, `grok-4.5-latest`, `grok-build-latest`, `grok-code-fast`, `grok-code-fast-1`, `grok-code-fast-1-0825`.


### anthropic

- Gated `claude-mythos-5-2`, `claude-mythos-5-1`, `claude-mythos-5`, and `claude-mythos-preview`: limited/invited availability; Mythos Preview additionally has no dated shutdown.
- Retired exact API IDs from the deprecation source: `claude-opus-4-1-20250805`, `claude-opus-4-20250514`, `claude-sonnet-4-20250514`, `claude-3-7-sonnet-20250219`, `claude-3-5-haiku-20241022`, `claude-3-haiku-20240307`.
- Historical retirement tables additionally exclude `claude-3-5-sonnet-20240620`, `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-2.0`, `claude-2.1`, `claude-3-sonnet-20240229`, `claude-1.0`, `claude-1.1`, `claude-1.2`, `claude-1.3`, `claude-instant-1.0`, `claude-instant-1.1`, `claude-instant-1.2`: retired.
- Nontext-only families: none in this archive inventory.


### vertex

- `claude-mythos-5-2`, `claude-mythos-5-1`, `claude-mythos-5`: gated, limited availability.
- `claude-opus-4-1@20250805`, `claude-opus-4@20250514`, `claude-sonnet-4-5@20250929`, `claude-sonnet-4@20250514`: explicitly deprecated in Google-managed endpoint source, but no Google shutdown dates in archive. Google sets its own lifecycle; Anthropic retirement dates cannot substitute. Required shutdown field prevents truthful inclusion.
- Older families and aliases absent from the archived Google-managed API model-ID table are excluded; no IDs are invented. Nontext-only families: none in Claude inventory.


### bedrock

- `anthropic.claude-mythos-5-1`, `anthropic.claude-mythos-5`, and runtime-only Mythos 5.2 family: gated access; excluded.
- Claude Opus 4.6, Opus 4.5, Opus 4.1, Opus 4, Sonnet 4.6, Sonnet 4.5, Sonnet 4, Sonnet 3.7, Sonnet 3.5/v2, Haiku 3.5, Haiku 3, Opus 3, Sonnet 3, Claude 2.0, and Instant: price-catalog presence is not an exact API model identifier or lifecycle guarantee; no corresponding exact Bedrock ID in the archived endpoint/model tables. Older IDs are not fabricated. Partner-specific deprecated lifecycle dates also are not supplied.
- Nontext-only families: none in Claude inventory.


## OpenRouter exact correspondence and exclusions


| OpenRouter ID | Direct-vendor ID |
| --- | --- |
| `google/gemini-4-hydrogen` | `gemini-4-hydrogen` |
| `google/gemini-4-carbon` | `gemini-4-carbon` |
| `anthropic/claude-fable-5.2` | `claude-fable-5-2` |
| `z-ai/glm-5.3-flashx-legal` | `glm-5.3-flashx-legal` |
| `openai/gpt-6.1-terra` | `gpt-6.1-terra` |
| `deepseek/deepseek-v4.1-flash-1017` | `deepseek-flash` |
| `google/gemini-4-argon` | `gemini-4-argon` |
| `anthropic/claude-haiku-5.5` | `claude-haiku-5-5` |
| `openai/gpt-6.1-sol` | `gpt-6.1-sol` |
| `anthropic/claude-sonnet-5.5` | `claude-sonnet-5-5` |
| `openai/gpt-6-luna` | `gpt-6-luna` |
| `openai/gpt-6-sol` | `gpt-6-sol` |
| `anthropic/claude-opus-5.5` | `claude-opus-5-5` |
| `x-ai/grok-4.7` | `grok-4.7` |
| `z-ai/glm-5.3-flashx` | `glm-5.3-flashx` |
| `openai/gpt-6-astra` | `gpt-6-astra` |
| `google/gemini-3.8-flash` | `gemini-3.8-flash` |
| `anthropic/claude-fable-5.1` | `claude-fable-5-1` |
| `z-ai/glm-5.3-flash` | `glm-5.3-flash` |
| `z-ai/glm-5.3` | `glm-5.3` |
| `deepseek/deepseek-v4-pro-0813` | `deepseek-v4-pro` |
| `x-ai/grok-4.6` | `grok-4.6` |
| `anthropic/claude-opus-5` | `claude-opus-5` |
| `google/gemini-3.6-flash` | `gemini-3.6-flash` |
| `google/gemini-3.5-flash-lite` | `gemini-3.5-flash-lite` |
| `openai/gpt-5.6-luna` | `gpt-5.6-luna` |
| `openai/gpt-5.6-terra` | `gpt-5.6-terra` |
| `openai/gpt-5.6-sol` | `gpt-5.6-sol` |
| `x-ai/grok-4.5` | `grok-4.5` |
| `anthropic/claude-sonnet-5` | `claude-sonnet-5` |
| `z-ai/glm-5.2` | `glm-5.2` |
| `anthropic/claude-fable-5` | `claude-fable-5` |
| `anthropic/claude-opus-4.8` | `claude-opus-4-8` |
| `x-ai/grok-build-0.1` | `grok-build-0.1` |
| `google/gemini-3.1-flash-lite` | `gemini-3.1-flash-lite` |
| `openai/gpt-chat-latest` | `chat-latest` |
| `x-ai/grok-4.3` | `grok-4.3` |
| `openai/gpt-5.5-pro` | `gpt-5.5-pro` |
| `openai/gpt-5.5` | `gpt-5.5` |
| `anthropic/claude-opus-4.7` | `claude-opus-4-7` |
| `z-ai/glm-5.1` | `glm-5.1` |
| `x-ai/grok-4.20-multi-agent` | `grok-4.20-multi-agent-0309` |
| `x-ai/grok-4.20` | `grok-4.20-0309-reasoning` |
| `openai/gpt-5.4-nano` | `gpt-5.4-nano` |
| `openai/gpt-5.4-mini` | `gpt-5.4-mini` |
| `openai/gpt-5.4-pro` | `gpt-5.4-pro` |
| `openai/gpt-5.4` | `gpt-5.4` |
| `google/gemini-3.1-pro-preview-customtools` | `gemini-3.1-pro-preview-customtools` |
| `openai/gpt-5.3-codex` | `gpt-5.3-codex` |
| `google/gemini-3.1-pro-preview` | `gemini-3.1-pro-preview` |
| `anthropic/claude-sonnet-4.6` | `claude-sonnet-4-6` |
| `z-ai/glm-5` | `glm-5` |
| `anthropic/claude-opus-4.6` | `claude-opus-4-6` |
| `z-ai/glm-4.7` | `glm-4.7` |
| `google/gemini-3-flash-preview` | `gemini-3-flash-preview` |
| `openai/gpt-5.2-pro` | `gpt-5.2-pro` |
| `openai/gpt-5.2` | `gpt-5.2` |
| `anthropic/claude-opus-4.5` | `claude-opus-4-5-20251101` |
| `openai/gpt-5.1` | `gpt-5.1` |
| `anthropic/claude-haiku-4.5` | `claude-haiku-4-5-20251001` |
| `openai/gpt-5-pro` | `gpt-5-pro` |
| `z-ai/glm-4.6` | `glm-4.6` |
| `anthropic/claude-sonnet-4.5` | `claude-sonnet-4-5-20250929` |
| `openai/gpt-5` | `gpt-5` |
| `openai/gpt-5-mini` | `gpt-5-mini` |
| `openai/gpt-5-nano` | `gpt-5-nano` |
| `openai/o3-pro` | `o3-pro` |
| `openai/o3` | `o3` |
| `openai/gpt-4.1` | `gpt-4.1` |
| `openai/gpt-4.1-mini` | `gpt-4.1-mini` |
| `openai/gpt-4o-mini` | `gpt-4o-mini` |
| `openai/gpt-4o` | `gpt-4o` |

## Excluded catalog entries from the six selected vendors

All other vendors are outside the requested OpenRouter subset. The following exact selected-vendor IDs have no included unambiguous counterpart or fail the text/lifecycle scope:

- `google/gemini-omni-1.2-flash`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-omni-1.1-flash`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6.1-terra-pro`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6.1-terra-pro:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-nano-banana-2.1`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6.1-sol-pro`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6.1-sol-pro:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `z-ai/glm-5.3-prime`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6-luna-pro`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6-luna-pro:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6-sol-pro`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6-sol-pro:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-v4.1-flash`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-v4.1-flash:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6-astra-pro`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-6-astra-pro:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-v4-flash-vision-exp`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3.7-flash`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3.7-flash:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-v4-flash-0731`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-v4-flash-0731:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.6-luna-pro`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.6-luna-pro:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.6-terra-pro`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.6-terra-pro:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.6-sol-pro`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.6-sol-pro:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3.1-flash-lite-image`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3.1-flash-image`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3-pro-image`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3.5-flash`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3.5-flash:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-v4-pro`: Catalog name0423/canonical20260423 is the older snapshot; the direct-vendor API ID now serves0813. The explicitly matching0813 catalog entry is included.
- `deepseek/deepseek-v4-flash`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.4-image-2`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemma-4-26b-a4b-it`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemma-4-26b-a4b-it:free`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemma-4-31b-it`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemma-4-31b-it:free`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `z-ai/glm-5v-turbo`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/lyria-3-pro-preview`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/lyria-3-clip-preview`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `z-ai/glm-5-turbo`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3.1-flash-lite-preview`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3.1-flash-image-preview`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-audio`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-audio-mini`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.2-codex`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.2-chat`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.1-codex-max`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-v3.2`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-3-pro-image-preview`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.1-codex`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5.1-codex-mini`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-oss-safeguard-20b`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5-image-mini`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-5-image`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-2.5-flash-image`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-v3.2-exp`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-v3.1-terminus`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-chat-v3.1`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-oss-120b`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-oss-120b:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-oss-20b`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-oss-20b:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `anthropic/claude-opus-4.1`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `anthropic/claude-opus-4.1:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-2.5-flash-lite`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-2.5-flash`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-2.5-pro`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemini-2.5-pro-preview`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-r1-0528`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/o4-mini:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-4.1-nano`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-4.1-nano:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-chat-v3-0324`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemma-3-4b-it`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemma-3-12b-it`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemma-3-27b-it`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/o3-mini:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `deepseek/deepseek-chat`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-4o-2024-11-20`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-4o-2024-08-06`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-4o-mini-2024-07-18`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `google/gemma-2-27b-it`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-4o-2024-05-13`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-4-turbo:batch`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-3.5-turbo-0613`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-3.5-turbo-16k`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.
- `openai/gpt-4`: No unambiguous same-model counterpart among the six direct-vendor files; different versions/families are not inferred.


## AWS selected price dimensions

- Claude Fable 5; On-demand Inference; long_context=False; cache_read: SKU `22Z56KEWW97SCMCG`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 1.0 per MTok.
- Claude Fable 5; On-demand Inference; long_context=False; input: SKU `H8W3H3E6S4FWJSTK`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 10.0 per MTok.
- Claude Fable 5; On-demand Inference; long_context=False; output: SKU `QS2Z9EZ58TQJ3ND8`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 50.0 per MTok.
- Claude Fable 5; On-demand Inference; long_context=False; write1h: SKU `G8XRS7HNFT4R7J4W`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 20.0 per MTok.
- Claude Fable 5; On-demand Inference; long_context=False; write5m: SKU `JFEB858RNCE4VM7M`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 12.5 per MTok.
- Claude Fable 5.1; On-demand Inference; long_context=False; cache_read: SKU `BBRF2K84CMK6GBWT`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 0.25 per MTok.
- Claude Fable 5.1; On-demand Inference; long_context=False; input: SKU `JYVVXEBWY3NFD4NX`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 10.0 per MTok.
- Claude Fable 5.1; On-demand Inference; long_context=False; output: SKU `F79DTFXSVE378HDP`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 50.0 per MTok.
- Claude Fable 5.1; On-demand Inference; long_context=False; write1h: SKU `EGNBEEY5AS8337TZ`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 20.0 per MTok.
- Claude Fable 5.1; On-demand Inference; long_context=False; write5m: SKU `JCSMCC2X7NTGXDS9`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 12.5 per MTok.
- Claude Fable 5.2; On-demand Inference; long_context=False; cache_read: SKU `FC3Z4HBANYJ9GW9Z`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 0.2 per MTok.
- Claude Fable 5.2; On-demand Inference; long_context=False; input: SKU `TY3MW6UE5NXMT6WX`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 8.0 per MTok.
- Claude Fable 5.2; On-demand Inference; long_context=False; output: SKU `N2GTF4PEUZYC2F5S`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 40.0 per MTok.
- Claude Fable 5.2; On-demand Inference; long_context=False; write1h: SKU `JM9DZZFWNPGPUQBX`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 16.0 per MTok.
- Claude Fable 5.2; On-demand Inference; long_context=False; write5m: SKU `S9YJ2HDTB543ZUVY`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 10.0 per MTok.
- Claude Haiku 4.5; Batch Inference; long_context=False; input: SKU `T9333HTDJ5XXW7GZ`, `use1-mp:use1_inputtokencount_global_batch-units`, unit `1M tokens`, USD 0.5 per MTok.
- Claude Haiku 4.5; Batch Inference; long_context=False; output: SKU `P8DMZHZDTNRHAPMZ`, `use1-mp:use1_outputtokencount_global_batch-units`, unit `1M tokens`, USD 2.5 per MTok.
- Claude Haiku 4.5; On-demand Inference; long_context=False; cache_read: SKU `V6YWAS4REFW47M5K`, `use1-mp:use1_cachereadinputtokencount_global-units`, unit `1M tokens`, USD 0.1 per MTok.
- Claude Haiku 4.5; On-demand Inference; long_context=False; input: SKU `DY4B4Q3TRTAY8V6G`, `use1-mp:use1_inputtokencount_global-units`, unit `1M tokens`, USD 1.0 per MTok.
- Claude Haiku 4.5; On-demand Inference; long_context=False; output: SKU `XADKFYXVGBFBJSU7`, `use1-mp:use1_outputtokencount_global-units`, unit `1M tokens`, USD 5.0 per MTok.
- Claude Haiku 4.5; On-demand Inference; long_context=False; write1h: SKU `3Z3HTWANN6PKFUBJ`, `use1-mp:use1_cachewrite1hinputtokencount_global-units`, unit `1M tokens`, USD 2.0 per MTok.
- Claude Haiku 4.5; On-demand Inference; long_context=False; write5m: SKU `W4WDUUMEWN8ZMKYT`, `use1-mp:use1_cachewriteinputtokencount_global-units`, unit `1M tokens`, USD 1.25 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=False; cache_read: SKU `8FP5E8EDA6KXE8UU`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 0.01 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=False; input: SKU `CT2JY6DA5N94ZAXN`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 0.1 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=False; output: SKU `9C6E7ATQE23Q4W66`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 0.5 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=False; write1h: SKU `QMZ693GXPNRSQRMV`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 0.2 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=False; write5m: SKU `CV39UEQ78VU65KM9`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 0.125 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=True; cache_read: SKU `MDMT744HMHCN4SWC`, `use1-mp:use1_cache_read_tokens_long_ctx_global_standard-units`, unit `1M tokens`, USD 0.05 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=True; input: SKU `E7TVM9F3MW6M99X9`, `use1-mp:use1_input_tokens_long_ctx_global_standard-units`, unit `1M tokens`, USD 0.5 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=True; output: SKU `2GHZ832VV8MGPU8X`, `use1-mp:use1_output_tokens_long_ctx_global_standard-units`, unit `1M tokens`, USD 2.5 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=True; write1h: SKU `GVZFQ5E2J3BRKEG3`, `use1-mp:use1_cache_write_tokens_1h_long_ctx_global_standard-units`, unit `1M tokens`, USD 1.0 per MTok.
- Claude Haiku 5.5; On-demand Inference; long_context=True; write5m: SKU `G2KF4HARNER2AXE4`, `use1-mp:use1_cache_write_tokens_long_ctx_global_standard-units`, unit `1M tokens`, USD 0.625 per MTok.
- Claude Opus 4.7; On-demand Inference; long_context=False; cache_read: SKU `DJSZKXSZK62WK7HU`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 0.5 per MTok.
- Claude Opus 4.7; On-demand Inference; long_context=False; input: SKU `K6ATJXAP2KRY4E8C`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 5.0 per MTok.
- Claude Opus 4.7; On-demand Inference; long_context=False; output: SKU `NCFB5XVPZ7TATQNR`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 25.0 per MTok.
- Claude Opus 4.7; On-demand Inference; long_context=False; write1h: SKU `837PUVKM8JYTDVGM`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 10.0 per MTok.
- Claude Opus 4.7; On-demand Inference; long_context=False; write5m: SKU `BR4XHEJBXRMZGQ92`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 6.25 per MTok.
- Claude Opus 4.8; On-demand Inference; long_context=False; cache_read: SKU `XUG45N55868S5DRW`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 0.5 per MTok.
- Claude Opus 4.8; On-demand Inference; long_context=False; input: SKU `UF2KA578YZK6T9UE`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 5.0 per MTok.
- Claude Opus 4.8; On-demand Inference; long_context=False; output: SKU `DWUA6RYSEUDBTPA4`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 25.0 per MTok.
- Claude Opus 4.8; On-demand Inference; long_context=False; write1h: SKU `NX9E9H948HMJK3RT`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 10.0 per MTok.
- Claude Opus 4.8; On-demand Inference; long_context=False; write5m: SKU `VKQXRHDPK8NBP9SY`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 6.25 per MTok.
- Claude Opus 5; Batch Inference; long_context=False; input: SKU `RGSZ8DF5NB8ZUT8D`, `use1-mp:use1_input_tokens_global_batch-units`, unit `1M tokens`, USD 2.5 per MTok.
- Claude Opus 5; Batch Inference; long_context=False; output: SKU `JQZVTEVSX3ECK3N5`, `use1-mp:use1_output_tokens_global_batch-units`, unit `1M tokens`, USD 12.5 per MTok.
- Claude Opus 5; On-demand Inference; long_context=False; cache_read: SKU `77G6V6NH3EBMFDDE`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 0.5 per MTok.
- Claude Opus 5; On-demand Inference; long_context=False; input: SKU `NN4TW2XS9PF65MYP`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 5.0 per MTok.
- Claude Opus 5; On-demand Inference; long_context=False; output: SKU `V3ZQ2T8EG38YATXV`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 25.0 per MTok.
- Claude Opus 5; On-demand Inference; long_context=False; write1h: SKU `NXRAYDKP3P9GWEZS`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 10.0 per MTok.
- Claude Opus 5; On-demand Inference; long_context=False; write5m: SKU `928BA434K2J88YDT`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 6.25 per MTok.
- Claude Opus 5.5; On-demand Inference; long_context=False; cache_read: SKU `QT3QZUNUXV325ZDF`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 0.2 per MTok.
- Claude Opus 5.5; On-demand Inference; long_context=False; input: SKU `KVG5FBPDJPKF5TJY`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 4.0 per MTok.
- Claude Opus 5.5; On-demand Inference; long_context=False; output: SKU `MWH4TD2A4D5CEBAP`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 20.0 per MTok.
- Claude Opus 5.5; On-demand Inference; long_context=False; write1h: SKU `FBQZ4TZTVHHQMRTD`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 8.0 per MTok.
- Claude Opus 5.5; On-demand Inference; long_context=False; write5m: SKU `RVG5HJ3PZEQYVC74`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 5.0 per MTok.
- Claude Sonnet 5; On-demand Inference; long_context=False; cache_read: SKU `EFCA839SS62N88RU`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 0.2 per MTok.
- Claude Sonnet 5; On-demand Inference; long_context=False; input: SKU `YGES7RD83JWVPNKG`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 2.0 per MTok.
- Claude Sonnet 5; On-demand Inference; long_context=False; output: SKU `JEHFQVAE53BY2X97`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 10.0 per MTok.
- Claude Sonnet 5; On-demand Inference; long_context=False; write1h: SKU `3KW76RJZ3F7W8ZZ8`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 4.0 per MTok.
- Claude Sonnet 5; On-demand Inference; long_context=False; write5m: SKU `KSBHJHHKYATEYJ7G`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 2.5 per MTok.
- Claude Sonnet 5.5; On-demand Inference; long_context=False; cache_read: SKU `487WBAJQRFHYFE5M`, `use1-mp:use1_cache_read_tokens_global_standard-units`, unit `1M tokens`, USD 0.1 per MTok.
- Claude Sonnet 5.5; On-demand Inference; long_context=False; input: SKU `PXMCKMF8EGSRB3GB`, `use1-mp:use1_input_tokens_global_standard-units`, unit `1M tokens`, USD 2.0 per MTok.
- Claude Sonnet 5.5; On-demand Inference; long_context=False; output: SKU `HP32J6RXJZ3XYFUM`, `use1-mp:use1_output_tokens_global_standard-units`, unit `1M tokens`, USD 10.0 per MTok.
- Claude Sonnet 5.5; On-demand Inference; long_context=False; write1h: SKU `SW4A7584KK4SK2MK`, `use1-mp:use1_cache_write_tokens_1h_global_standard-units`, unit `1M tokens`, USD 4.0 per MTok.
- Claude Sonnet 5.5; On-demand Inference; long_context=False; write5m: SKU `CES7A5M9YH89UF9G`, `use1-mp:use1_cache_write_tokens_global_standard-units`, unit `1M tokens`, USD 2.5 per MTok.
## Lane verification

- Parsed all six written JSON files with Python standard-library json: PASS.
- Checked model-note lengths <=500, exactly one probe/default per provider, GA probes, minimum known GA probe input price, and verification date2026-11-14: PASS.
- Counts: Anthropic15 (14ga,1deprecated); Vertex14ga; Bedrock11ga.
- Full schema validation and unittest suite were intentionally left to the parent integrated candidate, as assigned. No endpoint runtime calls occurred.

## Coordinator verification corrections — 2026-11-15

Scope: the three coordinator fixes only. No network or runtime calls; no commit, tag, or push. Existing review/validation files describe the earlier candidate and are preserved. Source prices remain unchanged. Z.ai ID evidence uses the new 2026-11-15 archive; existing `verified` dates retain the 2026-11-14 pricing review date.

Long-context prices apply when the prompt's input tokens are strictly greater than `threshold_tokens`.

Normalization uses decimal K/k = 1,000 for every affected page; none defines a different token multiplier. Over/above/> N and short-context <= N map to N; >= N and "N or more" map to N - 1. OpenRouter explicitly calls its override boundary `min_prompt_tokens`: this is treated as an inclusive minimum, so its own N maps to N - 1 rather than importing a different host's threshold. The JSON supplies no additional prose definition of that field; this interpretation follows the field's minimum semantics. Direct Anthropic and Bedrock Haiku thresholds remain 100000 (prompts over 100,000); Vertex has no long_context object. Artificial fixture thresholds are unchanged.

Every changed threshold in retained records:

| Provider | Model | Before | After | Source wording / field |
| --- | --- | ---: | ---: | --- |
| openrouter | `openai/gpt-6.1-terra` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `anthropic/claude-haiku-5.5` | 100000 | 99999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-6.1-sol` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-6-luna` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-6-sol` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `x-ai/grok-4.7` | 200000 | 199999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-6-astra` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `x-ai/grok-4.6` | 200000 | 199999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-5.6-luna` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-5.6-terra` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-5.6-sol` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `x-ai/grok-4.5` | 200000 | 199999 | inclusive min_prompt_tokens |
| openrouter | `x-ai/grok-build-0.1` | 200000 | 199999 | inclusive min_prompt_tokens |
| openrouter | `x-ai/grok-4.3` | 200000 | 199999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-5.5-pro` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-5.5` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `x-ai/grok-4.20-multi-agent` | 200000 | 199999 | inclusive min_prompt_tokens |
| openrouter | `x-ai/grok-4.20` | 200000 | 199999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-5.4-pro` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `openai/gpt-5.4` | 272000 | 271999 | inclusive min_prompt_tokens |
| openrouter | `google/gemini-3.1-pro-preview-customtools` | 200000 | 199999 | inclusive min_prompt_tokens |
| openrouter | `google/gemini-3.1-pro-preview` | 200000 | 199999 | inclusive min_prompt_tokens |
| openrouter | `anthropic/claude-sonnet-4.5` | 200000 | 199999 | inclusive min_prompt_tokens |
| openai | `gpt-6-astra` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-6.1-sol` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-6.1-terra` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-6-luna` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-6-sol` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-5.6-sol` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-5.6-terra` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-5.6-luna` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-5.5` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-5.5-pro` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-5.4` | 272001 | 272000 | short <=272K / long >272K |
| openai | `gpt-5.4-pro` | 272001 | 272000 | short <=272K / long >272K |
| gemini | `gemini-3.1-pro-preview` | 200001 | 200000 | short <=200k / long >200k |
| gemini | `gemini-3.1-pro-preview-customtools` | 200001 | 200000 | short <=200k / long >200k |
| xai | `grok-4.7` | 200000 | 199999 | long >=200k |
| xai | `grok-4.6` | 200000 | 199999 | long >=200k |
| xai | `grok-4.5` | 200000 | 199999 | long >=200k |
| xai | `grok-4.3` | 200000 | 199999 | long >=200k |
| xai | `grok-4.20-0309-reasoning` | 200000 | 199999 | long >=200k |
| xai | `grok-4.20-0309-non-reasoning` | 200000 | 199999 | long >=200k |
| xai | `grok-build-0.1` | 200000 | 199999 | long >=200k |
| xai | `grok-4.20-multi-agent-0309` | 200000 | 199999 | long >=200k |

Sources: `openai-pricing.md:192`; `gemini-pricing.md:2150–2165` (also used by Custom Tools); `xai-models.md:9–26`; each retained OpenRouter record's `pricing.overrides[].min_prompt_tokens` in `openrouter-models.json`.

Removed batch-only identifiers (57); each retained base note names its route at the models-list prices:

- `google/gemini-4-hydrogen:batch`
- `google/gemini-4-carbon:batch`
- `anthropic/claude-fable-5.2:batch`
- `openai/gpt-6.1-terra:batch`
- `deepseek/deepseek-v4.1-flash-1017:batch`
- `google/gemini-4-argon:batch`
- `anthropic/claude-haiku-5.5:batch`
- `openai/gpt-6.1-sol:batch`
- `anthropic/claude-sonnet-5.5:batch`
- `openai/gpt-6-luna:batch`
- `openai/gpt-6-sol:batch`
- `anthropic/claude-opus-5.5:batch`
- `x-ai/grok-4.7:batch`
- `openai/gpt-6-astra:batch`
- `google/gemini-3.8-flash:batch`
- `anthropic/claude-fable-5.1:batch`
- `z-ai/glm-5.3-flash:batch`
- `z-ai/glm-5.3:batch`
- `x-ai/grok-4.6:batch`
- `anthropic/claude-opus-5:batch`
- `google/gemini-3.6-flash:batch`
- `google/gemini-3.5-flash-lite:batch`
- `openai/gpt-5.6-luna:batch`
- `openai/gpt-5.6-terra:batch`
- `openai/gpt-5.6-sol:batch`
- `anthropic/claude-sonnet-5:batch`
- `z-ai/glm-5.2:batch`
- `anthropic/claude-fable-5:batch`
- `anthropic/claude-opus-4.8:batch`
- `google/gemini-3.1-flash-lite:batch`
- `x-ai/grok-4.3:batch`
- `openai/gpt-5.5-pro:batch`
- `openai/gpt-5.5:batch`
- `anthropic/claude-opus-4.7:batch`
- `openai/gpt-5.4-nano:batch`
- `openai/gpt-5.4-mini:batch`
- `openai/gpt-5.4-pro:batch`
- `openai/gpt-5.4:batch`
- `google/gemini-3.1-pro-preview:batch`
- `anthropic/claude-sonnet-4.6:batch`
- `anthropic/claude-opus-4.6:batch`
- `google/gemini-3-flash-preview:batch`
- `openai/gpt-5.2-pro:batch`
- `openai/gpt-5.2:batch`
- `anthropic/claude-opus-4.5:batch`
- `openai/gpt-5.1:batch`
- `anthropic/claude-haiku-4.5:batch`
- `openai/gpt-5-pro:batch`
- `anthropic/claude-sonnet-4.5:batch`
- `openai/gpt-5:batch`
- `openai/gpt-5-mini:batch`
- `openai/gpt-5-nano:batch`
- `openai/o3:batch`
- `openai/gpt-4.1:batch`
- `openai/gpt-4.1-mini:batch`
- `openai/gpt-4o-mini:batch`
- `openai/gpt-4o:batch`

The requested schema-description regression failed before the schema change (1 test, 1 failure: missing description), then passed in the full suite.

Final verification of the corrected working-tree candidate:

- `python3 scripts/validate.py`: `18 files checked; 0 problems; clean` (exit 0).
- `python3 -m unittest discover -s tests`: `Ran 81 tests in 11.687s`, `OK` (exit 0).
- Snapshot comparison: only the authorized ID/source/probe/note/threshold edits in the five affected model files; retained prices and display names are unchanged.
- Exactly nine confirmed Z.ai API IDs, no OpenRouter batch IDs, all nine retained OpenRouter Z.ai routes have retained direct-vendor counterparts, and all 57 retained batch base notes name their route and models-list prices.
- Every provider has one GA probe at its minimum known GA input price and one GA default; the final inventory table gives all nine counts/probes/defaults (177 models total).
- Report correspondence has exactly 72 retained OpenRouter rows with confirmed Z.ai targets. All 45 threshold changes are listed above.
- Git remains uncommitted; the pre-existing R2 changes and earlier review/validation receipts are retained. No network, API call, commit, tag, or push was performed. Coordinator acceptance remains separate.

## Verification and review boundary

Final validator, full unittest suite, provider-summary command, source/provenance checks, retained review findings, candidate hashes and Git status are recorded in the R2 handoff. A clean validator is structural evidence, not a live endpoint check. Coordinator acceptance/checkpoint is separate; this lane does not admit R3.

## Historical blocked source audit (preserved verbatim)

# R2 seed-data source audit — blocked

Date: 2026-11-14. Dev mode: mvp.
Lane: `48b0c705-eb19-4870-a36a-e4db503a127a`.

## Outcome

R2 is blocked before writing provider or model records. No seed data is complete,
and no model counts, probes, defaults, or null inventories have been established.
The lane used only the coordinator's archived files in `.research/2026-11-14/`;
it made no network requests and performed no commit, tag, or push.

## Blocking source gap: DeepSeek authentication

The brief requires all written values to come from the archived files, with URLs
from `SOURCES.md`, and specifically requires checking each provider's base URL and
authentication against its source file. The only archived DeepSeek vendor page is
`deepseek-pricing.html`, mapped to
<https://api-docs.deepseek.com/quick_start/pricing>.

That page documents `https://api.deepseek.com`, the alternative Anthropic-format
URL `https://api.deepseek.com/anthropic`, model prices and limits, and support for
the Responses API. It does not document an authentication mechanism. In
particular, searches for `Authorization`, `Bearer`, `x-api-key`, `api_key`,
`API key`, and `authentication` find no occurrences in the raw HTML. Reading the
HTML text and searching the other archived pages did not produce a direct
DeepSeek authentication example.

`schema/provider.schema.json` makes `auth` mandatory and restricts it to
`x_api_key`, `bearer`, `google_api_key`, `aws_sigv4`, or `gcp_oauth`. It cannot
represent unknown authentication. Writing `bearer` from the task's provider table
would violate the stricter requirement that every value be read from a source
file. Substituting another vendor's Bearer example would not establish DeepSeek's
authentication either. The lane did not invent a value or change the schema.

**Coordinator decision needed:** supply an archived official DeepSeek
authentication page and its URL mapping, or explicitly authorize the task's
DeepSeek `bearer` value as an exception to the archive-only rule. Then resume R2
and complete every provider, model, source/null inventory, documentation update,
and verification required by the original brief.

## Preliminary findings to preserve for resumption

These are source-audit findings, not completed registry entries or a complete
inventory of exclusions and schema gaps.

- `ep-gemini.md`, mapped to <https://ai.google.dev/gemini-api/docs/quickstart>,
  documents `https://generativelanguage.googleapis.com/v1beta/interactions` with
  `x-goog-api-key`. `generateContent` does not appear. Schema v1 has
  `gemini_generate` but no Interactions protocol. The original brief explicitly
  requires recording this endpoint difference in a provider note and the final
  result.
- `ep-bedrock-claude.md`, mapped to
  <https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock>,
  documents the Messages API at
  `https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages` and gives
  `https://bedrock-mantle.{region}.api.aws/anthropic` as the client base URL. Its
  SigV4 example signs for `bedrock-mantle`. Converse and InvokeModel belong to
  the separate `bedrock-runtime` legacy route. A mantle record must not claim
  Converse compatibility; `anthropic_messages` is an existing schema value.
  Fable 5.2 is explicitly runtime-only and cannot be mixed into a mantle-only
  provider without recording that endpoint limitation.
- `openai-pricing.md`, mapped to <https://developers.openai.com/api/docs/pricing>,
  orders its extended standard table as input, output, cached input, 30-minute
  write, 12-hour write, then the corresponding long-context columns. Schema v1's
  5-minute and 1-hour write fields cannot stand in for those durations.
- `gemini-pricing.md`, mapped to <https://ai.google.dev/gemini-api/docs/pricing>,
  distinguishes per-token cache access from hourly storage, and contains
  time-limited prices and separate audio-input prices. Those conditions cannot
  all be represented by one schema-v1 token-price tuple.
- `zai-pricing.md`, mapped to <https://docs.z.ai/guides/overview/pricing>, labels
  cached-input **storage** as limited-time free. Schema v1 has no storage-price
  field; that fact alone does not document writes with 5-minute or 1-hour TTLs.
- `gcp-partner-pricing.txt`, mapped to
  <https://cloud.google.com/model-garden/partner-models/pricing>, lists global
  Opus 5.5 input/output at $4/$20 and batch input/output at $2.50/$12.50 per
  million tokens. These imply 37.5% discounts for input/output, whereas the same
  section's batch cache prices are half its standard cache prices. The brief
  requires `batch_discount_percent: null`; preserve the raw values and explain
  the distinction when seeding.
- `.gitignore` already contains `.research/`; no ignore change is needed.

## Verification boundary

The source-gap checks and empty-tree validator result are reported in the lane's
final handback. A clean empty registry is not R2 acceptance. The unittest suite
was not run for this source-only blocker handback; no validator, schema, test,
provider, or model files were changed. Full requested R2 verification remains due
after the source gap is resolved and the seed data is written.

