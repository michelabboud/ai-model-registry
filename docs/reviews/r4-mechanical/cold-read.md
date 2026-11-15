# R4 mechanical cold read

Status: CONFIRMED source inspection; no blocking defect identified in the first pass.

Recorded 2026-11-15 before reading receipts, other reviews, or coordinator adjudications. Baseline HEAD confirmed as `08d9fcb03744a188fe7f26b8305efe21ee8dc125`; review target is the frozen, uncommitted R4 source candidate, by explicit coordinator instruction. This is a working-tree exception to the normal committed-candidate review procedure.

Requested configuration: gpt-6.1-sol, high. Provider runtime identity, token use, queue time and provider measurements are unavailable. Fresh context in the same model family; shared filesystem and tool environment, with no sandbox-isolation claim. Mode: mvp. Reviews and dev-modes skill bodies loaded; the coordinator loaded the assignment roster. Local playbook layer was read for applicable constraints.

Read material: scripts/release_common.py; scripts/build_release.py; scripts/sign_release.py; scripts/verify_release.py; scripts/publish_release.py; tests/test_release.py; .gitignore; docs/releasing.md; scripts/new_signing_key.md; keys/README.md; docs/adr/0006-signing-with-openssl.md; README.md; ARCHITECTURE.md. No real key or gh execution, no network, no source modification.

Excluded: all other docs/reviews/*; all .research/r4-deep-only/*; all coordinator adjudications and sibling review content. Dedicated scratch parent reserved for this review only: .research/r4-mechanical-only/scratch.

The first source pass finds argument-list subprocesses, suppressed subprocess diagnostics, external owned regular 0600 key metadata checks, immediate public-key signature verification, signature-before-manifest-parse ordering, exact canonical tar header/padding checks, data-dirty/nonempty-output guards, verify-before-gh sequencing, paginated release-number selection, existing-target-tag refusal and byte-compared downloads. The test source contains throwaway-key and fake-gh paths and the mandatory negative cases.

No confirmed blocking finding at cold read. Remaining mechanical work: verify candidate/receipt provenance and inspect focused operational failure handling and test gaps. Live GitHub publication, a real signing ceremony and consumer acceptance remain unverified by design; existing-source receipt reuse is not independent test execution. Potential same-user mutation races and publication serialization are operator trust/hardening questions rather than evidenced realistic attacks in this brief.
