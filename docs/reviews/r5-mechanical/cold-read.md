# R5 mechanical cold read

Source read: `CLAUDE.md`, `docs/model-watch.md`, `docs/adr/0005-model-watch.md`, `scripts/model_watch.py`, `.github/workflows/model-watch.yml`, `tests/test_model_watch.py`, and `tests/test_model_watch_workflow.py`.

This note precedes inspection of other project material and targeted reproduction. Base supplied: `8a2a00c434aba3885bb4195699e5621da20d694c`; candidate is frozen working-file bytes, not a new commit. Dev mode is `mvp`.

The implementation appears to enforce fixed vendors, bounded listings, strict IDs, header-only outbound authentication, safe diagnostic strings, a worksheet-only artifact boundary, lease-protected branch updates, and skipped-vendor carry-forward. The branch lifecycle shell has substantive disposable-repository tests. Root owns the broad validation run; its receipt is shared provenance and is not independent execution by this lane.

First concern to investigate: a vendor can reflect a valid-looking credential into a model ID or pagination cursor. The grammar checks admit ordinary token-shaped credentials; no check visible in the cold read prevents an exact credential from becoming a worksheet ID or an outbound cursor URL. This is a hypothesis pending reproduction, not an accepted finding yet.

Other focused checks: load all six real registry inputs with `load_registry`; inspect fixture shapes and changed documentation; pin primary inputs by SHA-256; verify branch behavior matches the stated close/preserve rules.

Independence limitation: fresh-context review on the same shared filesystem and within the same model family. No sibling review outputs were read; no review conclusions were exchanged with other reviewers. No network, fixes, installation, commits, tags, pushes, or subagents are authorized.
