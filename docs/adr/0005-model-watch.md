# 0005: A proposal-only weekly text-model watch

Date: 2026-11-15

## Status

Accepted for R5 in dev mode `mvp`. Implementation and offline acceptance are
recorded in the [R5 handoff](../handoffs/2026-11-15-r5-model-watch-handoff.md).
Live endpoint compatibility remains a separate coordinator check.

## Context

Vendor listings change between human source audits. A listing establishes only
what one account can currently see; it does not establish capabilities, prices,
general availability, or retirement. Automatic record updates would turn those
limited observations into apparently verified facts. Hosted CI must also never
receive the registry signing key.

Michel's own `genie-registry` already separates vendor access from Git write
access. R5 adapts that design to this repository's JSON text-model collections,
without changing the signed-release or data-validation contracts.

## Decision

- Compare six fixed vendor listings with `models/<provider>.json`. Generate only
  `candidates/<provider>.md`, with every proposed field marked `TO VERIFY` and
  references to the provider's `docs_url` and existing model/pricing sources.
  Existing `ga` and `preview` records absent from the complete listing become
  prompts to investigate; deprecated records do not become missing proposals.
- Keep endpoint, header, secret, pagination, and non-text exclusion policy in one
  `VENDORS` table. Gemini requires `generateContent`. OpenRouter admits only the
  six approved vendor prefixes and excludes `:batch` routes.
- Use Python 3.11+ standard library only. Refuse redirects, strip surrounding key
  whitespace, accept visible ASCII keys only, and name invalid secrets without
  printing their values. Reject known key values reflected into IDs or page
  cursors before rendering or query construction. Drop and count hostile model
  IDs without echoing them.
  Fail a vendor on an unexpected response shape or an incomplete listing rather
  than guessing; bound each listing to 4 MiB cumulatively, 2,000 entries, and
  10 pages.
- Split CI into `watch` (read-only token, vendor keys) and `pull-request` (write
  token, no vendor keys or vendor-facing code). The latter admits only the six
  known worksheet names from the artifact and never follows artifact symlinks.
  Run on Mondays at 06:23 UTC and manual dispatch only, with pinned actions,
  timeouts, concurrency control, and no pull-request trigger.
- Maintain one `model-watch/auto` branch and one open PR. Regenerate from `main`,
  push with `--force-with-lease`, and preserve branches carrying human commits.
  A skipped vendor keeps its prior worksheet and is marked possibly stale.
  Close the PR only after every watched vendor was checked and no differences
  remain. Handle successful partial runs even when there are no fresh changes,
  so unresolved skipped worksheets remain visible and resolved worksheets clear.
  When an incomplete run clears the last worksheet of an existing bot branch,
  publish one empty reconciliation commit above `main` and update the existing
  PR body. Do not create an empty branch/PR or repeat that commit on unchanged
  runs. Keeping a distinct head avoids deliberately resetting an incomplete PR
  to the base commit; hosted lifecycle behavior remains a first-run check.
- Never edit `providers/` or `models/`, sign, release, or push `main`. Signing
  remains local to Michel under R4. Candidates stay ignored on `main` and are
  explicitly force-added only as named worksheet files on the watch branch.

## Alternatives rejected

- Automatically edit model records: list responses are insufficient evidence for
  most fields, and a routine merge could otherwise publish fabricated facts.
- Sign or release from CI: this would expose the production signing key to a
  hosted workflow and erase the custody boundary.
- Use one job with both vendor keys and write access: a vendor-response handling
  defect would have unnecessarily broad repository authority.
- Create a new branch or PR every week: repeated unresolved observations would
  accumulate duplicate review work.
- Reuse Genie's image-specific candidate cap or sibling model values: text-model
  inventory is larger, and sibling prices or limits are not evidence. Retain all
  admitted candidates within the listing bounds and use explicit placeholders.

## Consequences

Human source verification remains mandatory. Missing keys do not mean that a
vendor was checked, and listing omissions never prove retirement. Anthropic,
DeepSeek, and xAI endpoint shapes remain **UNVERIFIED** until the coordinator's
first successful live run. Z.ai, Vertex, and Bedrock remain unwatched because no
verified key-scoped listing endpoint was supplied for this task. The complete
threat sketch, key-setup procedure, exclusions, and review steps are in
[the model-watch guide](../model-watch.md).
