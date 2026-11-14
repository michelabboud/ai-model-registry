# R2 seed-data handoff — 2026-11-14

Dev mode: mvp. Lane: `852ee9b6-7ca5-4cf2-826e-50dfa394080b`.
Repository: `/home/michel/projects/ai-model-registry`, branch `main`.

## What was built

R2 is complete locally: nine provider objects and nine model collections contain
251 source-backed text-model/routing entries, verified `2026-11-14`. No network,
API inference, install, commit, tag, push, release, signing, or R3 admission ran.
`VERSION` stays `0.1.0`; `schema_version` stays 1. `LICENSE`, `VERSION`, and the
existing `.research/` ignore rule match HEAD byte-for-byte.

The pre-release cache shape now uses required `cache_writes` arrays (0–6 closed
TTL/price entries), per-array TTL uniqueness, and optional hourly storage in
standard and long-context pricing. Fixed cache-write names are rejected.
`gemini_interactions` is accepted by provider protocols and the new optional
harness protocol field. Fixtures, tests, README, ARCHITECTURE, source report,
ADR0003 and its index, CHANGELOG, BACKLOG, PLAN and PROGRESS are updated.

The starting tree already contained the previous lane's uncommitted HANDOFF,
PROGRESS, blocked handoff, and source-audit report. The blocked handoff remains
unchanged; its source report is preserved verbatim in the final source report's
historical section. No unrelated work was discarded.

## Verification evidence

Base/current Git HEAD (unchanged): `45a24db0e21211e415865af00e7f89786b31f432`.
Functional input-set SHA-256: `2c5942c6286c4e703b43594c0b87f6ad1c22652abbfcfd3d193819e62d5ec464`.
Python: 3.12.3. Toolchain: standard library only; no dependencies added.
All 51 final data/schema/validator/fixture/test input hashes are recorded in
[the machine receipt](../reports/2026-11-14-r2-validation.json). They match the
independently reviewed original and repair snapshots. All official archived
source bytes still match their initial review hashes.

```text
python3 scripts/validate.py
18 files checked; 0 problems; clean
Exit status: 0

python3 -m unittest discover -s tests -v
Ran 80 tests in 17.839s
OK
Exit status: 0
```

Raw full-suite receipt: `/tmp/r2-final-unittest-1.txt`.
Final validator receipt: `/tmp/r2-final-validator.txt`.
Provider summary: `/tmp/r2-final-provider-summary.txt` (stdlib JSON scan of every
model collection; counts, sole probe/default IDs, and recursive scalar-null count).
`git diff --check` returned clean. No live endpoint, account eligibility, signed
release, or consumer/runtime acceptance is claimed.

The cache/protocol regression file was run before implementation: 7 tests,
34 failed subtests as expected against R1. After implementation: 7 tests passed.
Retained receipts: `/tmp/r2-cache-before.txt`, `/tmp/r2-cache-after.txt`.
The final full suite is the authoritative integrated behavior check. The automatic
language-server hook also emitted type-inference diagnostics at the untyped CLI
report loop; no standalone static-type gate was configured or claimed, and base
attribution was not independently re-run. Runtime CLI paths passed the suite.

### Provider summary

| Provider | Models | Probe | Default | Scalar nulls |
| --- | ---: | --- | --- | ---: |
| anthropic | 15 | `claude-haiku-5-5` | `claude-opus-5-5` | 0 |
| bedrock | 11 | `anthropic.claude-haiku-5-5` | `anthropic.claude-opus-5-5` | 9 |
| deepseek | 2 | `deepseek-flash` | `deepseek-flash` | 2 |
| gemini | 15 | `gemini-3.1-flash-lite` | `gemini-3.8-flash` | 38 |
| openai | 31 | `gpt-5-nano` | `gpt-6.1-sol` | 73 |
| openrouter | 134 | `z-ai/glm-5.2` | `openai/gpt-6.1-sol` | 109 |
| vertex | 14 | `claude-haiku-5-5` | `claude-opus-5-5` | 2 |
| xai | 8 | `grok-build-0.1` | `grok-4.7` | 9 |
| zai | 21 | `GLM-4.7-Flash` | `glm-5.3` | 64 |

Scalar nulls include all nested price and limit fields; missing optional storage
and empty write arrays are not zeros or counted null fields. Every null and its
reason is listed by field and model ID in [the source report](../reports/2026-11-14-seed-data-sources.md).

### Independent review and repairs

- [Vendor/schema review and recheck](../reviews/2026-11-14-r2-vendor-schema-review.md):
  fresh-context requested `gpt-6.1-sol/xhigh`; confirmed Gemini 2.5 access gating,
  then accepted exclusion of all three restricted models and replacement probe
  `gemini-3.1-flash-lite`. Final affected nine JSON files validate; 11 patch
  manifest hashes match. Reviewer independently ran seven focused tests.
- [OpenRouter review and recheck](../reviews/2026-11-14-r2-openrouter-review.md):
  fresh-context requested `gpt-6.1-sol/high`; checked prices, 41 long-context
  mappings, 14 expiration/shutdown mappings, and batch variants. It caught the
  generic Pro slug's older DeepSeek0423 snapshot. Only that row was removed;
  the explicit0813 row and every surviving entry were independently rechecked.
- Four deprecated Vertex IDs lack archived Google shutdown dates and remain
  explicit allowed omissions; no first-party retirement dates were substituted.
  Z.ai callable-ID casing and exact visual formats remain source uncertainties.

Both actionable findings are closed on the final reviewed bytes. Reviews are
same-family, with fresh contexts and separate content-hashed inputs; process
isolation/knowledge boundaries beyond the native tool are not claimed. Requested
configurations are recorded, but provider runtime identity, token use, and measured
queue latency are unavailable. Two Standard implementation workers supplied
independent vendor file groups; one Strong and one Standard reviewer checked
separate scopes. The parent owned integration, OpenRouter, documentation, and the
single broad full-suite execution. Receipt reuse is not independent execution.

## Assumptions and source decisions

- Only archived official pages supply vendor facts; tier/probe/default are the
  explicit registry policy. Current priced non-preview listings are classified
  GA where the source supplies no stronger status. No deprecation date is guessed.
- Gemini 2.5 existing-user restrictions count as gating even when still serving.
  OpenRouter includes distinct official `:batch` routing IDs for matched models,
  with already-discounted prices and explicit batch-only endpoint notes.
- Batch percentages summarize input/output, not every cache/storage band. Exact
  cache exceptions and promotions remain notes; GCP Opus5.5 percentage stays null
  under the supplied decision and quotes $2.50/$12.50.
- Generic OpenRouter file input does not prove PDF, and generic cache-write rates
  without TTL do not prove either a write duration or hourly storage price.
- Provider protocol lists do not establish every model/endpoint combination.
  Runtime-only Bedrock Fable and Live-only Gemini Robotics Streaming are noted.
  The xAI legacy Chat listing is supported by archived navigation evidence;
  its request grammar and per-model compatibility were not verified live.

## Concerns, omissions, and remaining boundary

[The source report](../reports/2026-11-14-seed-data-sources.md) retains exact included
and excluded IDs, source filenames/URLs, all nulls, AWS SKU/unit evidence, and
all deviations. [BACKLOG](../../BACKLOG.md) records time-of-day schedules, regional
premiums, promotional/future and modality prices, Batch exceptions, per-model
routes, unresolved Z.ai identifiers, missing cloud lifecycles, Gemini-on-Vertex,
and non-Anthropic-on-Bedrock follow-up. Gated Mythos/Cyber/Rosalind, retired models,
nontext generation/embedding/OCR/voice services, unestablished hosted open-weight
models, and unmatched OpenRouter families/versions are excluded.

R2 does not claim complete Vertex legacy coverage: exact deprecated Google IDs
`claude-opus-4-1@20250805`, `claude-opus-4@20250514`,
`claude-sonnet-4-5@20250929`, `claude-sonnet-4@20250514` cannot satisfy the mandatory
shutdown field from this archive. Older Bedrock catalog product names alone do
not establish callable IDs or lifecycle. Those evidence gaps are not acceptance
by inference.

The external coordinator owns final source acceptance, version/checkpoint/commit/
push, and later task admission. R3–R5/M1 and publication remain outside this lane.
No approval question is pending in this no-input lane.

## Hygiene and retained artifacts

No worktree, build target, server, container, datastore, or long-lived service was
created. No background task is deliberately left running. One full test suite was
admitted at load21.923 on28 cores with37602MiB available; higher earlier loads were
used for lightweight independent work. Disk grew from about26GiB available at
entry to39GiB at the last inspection due to external host changes, not claimed
cleanup savings. No other project's output was touched.

Four content-pinned review snapshots are retained under the ignored `.research/`
root as reproduction evidence owned by this lane, for the coordinator's R2
acceptance event:

| Snapshot | Allocated bytes (`du -s -B1`) | Reason |
| --- | ---: | --- |
| `r2-review-852ee9b6` | 9437184 | Original eight-vendor/schema/source candidate and review finding inputs |
| `r2-openrouter-review-852ee9b6` | 1675264 | Original135-row catalog candidate and original source subset |
| `r2-repairs-review-852ee9b6` | 135168 | Final vendor/schema affected files and repair receipt input |
| `r2-openrouter-repair-852ee9b6` | 155648 | Final134-row catalog candidate and repair receipt input |

Total review snapshots:11403264 allocated bytes. They are evidence, not disposable
working trees. The original official archive predates this resumed lane and is
preserved. `/tmp/r2-claude-audit.md`, `/tmp/r2-other-audit.md`,
`/tmp/r2-openrouter-audit.md`, the four raw review reports, validator/test/summary
receipts, and one-off source extraction/report scripts are retained for audit and
reproduction; their final allocated-byte inventory is recorded below. Retained
repository reports are normal task deliverables. No evidence/log was deleted.

The shared dashboard was located via its helper at
`/home/michel/.local/state/build-task-dashboard/tasks.html`; browser URL conversion
failed under WSL. Its state lies outside this lane's writable roots, so no shared
state or browser was changed. This ancillary reporting limit did not block R2's
repository deliverable.

## Close-out confirmation

Local implementation, tests, docs and independent repair checks are complete.
No commit, tag, push, release, or version bump was performed under the lane's
explicit hold. The current source work and earlier blocked artifacts are left
reviewable on `main`. Full final `git status --short` and hygiene byte inventory
are appended by the final inspection; `.research/` remains ignored.

### Final artifact byte inventory

```text
24576	/tmp/r2-claude-audit.md
20480	/tmp/r2-other-audit.md
28672	/tmp/r2-openrouter-audit.md
12288	/tmp/r2-independent-review.md
8192	/tmp/r2-independent-repair-review.md
8192	/tmp/r2-openrouter-independent-review.md
4096	/tmp/r2-openrouter-repair-review.md
28672	/tmp/r2-cache-before.txt
4096	/tmp/r2-cache-after.txt
12288	/tmp/r2-final-unittest-1.txt
4096	/tmp/r2-final-validator.txt
4096	/tmp/r2-final-provider-summary.txt
4096	/tmp/r2-git-status-before-closeout.txt
12288	/tmp/r2-openrouter-seed.py
20480	/tmp/r2-build-source-report.py
9437184	.research/r2-review-852ee9b6
1675264	.research/r2-openrouter-review-852ee9b6
135168	.research/r2-repairs-review-852ee9b6
155648	.research/r2-openrouter-repair-852ee9b6
8192	.research/r2-original-blocked-source-report.md
86016	docs/reports/2026-11-14-seed-data-sources.md
8192	docs/reports/2026-11-14-r2-validation.json
12288	docs/reviews/2026-11-14-r2-openrouter-review.md
20480	docs/reviews/2026-11-14-r2-vendor-schema-review.md
```

Generated working output removed: `scripts/__pycache__` (45056 allocated bytes) and `tests/__pycache__` (90112 allocated bytes), 135168 bytes total. They contained only Python-generated `.pyc` files for the checked source/tests. All lane checks had finished, no open handles were reported by the targeted lsof checks, and neither cache remains. lsof emitted unrelated mount-stat warnings, so this is a bounded observation, not a host-wide idleness claim. No evidence or protected file was removed. No remaining large disposable working output was created.

### Final Git status

```text
 M ARCHITECTURE.md
 M BACKLOG.md
 M CHANGELOG.md
 M HANDOFF.md
 M PLAN.md
 M PROGRESS.md
 M README.md
 M docs/adr/README.md
 M schema/harness.schema.json
 M schema/models.schema.json
 M schema/provider.schema.json
 M scripts/validate.py
 M tests/fixtures/invalid/command-path/models/example-provider.json
 M tests/fixtures/invalid/http-url/models/example-provider.json
 M tests/fixtures/invalid/missing-verified/models/example-provider.json
 M tests/fixtures/invalid/negative-price/models/example-provider.json
 M tests/fixtures/invalid/two-probes/models/example-provider.json
 M tests/fixtures/invalid/unknown-key/models/example-provider.json
 M tests/fixtures/valid/models/example-provider.json
 M tests/test_validate.py
?? docs/adr/0003-cache-pricing-shape.md
?? docs/handoffs/2026-11-14-r2-blocked-handoff.md
?? docs/handoffs/2026-11-14-r2-seed-data-handoff.md
?? docs/reports/2026-11-14-r2-validation.json
?? docs/reports/2026-11-14-seed-data-sources.md
?? docs/reviews/2026-11-14-r2-openrouter-review.md
?? docs/reviews/2026-11-14-r2-vendor-schema-review.md
?? models/anthropic.json
?? models/bedrock.json
?? models/deepseek.json
?? models/gemini.json
?? models/openai.json
?? models/openrouter.json
?? models/vertex.json
?? models/xai.json
?? models/zai.json
?? providers/anthropic.json
?? providers/bedrock.json
?? providers/deepseek.json
?? providers/gemini.json
?? providers/openai.json
?? providers/openrouter.json
?? providers/vertex.json
?? providers/xai.json
?? providers/zai.json
?? tests/test_cache_pricing.py
```

Final inspection: functional input hashes unchanged, license/version/ignore bytes unchanged, `.research/` ignored, whitespace diff clean. The dirty/untracked status above is the intentional uncommitted R2 handback plus preserved earlier lane artifacts. No Git write was attempted.
