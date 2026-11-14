# 0004: Required harness wire protocols

Date: 2026-11-14

## Status

Accepted for R3 before the first registry release. Supersedes R2's optional
harness protocol declaration; `schema_version` remains 1.

## Context

A gateway must know which ingress a coding CLI needs when it points at a custom
endpoint. An adapter describes how an application configures that CLI, while the
wire protocol describes the requests the gateway must accept. Neither a CLI's
vendor nor the protocol of its default backend establishes custom-endpoint support.

## Decision

Require `protocols` on every harness: a unique array of zero to four entries from
`anthropic_messages`, `openai_chat`, `openai_responses`, `gemini_generate`, and
`gemini_interactions`. The schema enforces presence, bounds, types and vocabulary.
The semantic validator enforces empty if and only if `adapter` is `detect_only`.
Every configurable adapter therefore needs at least one verified wire protocol,
and a detection-only record cannot advertise gateway integration.

Protocols describe verified custom-endpoint capabilities, not a promise that every
model supports every operation. Unknown protocol support is left out, explained
in notes and the source report, and tracked in the backlog. Provider protocols
retain their existing broader vocabulary and bounds.

## Alternatives rejected

- Infer protocols from the adapter: rejected because `env_generic` and
  `config_snippet` each cover several protocols. Configuration format and request
  format are independent.
- Keep the field optional: rejected because consumers cannot distinguish an
  omitted integration fact from an intentionally detection-only record.
- Copy a vendor API's protocols onto its CLI: rejected because the CLI may use
  a proprietary backend or a smaller set of transports for custom endpoints.

## Consequences

Consumers can choose a compatible gateway ingress without adapter-name heuristics.
All harness examples and fixtures must supply the field. A detection-only record
can be enriched only after its endpoint protocol is verified and its adapter is
changed together with a nonempty protocol list. This is a pre-release contract
change, with no published consumers to migrate and no schema-version increment.
