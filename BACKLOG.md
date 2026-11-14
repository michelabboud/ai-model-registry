# Backlog

- 2026-11-15 — R2 coordinator verification — Source: coordinator fix brief. Done locally: nine providers and 177 model records after API-ID, batch-route and threshold corrections; validator clean (18 files, 0 problems) and 81 passing tests. Coordinator acceptance/checkpoint remains pending.
- 2026-11-14 — R3 — Source: current coding-CLI harness brief. Done locally: required protocol contract and 13 sourced records; 31 files validate clean and 89 tests pass. Research gaps are enumerated below. Coordinator review/checkpoint remains separate.
- 2026-11-14 — R4 — Source: R1 brief and upstream plan. Open: define release payload and key distribution, build manifest/signature/archive tooling, and publish verified `registry/<N>` releases; signing never in CI.
- 2026-11-14 — R5 — Source: R1 brief and upstream plan. Open: vendor list-API work, including documenting environment key names only in `.env.example`.
- 2026-11-14 — M1 — Source: approved upstream registry plan. Open: consumer integration and its acceptance evidence, starting with The Operator; Genie follows later.

See [PLAN.md](PLAN.md) for the authoritative plan link. These are later approved-plan
items owned by the coordinator, not work silently omitted from R1.

- 2026-11-14 — R2 source audit — Open: time-of-day pricing (DeepSeek peak/off-peak schedules and holidays) is not expressible in schema v1; baseline is peak and notes retain the schedule.
- 2026-11-14 — R2 source audit — Open: regional/multi-region pricing premiums, residency/FedRAMP uplifts, and endpoint geography are not structured by schema v1; seed prices use documented global/standard scope.
- 2026-11-14 — R2 scope — Open: Gemini models on Vertex are not yet listed; Vertex seed covers Claude only.
- 2026-11-14 — R2 scope — Open: non-Anthropic models on Bedrock are not yet listed.
- 2026-11-14 — R2 GCP pricing source — Open: Google's Opus 5.5 batch input/output $2.50/$12.50 conflict with a uniform all-category discount; the percentage stays null and the raw rates remain in notes.
- 2026-11-14 — R2 source audit — Open: promotion windows, future prices, service-speed tiers, modality-specific token prices, tools/session fees, and batch cache/storage exceptions need richer tariffs; notes preserve the sourced conditions.
- 2026-11-14 — R2 source audit — Open: provider protocol lists cannot express per-model endpoint restrictions (Bedrock runtime-only Fable 5.2, Gemini Live-only Robotics Streaming); model/provider notes name the limitations.
- 2026-11-14 — R2 source audit — Open: generic OpenRouter `input_cache_write` has no TTL/unit-of-time metadata; raw converted values remain in model notes rather than inventing a TTL or hourly storage mapping. Generic `file` input also cannot be narrowed to schema-v1 `pdf` safely.
- 2026-11-15 — R2 Z.ai API-reference audit — Source: `zai-chat-completion.md`. Open: `GLM-4.7-FlashX`, `GLM-4.5`, `GLM-4.5-X`, `GLM-4.5-Air`, `GLM-4.5-AirX`, `GLM-4-32B-0414-128K`, `GLM-4.7-Flash`, `GLM-4.5-Flash`, `GLM-4.6V`, `GLM-4.6V-FlashX`, `GLM-4.5V`, `GLM-4.6V-Flash` — id not confirmed by API reference; excluded pending explicit callable-ID evidence. Nine enum-confirmed lowercase API IDs are retained.
- 2026-11-14 — R2 source audit — Open: archived cloud-Claude identifiers/lifecycles are incomplete, including Google deprecated models without Google shutdown dates; do not substitute Anthropic-host retirement dates or fabricate older Bedrock IDs.
- 2026-11-15 — R2 OpenRouter Z.ai correspondence — Source: coordinator verification / Z.ai API model enum. Open: `z-ai/glm-4.7-flash`, `z-ai/glm-4.6v`, `z-ai/glm-4.5v`, `z-ai/glm-4.5`, `z-ai/glm-4.5-air` — id not confirmed by API reference; excluded because no retained direct-vendor counterpart exists.

## R3 research gaps

All items below are **UNVERIFIED**, from the coordinator's 2026-11-14 harness
research. They are excluded from factual record fields; resolving them can enrich
records or consumers' integration/asset choices. No network verification ran in R3.

- 2026-11-14 — R3 / Codex — Open, UNVERIFIED: `OPENAI_BASE_URL` environment override; maintainer comment alone was not accepted as documentation of support.
- 2026-11-14 — R3 / Codex — Open, UNVERIFIED: `OPENAI_API_KEY` name in the consulted Codex docs; no API-key environment role is inferred.
- 2026-11-14 — R3 / Codex — Open, UNVERIFIED: `CODEX_API_KEY` name in the consulted Codex docs; no API-key environment role is inferred.
- 2026-11-14 — R3 / OpenCode v1 — Open, UNVERIFIED: exact `--version` output format; major matching accepts a version token without claiming a verified full banner.
- 2026-11-14 — R3 / OpenCode v2 — Open, UNVERIFIED: `--model`/`-m` flag; `model_flag` stays null.
- 2026-11-14 — R3 / OpenCode v2 — Open, UNVERIFIED: v2.0.x/v2.1.x GitHub release existence; no release-history claim is recorded.
- 2026-11-14 — R3 / OpenCode v1 — Open, UNVERIFIED: `@ai-sdk/anthropic` custom-baseURL support; Anthropic Messages is omitted from this harness.
- 2026-11-14 — R3 / Aider — Open, UNVERIFIED: Anthropic base URL override; only OpenAI Chat Completions is recorded.
- 2026-11-14 — R3 / Copilot — Open, UNVERIFIED: `COPILOT_PROVIDER_BASE_URL` name; excluded along with all legacy `COPILOT_PROVIDER_*` mappings under the brief.
- 2026-11-14 — R3 / Copilot — Open, UNVERIFIED: `COPILOT_PROVIDER_TYPE` name; excluded along with all legacy `COPILOT_PROVIDER_*` mappings under the brief.
- 2026-11-14 — R3 / Copilot — Open, UNVERIFIED: exact `providers.json` JSON nesting; the record names the file and transport selectors without inventing a snippet.
- 2026-11-14 — R3 / OpenHands — Open, UNVERIFIED: Agent Canvas npm package as a maintained successor; no installation or replacement recommendation is recorded.
- 2026-11-14 — R3 / OpenHands — Open, UNVERIFIED: `agent_settings.json` field names; no provider config shape is asserted.
- 2026-11-14 — R3 / OpenHands — Open, UNVERIFIED: custom-baseURL wire protocol; adapter remains `detect_only` with `protocols: []`.
- 2026-11-14 — R3 / OpenClaw — Open, UNVERIFIED: `api` values beyond `openai-completions` and `anthropic-messages`, including Responses and Gemini; no extra protocols are declared.
- 2026-11-14 — R3 / Antigravity — Open, UNVERIFIED: `antigravity` binary/launcher name; only `agy` is recorded.
- 2026-11-14 — R3 / Antigravity — Open, UNVERIFIED: release date of CLI v1.5.8; no release date is recorded.
- 2026-11-14 — R3 / Grok Build — Open, UNVERIFIED: `api_backend` default in docs.x.ai; transport choices are recorded without assigning a default.
- 2026-11-14 — R3 / Grok Build — Open, UNVERIFIED: release date; local version evidence does not supply a release date.
- 2026-11-14 — R3 / Muse Code — Open, UNVERIFIED: custom-endpoint wire protocol; adapter stays `detect_only` with `protocols: []`.
- 2026-11-14 — R3 / Muse Code — Open, UNVERIFIED: `settings.json` provider keys; no custom-provider config shape is asserted.
- 2026-11-14 — R3 / Muse Code — Open, UNVERIFIED: bearer-token behavior on a non-Meta base URL; no gateway authentication mapping is claimed.
- 2026-11-14 — R3 / Muse Code — Open, UNVERIFIED: release date; omitted from the record.
- 2026-11-14 — R3 / Muse Code — Open, UNVERIFIED: official Muse-specific logo; `meta` is an app-neutral identifier, not a supplied asset.
- 2026-11-14 — R3 / Anthropic — Open, UNVERIFIED: brand-usage terms; `claude-code` grants no asset or trademark license.
- 2026-11-14 — R3 / OpenAI — Open, UNVERIFIED: brand-usage terms; `openai` grants no asset or trademark license.
- 2026-11-14 — R3 / xAI — Open, UNVERIFIED: brand-usage terms; `xai` grants no asset or trademark license.
- 2026-11-14 — R3 / Nous — Open, UNVERIFIED: brand-usage terms; `hermes-agent` grants no asset or trademark license.
- 2026-11-14 — R3 / OpenClaw — Open, UNVERIFIED: brand-usage terms; `openclaw` grants no asset or trademark license.
- 2026-11-14 — R3 / OpenHands — Open, UNVERIFIED: brand-usage terms; `openhands` grants no asset or trademark license.
- 2026-11-14 — R3 / Aider — Open, UNVERIFIED: brand-usage terms; `aider` grants no asset or trademark license.
- 2026-11-14 — R3 / OpenCode v2 — Open, UNVERIFIED: native custom-endpoint Responses routing is not independently established by the research; v1 config acceptance alone is not treated as a v2 protocol guarantee.

- 2026-11-15 — R3 editor diagnostic — Open, UNVERIFIED attribution: basedpyright reported bool/int not iterable at the validator CLI report loop; the loop and report construction are unchanged from HEAD. No standalone baseline type-check was run; required validator/unittest gates pass. Assess the annotation/inference issue separately before claiming a type-check pass.
