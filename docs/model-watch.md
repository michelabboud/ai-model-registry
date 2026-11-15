# Weekly text-model watch

Dev mode: `mvp`. R5 adapts Michel's own
[`genie-registry` model-watch design](https://github.com/michelabboud/genie-registry/blob/main/docs/model-watch.md).
The implementation is Python 3.11+ standard library only. It produces proposals;
it does not verify vendor facts or publish registry data.

## What it compares

The watch lists each configured vendor's models and compares the admitted IDs
with `models/<provider>.json`. An ID is new when it is listed, survives that
vendor's text-family filters, and is absent from the model file. An existing
`ga` or `preview` model is missing when it appears nowhere in that vendor's
complete listing. Deprecated records are not proposed as missing.

For a missing model: **Confirm the retirement in the vendor's deprecation notes
before removing it; a key without access to a model also hides it.** A listing
omission is a prompt to check, not a fact of retirement.

The only proposed files are `candidates/<provider>.md`. Every proposed field is
`TO VERIFY`; the worksheet links the official `docs_url` from
`providers/<provider>.json` and sources already cited in that provider's model
records, including its pricing source. Those links are starting points for human
verification, not evidence that a newly listed ID has the same price or limits.
No sibling model's prices or limits become proposed facts.
Where a record's pricing reference is a model overview, as with the existing
xAI source, the watch keeps that cited URL rather than inventing a separate
pricing page.

`candidates/` is ignored on `main`. The PR job explicitly adds only the six known
worksheet filenames to the watch branch; it does not alter the ignore rule.
The watch never edits `providers/` or `models/`, never signs, never creates a
release, and never pushes `main`. The production signing key is never in CI.

## Vendor policy

All vendor-specific endpoint, header, secret, pagination, and exclusion policy
lives in `VENDORS` in `scripts/model_watch.py`.

| Provider | GET endpoint | Authentication headers | Repository secret | Response policy |
| --- | --- | --- | --- | --- |
| `openai` | `https://api.openai.com/v1/models` | `Authorization: Bearer` | `OPENAI_MODELS_KEY` | `data` array of IDs; no inferred capability field. |
| `anthropic` | `https://api.anthropic.com/v1/models?limit=1000` | `x-api-key`; `anthropic-version: 2023-06-01` | `ANTHROPIC_MODELS_KEY` | **UNVERIFIED:** `data`, `has_more`, and `last_id`; follow the cursor while `has_more` is true. |
| `gemini` | `https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000` | `x-goog-api-key` | `GEMINI_MODELS_KEY` | `models` array; follow `nextPageToken`; require `supportedGenerationMethods` to contain `generateContent`. |
| `xai` | `https://api.x.ai/v1/models` | `Authorization: Bearer` | `XAI_MODELS_KEY` | **UNVERIFIED:** `data` array of IDs; never fall back to Genie's image endpoint. |
| `deepseek` | `https://api.deepseek.com/models` | `Authorization: Bearer` | `DEEPSEEK_MODELS_KEY` | **UNVERIFIED:** `data` array of IDs. |
| `openrouter` | `https://openrouter.ai/api/v1/models` | None; public endpoint | None | `data` array; only the approved vendor prefixes below. Always checked. |

The supplied Anthropic, DeepSeek, and xAI response shapes are **UNVERIFIED**
until a first successful live run confirms them. The coordinator owns that live
check; R5 performs no network access. Unexpected shapes fail the affected vendor
visibly, fail the run, and prevent PR publication. The code does not guess an
alternate envelope, ID field, or endpoint.

Z.ai, Vertex, and Bedrock are not watched in R5. No documented, key-scoped list
endpoint verified for this task was supplied; each has a separate backlog entry.

Anthropic requires a Boolean `has_more` and, when it is true, a `last_id` that
matches the final entry's ID. Gemini requires a `name` field and, for admitted
IDs, a string array of `supportedGenerationMethods`. A name without the
`models/` prefix is an invalid ID: it is dropped and counted without echoing it.
Missing arrays, model-entry keys, generation-method arrays for admitted IDs, or
pagination indicators are response-shape errors rather than an empty listing.

### Text-family filters

The filters are a small, explicit list in each vendor's `VENDORS` entry, with
fixture tests. They exclude known embedding, image-generation, audio/TTS/Whisper,
moderation, realtime-only, and OCR name families. Exclusions identify non-text
routes, not multimodal text models: an image-input chat model can still produce
text. A surviving name is only a candidate and does not establish capabilities.

The shared case-insensitive token pattern excludes the following complete
family tokens, bounded by the start/end of the ID or `-`, `_`, `.`, `/`, or `:`:

```text
embed, embeds, embedding, embeddings, image, imagegen, imagegeneration, audio, tts,
whisper, moderation, realtime, ocr, transcribe, transcription, speech, video
```

| Provider | Additional exclusion / admission policy |
| --- | --- |
| OpenAI | Exclude `^(?:dall-e\|sora)(?:[-_.]\|$)` families. |
| Anthropic | Shared family-token exclusions only. |
| Gemini | Exclude `^(?:imagen\|veo)(?:[-_.]\|$)` families after stripping `models/`; require `generateContent`. |
| xAI | Shared family-token exclusions only. |
| DeepSeek | Shared family-token exclusions only. |
| OpenRouter | Additionally exclude `^(?:openai/)?(?:dall-e\|sora)(?:[-_.]\|$)` and `^google/(?:imagen\|veo)(?:[-_.]\|$)` families. Admit only `openai/`, `anthropic/`, `google/`, `deepseek/`, `z-ai/`, and `x-ai/` prefixes; never `:batch` IDs. |

Vertical bars in the table's regular expressions are escaped for Markdown;
the code uses ordinary regex alternation. Token boundaries avoid excluding a
text model merely because it contains the same letters inside a longer word.

Review the code's exact regular expressions when extending a family. Adding a
filter is a reviewed policy change; failure to recognize a new non-text family
produces an unverified worksheet rather than a data update.

## Threat sketch and safeguards

1. **A list response is untrusted input.** It may contain path traversal,
   Markdown or shell content, malformed data, or an unexpectedly large listing.
   IDs follow the schema-v1 character vocabulary,
   `[A-Za-z0-9][A-Za-z0-9._:/@-]{0,127}`, with `..` forbidden. Direct-vendor
   IDs have no slash; OpenRouter IDs have exactly one slash. Hostile IDs are dropped and
   counted, never echoed into a log, summary, worksheet, or PR. Listings are
   bounded to 4 MiB cumulatively per vendor, 2,000 entries, and 10 pages. Exceeding
   a limit fails instead of truncating; missing detection needs a complete list.
2. **Vendor keys must not escape.** Keys originate only in the five named
   environment variables, have surrounding whitespace stripped, and are refused
   by secret name if they contain anything outside visible ASCII. They travel
   only in headers, never URLs, output, artifacts, or files. HTTP bodies and raw
   transport errors are not printed. Redirects are refused before a key could be
   replayed to a different host. Known key values reflected in model IDs or
   pagination cursors fail that vendor before any worksheet or query URL is
   constructed, even if the reflected string passes the ID/cursor grammar.
3. **Vendor handling has no repository write token.** `watch` has
   `contents: read`, runs tests and the vendor-facing script, and uploads the
   worksheets and PR body as an artifact. `pull-request` has `contents: write`
   and `pull-requests: write`, no vendor keys, and no vendor-facing code. It
   treats the artifact as data and admits only `openai.md`, `anthropic.md`,
   `gemini.md`, `xai.md`, `deepseek.md`, and `openrouter.md` under `candidates/`.
   Symlinks are not followed. Extra filenames never become committed content.
4. **Fork PRs cannot invoke the privileged workflow.** Its triggers are Monday
   06:23 UTC and `workflow_dispatch` only; there is no `pull_request` or
   `pull_request_target` trigger. Top-level permissions are empty. Each job has
   a timeout, actions are pinned to the supplied full SHAs, and one concurrency
   group serializes runs.
5. **Automation must not erase human branch work.** One `model-watch/auto`
   branch is regenerated from `main`, with at most one open PR updated in place.
   Pushes use `--force-with-lease` against the observed branch SHA. A branch with
   human commits detected at discovery is left untouched, including PR closure. This is a cooperative
   author check, not cryptographic authentication of commit authorship.
6. **Skipped is different from checked.** An absent or whitespace-only key
   skips that vendor. Its previous branch worksheet is carried forward and
   marked possibly stale, because it was not re-checked against `models/`.
   OpenRouter always runs. A successful run can clear resolved checked-vendor
   worksheets while retaining skipped-vendor worksheets even if it finds no
   fresh changes. If a partial run clears the last worksheet on an existing bot
   branch, one empty reconciliation commit keeps the head distinct from `main`
   while clearing those resolved files; an identical repeat adds no commit.
   This never creates a new empty branch or PR. An existing PR's body is updated
   to the current incomplete report. An error fails the run and leaves the
   published branch alone.
7. **Nothing is automatically released.** Only human source verification can
   turn a worksheet into a record. Signing and release publication remain
   outside this workflow. A compromised trusted `main` workflow or runner is
   outside the response-parsing safeguards; token separation reduces authority
   but does not authenticate vendor facts.

Exit codes: `0` means no fresh differences, `3` means fresh differences, and `1`
means an error. Step outputs also identify skipped vendors and whether every
vendor was checked. A PR closes only when all watched vendors were checked and
nothing remains. Closing an unresolved PR does not silence the watch: the next
successful run can reopen it while the same differences remain.

## One-time setup for Michel

Do this setup separately from the offline R5 implementation. Never commit values
to `.env.example`, a worksheet, a shell command, or repository data.

1. In repository **Settings → Actions → General → Workflow permissions**, allow
   GitHub Actions to create pull requests. Leave the default token read-only;
   the two jobs request their own permissions. Requiring full-length action SHA
   pins is recommended. This guide does not claim those settings were changed.
2. Create a separate restricted list-only key for each keyed vendor, using its
   current access controls. These creation instructions identify the intended
   permissions; R5 has not tested current console options:

   | Vendor | Where to create the dedicated key | Intended restriction |
   | --- | --- | --- |
   | OpenAI | OpenAI platform API-key settings | Restricted key: all permissions None except **Models: Read**. |
   | Anthropic | Anthropic Console API-key settings | Allow only model listing/read access if the current console supports that scope. |
   | Gemini | Google AI Studio / Google Cloud API-key settings | Restrict to the Generative Language API and model listing where method restrictions are supported. API restriction alone is not a list-only permission. |
   | xAI | xAI Console team API-key settings | Allow only the model-list endpoint where endpoint restrictions are supported. |
   | DeepSeek | DeepSeek platform API-key settings | Allow only model listing/read access where scope restrictions are supported. |

   Do not infer that a generic key is list-only. If the vendor cannot enforce the
   intended restriction, leave its secret absent while reviewing that exposure
   with the coordinator. A dedicated low-budget project/team can limit spending
   but does not make an unrestricted key list-only. R5 does not establish that
   Anthropic, Gemini, xAI, or DeepSeek currently offer every restriction above.
3. Store the approved keys as repository Actions secrets with exactly these
   names. The commands prompt for values; do not append a value to them:

   ```sh
   gh secret set OPENAI_MODELS_KEY --repo michelabboud/ai-model-registry
   gh secret set ANTHROPIC_MODELS_KEY --repo michelabboud/ai-model-registry
   gh secret set GEMINI_MODELS_KEY --repo michelabboud/ai-model-registry
   gh secret set XAI_MODELS_KEY --repo michelabboud/ai-model-registry
   gh secret set DEEPSEEK_MODELS_KEY --repo michelabboud/ai-model-registry
   ```

   Each keyed vendor is optional. OpenRouter requires no secret. No signing key
   belongs in Actions secrets or either job.
4. Run **Actions → model-watch → Run workflow**. The coordinator checks the first
   live response shape for Anthropic, DeepSeek, and xAI before removing their
   **UNVERIFIED** labels. A failed check must retain those labels and diagnostic
   evidence; a mocked fixture pass is not live compatibility evidence.

## Turn a worksheet into a sourced record

1. Read the PR summary, including dropped-ID counts, skipped vendors, and stale
   worksheets. Review all proposed changes against the official linked sources.
2. Branch from the watch branch instead of committing on it. Human commits on
   `model-watch/auto` cause the watch to leave that branch alone.
3. For every new ID, independently confirm its callable name, status, tier,
   context/output limits, modalities, and every pricing category. Resolve every
   `TO VERIFY` field using official vendor documentation. Preserve `null` for
   unknown prices and numeric zero only for explicitly free service. Do not
   transfer sibling rates or a generic batch discount into unsupported fields.
4. Add the verified record to `models/<provider>.json`, with official `sources`
   and the actual human verification date. Recheck probe/default choices and
   the cheapest-GA-probe rule for that provider. For missing IDs, confirm a
   deprecation notice before changing status or removing a record.
5. Remove all worksheet files from the human-owned merge branch, including
   unhandled worksheets, before merging to `main`; unresolved evidence remains
   on the watch branch. Then run the validator and tests. The watch PR is a worksheet inbox; merging a worksheet
   does not create a verified model record. Review and merge the actual sourced
   data changes through the normal repository process.
6. Publish a numbered signed registry release only through R4's local procedure
   once Michel's signing key and the release tooling are ready. R5 never signs
   or releases, and no live release is claimed here.

## Offline checks and design differences from Genie

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests
python3 scripts/model_watch.py --help
git status --short
```

Tests use clearly invented per-vendor response fixtures and mocked `urllib`;
they need no key and make no network requests. Workflow behavior is checked
against disposable local Git repositories and a stub GitHub CLI. That proves
local branch/PR logic, not hosted GitHub acceptance or vendor compatibility.

The security boundaries are retained from Genie. Adaptations are JSON text-model
comparison instead of TOML image records, six vendors, explicit text exclusions,
all admitted proposals instead of an image-specific candidate cap, field
placeholders instead of seeded sibling values, and a cumulative byte bound.
The successful partial/no-fresh-change path also preserves skipped worksheets
and clears resolved checked worksheets; this closes an ambiguity in Genie's
fresh-change-only PR path. Reflected-credential rejection additionally prevents
valid-looking IDs/cursors from disclosing keys. The bounded empty-commit case
keeps a partial reconciliation from resetting the PR head to exactly `main`;
hosted lifecycle behavior still needs the coordinator's first run. [ADR 0005](adr/0005-model-watch.md) records the decision.
