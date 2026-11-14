# ai-model-registry
Dev mode: mvp

- Keep this a public data repository, with schemas, validation tooling, and documentation only; no application runtime.
- Verify every real value against an official vendor page and date it. Required `sources` and `verified` belong to every provider, model entry, and harness.
- A `null` price means unknown or not published; zero means free. Never substitute one for the other.
- Never store credentials, API keys, tokens, or environment values. Harnesses carry roles only; consuming applications supply values.
- Use Python 3.11+ and the standard library only. Download no validator dependencies.
- Keep closed objects, closed adapter enums, HTTPS URLs, bare commands, and the environment denylist. Preserve command and environment restrictions in both schemas and semantic validation.
- Treat supported JSON Schema keywords as an enforced contract. An unsupported keyword must stop schema loading.
- Signing never runs in CI. R4 will define signed `registry/<N>` releases; no release exists yet.
- Preserve the coordinator-provided CC0-1.0 `LICENSE` verbatim.
- Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v` before claiming validation passes.
- Follow the current lane's explicit authority. R1 does not commit, tag, push, publish, or start later tasks; its coordinator does the checkpoint and reviews.
- Read `PLAN.md`, `PROGRESS.md`, and `HANDOFF.md` for scope, evidence, and current handoff.
