# Backlog

- 2026-11-15 — R2 coordinator verification — Source: coordinator fix brief. Done locally: nine providers and 177 model records after API-ID, batch-route and threshold corrections; validator clean (18 files, 0 problems) and 81 passing tests. Coordinator acceptance/checkpoint remains pending.
- 2026-11-14 — R3 — Source: approved upstream registry plan. Open: execute its specified registry task; full scope was not supplied to R1 and is not invented here.
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
