# Registry delivery plan

Dev mode: mvp

Status: approved 2026-11-14. Written and last updated: 2026-11-14.

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
| R2 | Officially sourced and dated vendor data; full scope in upstream plan | Coordinator-assigned lane | R1 accepted | Open |
| R3 | Registry task specified in the upstream approved plan; no implementation authorized in this lane | Coordinator-assigned lane | As specified upstream | Open |
| R4 | Numbered signed releases: manifest, Ed25519 signature, and archive | Coordinator-assigned lane | As specified upstream | Open |
| R5 | Vendor list-API work, including documenting key names without values; full scope upstream | Coordinator-assigned lane | As specified upstream | Open |
| M1 | Consumer integration milestone; first consumer is The Operator, later Genie | Coordinator | As specified upstream | Open |

Tasks run back to back under the coordinator's admission and review rules. This
lane owns R1 only and returns its result to the coordinator; it does not begin
R2–R5 or M1, create a release, or commit, tag, or push.

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
