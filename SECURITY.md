# Security policy

Report vulnerabilities through GitHub's private vulnerability reporting for
[michelabboud/ai-model-registry](https://github.com/michelabboud/ai-model-registry/security/advisories/new).
Do not publish exploit details, credentials, private signing keys, or sensitive
consumer configuration in public issues or pull requests.

Scope includes malicious or unsafe registry data, schema and validator bypasses,
workflow changes, release integrity, and signing-key handling. No release exists
yet. Security fixes apply to the current development branch. The local
[release ceremony](docs/releasing.md), [manual rotation procedure](scripts/new_signing_key.md#rotation)
and [public-key history](keys/README.md) define key handling; the first real key
and release remain separate manual work. Historical releases must retain their
original trusted key. Signatures establish integrity, not vendor accuracy or
freshness; clients enforce minimum versions and rollback policy separately.

Provide the affected file and JSON pointer or workflow step, a minimal invented
reproduction, expected rejection, observed result, and impact on a consuming app.
If a signing-key exposure is suspected, describe the affected key identifier and
release without sharing private key bytes.

Ordinary outdated vendor facts can be reported as data corrections with an
official source and date. A correction that enables harmful endpoints or launcher
configuration is a security report. Vulnerabilities in vendor services or in
consumer applications belong to those projects unless this repository's data or
validation creates the unsafe path.
