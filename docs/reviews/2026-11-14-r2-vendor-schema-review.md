# R2 vendor-schema review and repair adjudication — 2026-11-14

Dev mode: mvp. No release or live API qualification. Fresh-context native same-family reviewer; source snapshots were content-hashed because the lane forbids commits. Runtime provider identity, token use and independently measured queue latency are unavailable.

Requested configuration: gpt-6.1-sol / xhigh.

Coordinator disposition: confirmed actionable finding repaired and independently rechecked. Source limitations remain documented in the seed report/backlog; they are not fabricated as resolved. All final validation input hashes match the reviewed original and repair snapshots.

## Original independent report (preserved)

# CONFIRMED / REFUTED / UNVERIFIED — independent R2 review

## Cold-read findings

### CONFIRMED — P2 — Existing-user-only Gemini 2.5 models violate the ungated inclusion rule

- Candidate: `models/gemini.json`, `/models/9` (`gemini-2.5-pro`), `/models/10` (`gemini-2.5-flash`), `/models/11` (`gemini-2.5-flash-lite`); the latter has `/probe: true`.
- Source: `sources/gemini-models.md:276-284`, Gemini 2.5 Flash-Lite note, mapped to https://ai.google.dev/gemini-api/docs/models. It explicitly limits access to the 2.5 models to users who actively used them in the past. Flash-Lite remains served and not deprecated, but it is access restricted. Each candidate's own note also acknowledges existing-user-only access.
- Impact: a new Gemini account/project can fail the selected connectivity probe despite a valid credential and endpoint. Keeping the other restricted 2.5 records also contradicts the brief's exclusion of gated models.
- Action: exclude all three restricted 2.5 records and recompute the probe among remaining GA text models with published input prices. In this snapshot, `gemini-3.1-flash-lite` at $0.25/MTok is the cheapest eligible remaining entry. Recheck dependent catalog matches separately.
- Coordinator response: accepted during review; repairs are pending outside this immutable snapshot. I did not inspect or accept repaired working-tree bytes.

### CONFIRMED omission / UNVERIFIED required lifecycle value — Vertex legacy coverage limitation

- Candidate: `models/vertex.json`, `/models`; missing `claude-opus-4-1@20250805`, `claude-opus-4@20250514`, `claude-sonnet-4-5@20250929`, and `claude-sonnet-4@20250514`.
- Source: `sources/ep-vertex-claude.md:304-310` gives these exact API IDs and marks them deprecated. `:314-316` says regional availability varies and Google owns lifecycle dates, which can differ from Claude API dates. Mapped URL: https://platform.claude.com/docs/en/build-with-claude/claude-models-on-google-cloud/google-managed. `sources/anthropic-pricing.md:29-35` explicitly distinguishes models still available on Google managed from first-party retirement.
- Impact: this candidate does not cover every still-serving deprecated Google-managed Claude ID. First-party shutdown dates cannot safely fill the missing Google dates.
- Constraint: `schema/models.schema.json` requires a real shutdown date for deprecated records; these Google dates are absent from the allowed archive. No source-backed complete record can be created without resolving that missing field. Under the coordinator's clarified source-gap omission rule, this is an allowed omission and a coverage limitation, not a request to guess dates or expand R2's schema scope.
- Action: retain the four exact omitted IDs and the unavailable Google retirement-date evidence in the final coverage record/backlog. Do not describe Vertex as a complete still-serving catalog.

## Batch discount assessment

REFUTED: the reviewed `batch_discount_percent: 50` values are not incorrect when the field means the discount on input and output token prices. No existing per-model note falsely claiming that all cache/storage categories halve was found. The scalar must be documented as input/output-only; it cannot safely generate an entire Batch pricing tuple.

| Candidate location | Source and precise consequence |
|---|---|
| Gemini `/models/7` and `/models/14`, Pro Preview and customtools | `sources/gemini-pricing.md`, Gemini 3.1 Pro Preview Standard/Batch sections (`:2115-2375`): input/output halve; cached input explicitly remains Standard, as the current notes say. Storage remains $4.50/MTok-hour. |
| Gemini `/models/8`, 3 Flash Preview | Same source, Gemini 3 Flash Preview (`:3030-3262`): input/output halve; cached input explicitly remains Standard. Current note is accurate. Storage remains $1/MTok-hour. |
| Gemini `/models/3`, `/models/4`, `/models/5`, `/models/12`, 3.8/3.6 Flash, 3.5 Flash-Lite, Robotics ER 2 | Their Standard/Batch source sections show halved cache-read prices but unchanged hourly storage. Examples: 3.8 Flash cache $0.075 to $0.0375, storage $0.50 in both; 3.5 Flash-Lite cache $0.03 to $0.015, storage $1 in both. A global rule halving all stored prices would understate storage costs. |
| Gemini `/models/6`, 3.1 Flash-Lite | Same source, Gemini 3.1 Flash-Lite (`:1883-2114`): cached text input halves $0.025 to $0.0125 and storage also halves $1 to $0.50. This prevents treating every Gemini model's storage as unchanged. |
| OpenAI `/models/10`, GPT-5.4 | `sources/openai-pricing.md:45,91`: input $2.50 to $1.25 and output $15 to $7.50 are exactly 50%; the published short-context cached Batch price is rounded to $0.13 from Standard $0.25. Deriving $0.125 would disagree with the archived displayed rate. |
| Vertex `/models/3`, Opus 5.5 | GCP global table: Standard input/output $4/$20, Batch $2.50/$12.50, while cache categories halve. Null is the correct single-discount representation under the brief. Current note/null preserves the inconsistency. |

The source Standard values in the candidate remain correct. Documenting the field's input/output scope centrally resolves the ambiguity; repeated cache overrides or a new pricing schema are not required by this review. The soon-to-be-excluded Gemini 2.5 rows also correctly noted Standard cached-input pricing in Batch.

## Refuted hypotheses and checked areas

- REFUTED cache-contract regression: required `cache_writes`, length 0-6, closed `{ttl, price}` records, exact requested TTL regex, nonnegative-or-null prices/storage, optional hourly storage, and schema version 1 are present. Semantic TTL uniqueness is applied independently to Standard and long-context arrays, including duplicate TTLs with different prices.
- REFUTED protocol broadening outside the requested enum: provider and optional harness protocol arrays accept `gemini_interactions` while rejecting unknown/duplicate values. The harness field remains optional. Bare-command and denied-environment-name/prefix restrictions remain independently enforced by validator semantics.
- REFUTED OpenAI cache TTL/unit transcription error: Standard pricing rows `openai-pricing.md:33-46` support the 30m/12h write entries and long-context amounts. Other unknown write rates remain empty. Unknown context/output limits remain null instead of borrowing unarchived model-card values.
- REFUTED Gemini storage-as-write transcription: Gemini hourly rates are stored only in `cache_storage_per_mtok_hour`, with empty write arrays; Standard token tuples and current promotional rates match the relevant sections. Gemini 4 max output 1M is explicitly the published maximum of the source's 64K / 1M notation, with a note preserving that distinction.
- REFUTED DeepSeek peak/alias/vision error: archived pricing table supports Flash $0.30/$1.20/$0.006 and Pro $1.32/$3.96/$0.044, 1M context, maximum 384K output, and Flash-only vision. Source says legacy Flash names route to the current Flash model after the old models retired. Provider note records this; the coordinator's announced model-note addition was not in this snapshot and was not inspected. No duplicate retired records are required.
- REFUTED xAI threshold and Batch transcription: `xai-models.md` uses greater-than-or-equal 200k and the candidate preserves 200000, unlike the strictly-above thresholds of other vendors. Decoded official HTML metadata supports candidate context/modalities and `batchEnabled: true` plus 20% for seven models. Grok Build has a discount field but lacks Batch enablement; keeping its discount null is justified. No output limit was inferred from `maxPromptLength`.
- REFUTED cloud regional/price-unit mixup for included records: first global GCP table supports the candidate's rates and explicit unknown Opus 4.5 one-hour write tariff. AWS selected global Standard rows use `1M tokens`; their values match the included models, including Haiku 5.5 long-context rates. Haiku 4.5 global input/output Batch $0.50/$2.50 versus Standard $1/$5 supports 50%. Regional rows are distinct and correctly not substituted.
- REFUTED endpoint/auth mismatch within documented provider scope: archive supports Anthropic Bearer with legacy x-api-key fallback; Gemini v1beta Interactions plus Api-Revision and separately documented generateContent; DeepSeek OpenAI base with Anthropic on a separate base; Z.AI standard v4 chat and Bearer; xAI Responses; Vertex global rawPredict and OAuth; Bedrock mantle Messages base and SigV4 service `bedrock-mantle`. Fable 5.2 runtime-only routing remains explicitly noted, as requested by the brief.

## Unverified source boundaries

- Z.AI `models/zai.json` `/models/1` (`GLM-5.3-Flash`) has text-only modalities. `sources/ep-zai.md:36-38` calls it a multimodal coding model specializing in visual programming, but the archive does not enumerate exact image/video input formats. This supports an uncertainty note, not inventing a particular modality. Remaining uppercase table-label API IDs are also explicitly caveated in the candidate; their case-sensitive API behavior cannot be established from this archive alone.
- Bedrock source endpoint table establishes the mantle model subset and flags Fable 5.2 as runtime-only. Old product names in the AWS price catalog alone do not prove currently callable IDs, ungated access, or lifecycle, so I did not manufacture legacy Bedrock additions from price rows.
- No network, credentials, live API inference, vendor account eligibility, performance benchmark, or repaired working-tree acceptance was performed. Source statements are archive-bound to the 2026-11-14 evidence, not current live verification.

## Candidate identity and focused verification

Candidate: `/home/michel/projects/ai-model-registry/.research/r2-review-852ee9b6`.
Manifest SHA-256: `01d2bf2e7ffca2e8837d4d7461770af39fd09d8a5679c4e46d01801662b5e63a`.
All 83 manifest entries matched their hashes at the initial check. End-of-review manifest recheck also reported no mismatches.

Independent focused command, run from the snapshot with bytecode writes disabled:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_cache_pricing.py -v
Ran 7 tests in 0.045s
OK
```

I read the snapshot schema/validator, all eight provider/model datasets (120 model records), and the mapped official archived sources relevant to their claims. This is a source review plus seven focused contract tests, not a second execution of the coordinator's full suite. No source was edited, no Git operation/network/install/cleanup was performed, and no other review notes or moving-tree data were read.

## Independent repair recheck (preserved)

# CONFIRMED / REFUTED / UNVERIFIED — independent R2 repair recheck

Requested configuration: `gpt-6.1-sol` at `xhigh`.
Runtime model identity and token usage were not independently measured.

Verdict: the confirmed Gemini gating defect is repaired in this pinned patch. No new actionable defect was confirmed in the affected files. This accepts the bounded repairs and their source-backed notes, not a full-suite run, live vendor API compatibility, or dependent OpenRouter data.

## CONFIRMED — original P2 repaired

`models/gemini.json` now contains 15 models. All three existing-user-only 2.5 records (`gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`) are absent. The sole probe is `/models/6`, `gemini-3.1-flash-lite`, GA at $0.25/MTok input. A focused computation over every remaining GA entry with known input price confirms this is the lowest input price. The default remains `gemini-3.8-flash`.

This resolves the original finding against `sources/gemini-models.md:279-284`, which limits 2.5-family access to prior active users. No restricted 2.5 alias was reintroduced into this patch's Gemini collection. Dependent OpenRouter data was not supplied in the patch and was not accepted here.

## CONFIRMED — pricing notes and central semantics agree with the archive

- `README.md:124` explicitly limits `batch_discount_percent` to input/output, rejects automatic extrapolation to cache/storage/context bands, and directs readers to the notes. This resolves the interpretation risk identified in the first review without changing the data contract.
- `models/openai.json`, `gpt-5.4` `/models/10/note`, preserves the published $0.13 short-context Batch cached price instead of deriving $0.125 from Standard $0.25. The exact source rows are `sources/openai-pricing.md:45,91`.
- The `gpt-5.5-pro` `/models/9/note` correctly limits the summarized discount to short-context input/output; the archived long-context Batch columns are unpublished (`openai-pricing.md:44,90`). The changed GPT-4.1, GPT-4.1 Mini, GPT-4o, GPT-4o Mini, and o3 notes correctly distinguish halved input/output from their unpublished Batch cached-input columns (`:94-110`). No claim that those cached prices are free or derivable was added.
- `models/gemini.json`, `/models/3`, `/models/4`, `/models/5`, `/models/9` notes accurately preserve unchanged Standard storage for 3.8 Flash, 3.6 Flash, 3.5 Flash-Lite, and Robotics ER 2 Batch. The original archived pricing sections support those exceptions; for example 3.8 storage is $0.50/MTok-hour in both Standard and Batch (`gemini-pricing.md:870,922`), and 3.5 Flash-Lite storage is $1 in both (`:1439,1494`).
- Gemini `/models/6/note` correctly records the different 3.1 Flash-Lite storage case: Standard $1 versus Batch $0.50/MTok-hour (`gemini-pricing.md:1932,1982`). Existing Pro Preview/customtools and 3 Flash Preview notes still correctly say cached input remains Standard.
- `models/deepseek.json`, `/models/0/note`, now names current version `DeepSeek-V4.1-Flash-1017` and both legacy aliases. Archived `deepseek-pricing.html`, Model Details footnote (1), and `ep-deepseek.html`, first-call model note, explicitly support that routing and retirement distinction. No extra retired model record was created.
- `models/zai.json`, `/models/1/note`, now records the exact source uncertainty: the quickstart calls GLM-5.3-FLASH multimodal/visual coding (`ep-zai.md:36-38`) but does not enumerate visual input formats. The patch correctly adds no guessed image/video modality or limit.

REFUTED: no incorrect numeric discount, cache/storage price, fabricated limit, or misleading new note was found in these repairs. Vertex Opus 5.5's null discount and the four source-constrained Vertex omissions were unchanged and were not rescanned.

## xAI legacy protocol evidence and its limit

CONFIRMED: the original official `sources/xai-models.html` contains this navigation entry twice:

```html
<a href="/developers/model-capabilities/legacy/chat-completions">...Chat Completions (Legacy)...</a>
```

The archived file is mapped to https://docs.x.ai/docs/models. Its surrounding navigation is the provider's model-capability documentation. This supports a provider-level legacy Chat Completions family, alongside Responses directly demonstrated by `sources/ep-xai.md:64-71,78-80`.

`providers/xai.json` `/protocols` now lists `openai_chat` and `openai_responses`; `/note` accurately identifies that the Chat evidence is an archived navigation link. It does not claim a demonstrated legacy request, a specific legacy route, or universal compatibility across listed models. `README.md` explicitly says a provider protocol list is not a claim that every model supports every endpoint. The narrowly qualified metadata claim is supported; no additional operational claim should be inferred from it.

UNVERIFIED: the linked legacy documentation body was not archived. Exact legacy request/response shape, route, model support, and current live availability cannot be independently established from the allowed source contents. No network or inference probe was used to fill that gap. This limitation does not establish that the listed protocol is wrong.

## Other affected provider claims

- Gemini's unversioned provider root plus explicit `/v1beta` note matches the requested representation. The archive demonstrates both versioned endpoint families: `ep-gemini.md:176-179` for Interactions with its revision header and `gemini-generate-content.md` for generateContent. The note retains the Live-only Robotics exception.
- Z.AI's trailing-slash normalization and display spelling introduce no contrary vendor claim; the archived quickstart shows `https://api.z.ai/api/paas/v4/chat/completions` and Bearer auth.
- Added OpenAI pricing, Bedrock AWS catalog, and Gemini model/pricing source URLs match the original `sources/SOURCES.md` mapping and support the provider notes they accompany.

## Candidate and focused evidence

Patch snapshot: `/home/michel/projects/ai-model-registry/.research/r2-repairs-review-852ee9b6`.
Patch manifest SHA-256: `14327e59a84392c7d2550e64d94d18cf0020e6d0b5a49db5ab694bc59a0096e8`.
All 11 listed payload hashes matched. Original comparison/source snapshot: `/home/michel/projects/ai-model-registry/.research/r2-review-852ee9b6`, whose manifest was verified in the initial review.

Focused check: loaded the original pinned validator with bytecode writes disabled, checked both original provider/model schemas, and ran structural plus semantic validation on the patch's five provider objects and four model collections at source date 2026-11-14. Result:

```text
9 affected JSON files: each errors []
GEMINI2.5 IDS []
GEMINI MODEL COUNT 15
GEMINI PROBE [('gemini-3.1-flash-lite', 'ga', 0.25)]
CHEAPEST GA KNOWN (0.25, 'gemini-3.1-flash-lite')
TOTAL AFFECTED JSON ERRORS 0
```

No full rescan or full suite was run because schema, validator, and tests were unchanged and the coordinator owns that gate. No moving-tree data, other review reports, network, Git mutation, installation, or cleanup was used. Only this report was written.
