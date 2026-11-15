<!-- Astra via hexe, Opus 5.5 validating, by Michel's word 2026-10-09 -->
> **Coordinator validation (Opus 5.5, 2026-11-15):** Minor 1 accepted on the reviewer's reproduction (the workflow shell exits 1 when the artifact holds only pr-body.md); minor 2 confirmed (test_validate.py:274 writes invalid JSON, so it passes for the wrong reason); minor 3 confirmed (releasing.md:163–167 omits the human-confirmation requirement from the approved plan); nit confirmed. All fixed before the first signed release, with the two cheap hardening items.

# Milestone review M1 — ai-model-registry 0c1f79b
Verdict: PASS WITH MINORS

Reviewed all six commits through `0c1f79bd86b0e73fc0c2c2da9cf894737b98a6b7`, in `mvp` mode. **No confirmed defect requires delaying the first signed release.** Hosted workflow and consumer acceptance remain separate.

## Blockers

None confirmed.

## Majors

None confirmed.

## Minors

1. **The no-change workflow depends on an empty directory surviving artifact transport.**  
   `.github/workflows/model-watch.yml:164` rejects `[ ! -d "$in/candidates" ]`. When no worksheets exist, the producer creates an empty directory at line 66, but only `pr-body.md` contains data. `tests/test_model_watch_workflow.py:52` always creates the receiving directory, hiding this case.

   **Confirmed reproduction:** running the actual workflow shell against a temporary download containing only `pr-body.md` exits 1 with `artifact directories are not regular directories`. Reconciliation and subsequent PR closure cannot proceed. **UNCONFIRMED:** the pinned actions’ hosted round-trip behavior was not exercised. Preserve an explicit marker or safely accept an absent worksheet directory, and test that transport case.

2. **The oversized-input test cannot detect removal of the size restriction.**  
   `tests/test_validate.py:274–275` writes:
   ```python
   write_bytes(b' ' * (1024 * 1024 + 1))
   self.assert_bad(PROVIDER, '')
   ```
   This is invalid JSON regardless of its size. With the validator’s cap relaxed to 2 MiB in memory, the test’s asserted condition still passed—now because JSON parsing failed. An otherwise valid provider padded beyond 1 MiB was accepted under that relaxed cap.

   The production restriction works; its regression test does not protect it. Use oversized, otherwise valid JSON and assert the size-specific diagnostic.

3. **Client guidance omits the required human confirmation before activation.**  
   `docs/releasing.md:163–167` says, “Apply schema and semantic validation before activating data,” then assigns activation responsibilities to consumers. Neither this sequence nor the corresponding architecture guidance states the approved requirement that a person confirm changes before application.

   A client author following this reference could implement automatic activation after verification. State the confirmation requirement explicitly, especially for endpoint and launcher changes. This is a documentation-contract gap; no consumer implementation was supplied to establish unsafe activation.

## Nits

- **Current progress metadata is stale.** `PROGRESS.md:3` states “Repository version: 0.4.0”; line 8 reports “251 models.” This candidate is version **0.5.0 with 177 models**. Preserve historical receipts, but correct the current summary.

## Hardening

- **File identity across checks:** `scripts/release_common.py:317–319` reads manifest bytes, verifies a separately reopened pathname, then parses the earlier bytes. Key metadata checking at lines 324–338 likewise precedes OpenSSL reopening the path at line 356. A concurrent local writer could substitute files between these operations. This requires local write access to the relevant files/directories; no network-only bypass was established.

- **Archive resource bounds:** `scripts/release_common.py:265` calls `digest_stream(handle)` before comparing the signed size; its loop reads to EOF at line 65. Someone replacing a downloaded release asset can force unnecessary hashing of an oversized file. Integrity still fails, and uncompressed `r:` mode avoids decompression bombs, but the signed byte count could bound work earlier.

## Verified sound (brief)

- **Executed checks:** validator reported `31 files checked; 0 problems; clean`; unittest reported `Ran 187 tests in 37.846s — OK`. Temporary fixtures and throwaway keys only; repository remained clean.
- **Validation:** closed schemas, unsupported-keyword rejection, independent command/environment restrictions, parsed HTTPS URLs, placeholder restrictions, bounded JSON reads/depth, duplicate-key and nonfinite-number rejection, and probe/default/shutdown rules are implemented and exercised.
- **Release tooling:** deterministic canonical ustar, signature-before-manifest-parsing order subject to the local race noted above, complete hash/membership checks, forbidden archive types/paths, and no extraction. Python does not read private-key contents. Publication tests cover consecutive numbering, existing-tag refusal, explicit destination binding, staged assets and download comparison; actual GitHub publication was not exercised.
- **Model watch:** vendor keys and write authority occupy separate jobs; no PR trigger reaches the privileged workflow. Actions have full SHA pins. Redirect refusal, bounded listings, hostile-ID handling, credential-reflection rejection, fixed worksheet admission and lease-protected pushes have meaningful offline coverage.
- **Data:** nine providers, 177 models and 13 harnesses. All 45 documented threshold corrections match the records. Probe/default selections and cache shapes validate; sampled harness unknowns remain explicitly qualified or detection-only.
- **Hygiene:** no credential-pattern matches in 168 unique historical blobs across six commits, excluding `docs/reviews/`. Observed local paths describe ordinary checkout/dashboard locations. CC0 is consistent and unchanged since introduction; the security policy provides a private reporting route.
- **Limits:** vendor facts were checked for internal/source-report consistency, not reverified live. Hosted artifact transport, real-key backup/rotation and consumer integration remain **UNCONFIRMED**. No repository files were changed, and `docs/reviews/` was not read.