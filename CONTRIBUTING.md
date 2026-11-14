# Contributing

Use Python 3.11 or newer. The validator and tests use only the standard library;
there is no dependency-installation step. Read [ARCHITECTURE.md](ARCHITECTURE.md)
and the [accepted decisions](docs/adr/README.md) before changing the contract.

## Data changes

Every value needs verification against an official vendor page and a `verified`
date. Include official HTTPS source URLs on each provider, model entry, and harness.
Do not use secondary articles or guesses as authority. If a price is not published
or is unknown, write `null`; write zero only when the official source says it is
free. Use USD per million tokens and distinguish cache durations and long-context
pricing. Do not invent a vendor's capabilities or model identifiers.

One provider or harness object lives in its matching `<id>.json`; one model
collection lives in `<provider-id>.json` and needs that provider record. Examples
belong only in clearly marked fixtures or documentation. `media/` is reserved for
Genie and is outside this validator's contract.

Never contribute API keys, credentials, environment values, executable files, or
icon assets. Harness records declare roles only. Do not weaken the bare-command
rules, adapter allowlist, or environment denylist. Those command and environment
rules deliberately exist in both the schemas and semantic validator.

## Validate a contribution

```sh
python3 scripts/validate.py
python3 scripts/validate.py --root tests/fixtures/valid
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/validate.py
```

Add meaningful tests for changed behavior and failure cases. A new schema keyword
requires interpreter support and a loader-guard test in the same change. All
objects remain closed. Run CI-equivalent checks before submitting a pull request.

## Source checkpoints

Use Michel's public Git identity:
`29182417+michelabboud@users.noreply.github.com`.
`VERSION` is the repository version source of truth. Source task checkpoints use
`checkpoint/<VERSION>` tags, derived from that file. Preserve unrelated work and
include validation evidence in the handoff or pull request. The R1 implementation
lane must not commit, tag, or push; its coordinator performs the checkpoint after
review.

`registry/<N>` releases are a separate data-release sequence to be implemented in
R4. No release exists yet. Private signing keys stay out of this repository and
signing never runs in CI. Report vulnerabilities privately as described in
[SECURITY.md](SECURITY.md).
