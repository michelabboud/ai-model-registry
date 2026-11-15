# Registry delivery plan

Dev mode: mvp

Status: approved 2026-11-14. Written: 2026-11-14. Last updated: 2026-11-15.

Threat sketch: a contributor or release attacker could change a model identifier,
price, endpoint, command, or environment binding consumed by an application.
Schemas and validation restrict the accepted grammar, command names, adapter
identifiers, URLs, and environment names. Applications supply secret values and
gateway URLs; registry records supply roles only. Future clients must verify an
Ed25519 signature and every manifest hash before parsing registry data. A signature
establishes the publisher and integrity, not the truth of a price or vendor claim.
Official sources and verification dates remain mandatory.

The authoritative approved plan is
[The Operator's registry plan](https://github.com/michelabboud/the-operator/blob/main/docs/plans/2026-11-14-ai-model-registry-plan.md),
approved 2026-11-14. This index records only the scope supplied to this repository;
consult that plan for later tasks' full specifications and acceptance gates.

| Task | Deliverable | Owner | Dependencies | Status |
| --- | --- | --- | --- | --- |
| R1 | Repository skeleton, three JSON Schemas, standard-library validator, fixtures, tests, and validation CI | R1 lane; coordinator integrates and reviews | None | Done 2026-11-14 (local checks); coordinator review/checkpoint pending |
| R2 | Officially sourced and dated vendor data; full scope in upstream plan | Coordinator-assigned lane | R1 accepted | Done locally 2026-11-14; coordinator acceptance/checkpoint pending |
| R3 | Required harness protocols and 13 officially sourced coding-CLI records | R3 lane; coordinator integrates and reviews | R1 and R2 supplied by coordinator | Done locally 2026-11-15; coordinator review/checkpoint pending |
| R4 | Numbered signed releases: manifest, Ed25519 signature, and archive | Coordinator-assigned lane | As specified upstream | Waiting on Michel's signing key |
| R5 | Six-vendor proposal-only text-model watch, separate watch/PR jobs, fixtures/tests, and key-name documentation | R5 lane; coordinator reviews/checkpoints and performs live check | R1–R3 supplied at repository version 0.3.0 | Done locally 2026-11-15; 141 tests/clean validator; coordinator acceptance/live checks separate |
| M1 | Consumer integration milestone; first consumer is The Operator, later Genie | Coordinator | As specified upstream | Open |

Tasks run back to back under the coordinator's admission and review rules. This
original R1 lane owned R1 only and returned its result to the coordinator; it did
not begin R2–R5 or M1, create a release, or commit, tag, or push. The current R2
lane's scope and evidence are recorded below.

## R1 execution and evidence

The implementation lane owns `schema/`, `scripts/`, `tests/`, and `.github/`.
A scoped documentation worker owns the repository documents, ADRs, and empty
directory markers. Shared-file changes and final integration stay sequential.
Workers communicate through the available native agent channel and return a file
list with evidence; a message alone is not acceptance. The coordinator owns the
independent review and source checkpoint after this lane's handback.

The validation boundary is one R1 candidate: validate the empty data directories,
validate the valid fixture tree, run the full unittest suite, compile the validator,
and inspect `git status --short`. No dependencies are downloaded. `LICENSE` is
preserved verbatim. No commit, tag, push, or signing operation runs in this lane.

| Step | File boundary | Evidence | Next step |
| --- | --- | --- | --- |
| Define contracts and decisions | `schema/`, `docs/adr/`, `PLAN.md` | Narrow schema vocabulary; ADRs accepted | Validator and fixtures |
| Implement validation and test fixtures | `scripts/`, `tests/` | Positive and adversarial checks with JSON pointers | Integrated verification |
| Document and integrate CI | Repository documents, `media/`, `.github/` | Local instructions and pinned validation workflow | Integrated verification |
| Verify and return R1 | Entire R1 candidate | Required commands and final test counts in the handoff | Coordinator review and checkpoint; then R2 admission |

R1 local verification completed 2026-11-14: 73 tests passed, empty and example
trees clean, validator compilation passed. See [the receipt](docs/reports/2026-11-14-r1-validation.md).

## R2 resumption — 2026-11-14

The current lane owns R2 only, under the supplied original brief and resumption
decisions. It performs no network access, commit, tag, push, release, or admission
of R3. The earlier DeepSeek source blocker is resolved by a new archived official
authentication page. The cache-shape decision is recorded in ADR 0003 before
implementation; `schema_version` stays 1.

The lane coordinates two scoped native workers. One owns Anthropic, Vertex, and
Bedrock provider/model files; one owns OpenAI, Gemini, DeepSeek, Z.ai, and xAI
provider/model files. They read only the archived official sources and return
per-provider source/null/omission audits. Shared files stay with the lane owner,
who owns schemas, validator, fixtures/tests, OpenRouter matching, documentation,
integration, and required verification. No recursive fan-out is assigned.

| Step | Evidence | Next step |
| --- | --- | --- |
| Replace cache fields; add storage and Gemini protocol contracts | Focused positive and adversarial tests, fixtures, ADR | Integrate vendor data |
| Seed nine providers from archived official pages | Per-record source URLs/date and per-provider audit | Cross-provider matching and audit |
| Integrate OpenRouter and document omissions/conditions | Complete source report and backlog | Frozen-candidate verification |
| Run validator, unittest suite, provider summary, Git status | Exact command results in the R2 handoff | Return to coordinator for independent review/checkpoint |

R2 local close-out: nine providers, 251 model/routing entries, clean 18-file
validator, 80 passing tests, and independently checked source-review repairs.
See [the final R2 handoff](docs/handoffs/2026-11-14-r2-seed-data-handoff.md).
No Git write, version bump, network lookup, release, or later task admission ran.

## R3 execution — 2026-11-14

Dev mode: mvp. Authorized by the current R3 lane brief. Tasks within R3 run back
to back; the lane returns to the coordinator after local verification and does not
admit R4. No network, commit, tag, push, version bump or release is authorized.
The threat sketch above still applies: new records contain environment roles and
app-neutral icon IDs only, never values, executable snippets, or shipped images.

The R3 owner handles the schema, semantic validator, fixtures/tests, ADR and shared
documentation sequentially. One scoped records worker owned only `harnesses/`
and the per-CLI source report, after the schema change lands locally. Both read
only `.research/2026-11-14/harness-research.md`; it remains ignored. The native
agent channel carries findings; the R3 owner integrates and runs required checks.
The coordinator owns independent review and the later source checkpoint.

| Step | Owner / file boundary | Evidence | Next step |
| --- | --- | --- | --- |
| Define required harness protocols | R3 owner: schema, validator, fixtures/tests, ADR 0004 | Positive and negative protocol contract tests | Populate records |
| Write 13 sourced records and field audit | Records worker: `harnesses/`, R3 source report | Per-field research provenance and explicit omissions | Integrate documentation |
| Document contract, icons and unknowns | R3 owner: README, architecture, progress, backlog and handoff | Research-to-record audit; all blocking UNVERIFIED items retained | Frozen-candidate verification |
| Verify and hand back | R3 owner: integrated R3 candidate | Validator, unittest counts, record summary and Git status | Coordinator independent review/checkpoint |

R3 local close-out: 13 harness records, required protocol contract, short format
labels, clean 31-file validator, and 89 passing tests. See the
[R3 handoff](docs/handoffs/2026-11-14-r3-harness-records-handoff.md) and
[field/source audit](docs/reports/2026-11-14-harness-records.md). The coordinator
owns independent review and checkpointing. No version, Git metadata, network,
release, or later-task admission was changed by R3.

## R5 execution — 2026-11-15

Dev mode: mvp. Authorized by the current R5 lane brief at repository version
0.3.0. The lane implements only the proposal-only model watch, offline fixtures
and tests, two-job workflow, and documentation. No network, commit, tag, push,
version bump, signing, release, or later-task admission is authorized. R4 is
waiting on Michel's signing key.

The R5 owner owns `scripts/model_watch.py`, vendor fixture tests, and final
integration. A scoped workflow worker owns `.github/workflows/model-watch.yml`
and its local workflow simulations. A documentation worker owns the guide,
ADR 0005, and affected repository records. These workers share the checkout,
preserve each other's edits, and do not recursively fan out. Shared-file and
dependent work stays sequential. The lane ran fresh-context mechanical and deep
reviews; the external coordinator owns final source acceptance, the source
checkpoint, and first live compatibility checks.

The threat sketch is [the model-watch guide](docs/model-watch.md): keep the
signing key outside CI, separate vendor-key parsing from repository write access,
admit only fixed worksheet names, refuse redirects and malformed/list-limit
responses, never echo hostile IDs or keys, and retain skipped worksheets as
possibly stale. [ADR 0005](docs/adr/0005-model-watch.md) records the adaptation
before implementation.

| Step | Owner / file boundary | Acceptance evidence | Status |
| --- | --- | --- | --- |
| Define proposal and CI trust boundaries | Documentation worker: guide and ADR 0005 | Six-vendor policy and full threat sketch | Done locally |
| Implement listings and worksheet generation | R5 owner: `scripts/`, vendor fixtures/tests | Mocked `urllib`, no network/real keys; required positive/failure paths | Done locally |
| Adapt the two-job workflow | Workflow worker: `.github/`, workflow simulation tests | Local branch/PR admission, lease, human-commit, and skipped-vendor behavior | Done locally |
| Integrate docs and verify the frozen candidate | R5 owner with documentation worker | Validator, full unittest discovery, CLI help, and Git status | Done locally |
| Return to coordinator | R5 owner: current handoff | Exact results and remaining UNVERIFIED/live/review boundaries | Done locally |

Shared dashboard reporting is unavailable in this lane: the existing shared
state is outside its writable roots. The lane does not relocate or overwrite
that state to work around containment. Its local implementation evidence is
recorded in the [R5 handoff](docs/handoffs/2026-11-15-r5-model-watch-handoff.md).

R5 final local acceptance: **31 files checked; 0 problems; clean**; **141 tests
in 19.006s, OK**; CLI help exit 0. Both review defects were reproduced, repaired,
and accepted by focused re-review. Initial and final source hashes, raw failures,
and exact command receipts are retained in the [validation report](docs/reports/2026-11-15-r5-validation.md).
No version change, repository commit, tag, or push was performed.

| R5 review | Requested configuration | Finding / final disposition |
| --- | --- | --- |
| Mechanical | `gpt-6.1-sol`, `high`; fresh context, shared filesystem | Credential reflection and partial-empty lifecycle reproduced; both fixed and focused re-reviews accepted. |
| Deep | `gpt-6.1-sol`, `xhigh`; fresh context, shared filesystem | Partial-empty lifecycle reproduced; credential-safety overstatement corrected after mechanical evidence; both final fixes accepted. |

Actual provider runtime identity, token use, and queue latency are unavailable.
The two reviewers share a model family; no cross-family independence is claimed.
