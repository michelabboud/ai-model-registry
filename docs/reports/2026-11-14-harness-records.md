# Harness record field and source audit — 2026-11-14

Dev mode: mvp. This report audits the 13 R3 harness records against the supplied,
ignored research archive `.research/2026-11-14/harness-research.md`. The archive is
the sole factual input for this lane. No network lookup, installed CLI execution,
dependency installation, Git write, or release operation was performed to create
the records. Research observations retain their original verification date,
2026-11-14; they are not fresh observations from this implementation session.

Every record uses `schema_version: 1`, `kind: harness`, and `verified: 2026-11-14`.
Unknown required fields use `null` or `[]`. Empty protocols mean detection only;
configurable adapters have at least one evidenced wire protocol. Adapters,
format labels, regexes and icon IDs are registry integration choices, not vendor
claims. The IDs are app-neutral asset identifiers; the registry ships no images
and does not imply asset licensing or endorsement.

Environment entries contain names and semantic roles only. Records carry no
credential values, gateway values, secret material, executable configuration
snippets or installation commands. Config paths in notes describe vendor
locations; `sources` and `docs_url` contain official HTTPS URLs only.

Local-help observations below were made by the research author using installed
vendor binaries on 2026-11-14. Official docs URLs accompany those records so
provenance has a public entry point; a URL is not a claim that the page itself
contains every archived local-help observation. Local evidence is attributed
explicitly where the archive establishes it. Unspecified version invocations are
not reconstructed from a version string. OpenCode V1 is the explicit exception
for a documented `--version` invocation whose exact output remains unverified.

## Protocol decisions

| Record | Adapter | Protocols |
| --- | --- | --- |
| `claude-code` | `claude_env` | `anthropic_messages` |
| `codex` | `codex_config` | `openai_responses` |
| `opencode-v1` | `opencode_v1` | `openai_chat`, `openai_responses` |
| `opencode-v2` | `opencode_v2` | `openai_chat`, `anthropic_messages` |
| `aider` | `env_generic` | `openai_chat` |
| `copilot-cli` | `config_snippet` | `openai_chat`, `openai_responses`, `anthropic_messages` |
| `openhands` | `detect_only` | `[]` (detection only) |
| `openclaw` | `config_snippet` | `openai_chat`, `anthropic_messages` |
| `hermes-agent` | `config_snippet` | `openai_chat`, `anthropic_messages`, `openai_responses` |
| `antigravity` | `env_generic` | `gemini_generate` |
| `grok-build` | `config_snippet` | `openai_chat`, `openai_responses`, `anthropic_messages` |
| `muse-code` | `detect_only` | `[]` (detection only) |
| `cursor-cli` | `detect_only` | `[]` (detection only) |

`openai_chat` means Chat Completions; `openai_responses` means Responses;
`anthropic_messages` means Messages. The Antigravity Gemini-compatible API maps
here to `gemini_generate`; no harness establishes `gemini_interactions`.

## Per-CLI field audit

### Claude Code (`claude-code`)

- Command: `claude`; aliases: `[]`.
- Adapter: `claude_env`; config style: `env`; icon: `claude-code`.
- Protocols: `["anthropic_messages"]`.
- Environment roles: `ANTHROPIC_BASE_URL` → `base_url`, `ANTHROPIC_AUTH_TOKEN` → `auth_token`.
- Model flag: `--model`; configuration profile flag: `null`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://code.claude.com/docs](https://code.claude.com/docs).

The gateway section establishes the Messages route and both retained environment roles. The research also lists an alternative ANTHROPIC_API_KEY credential, model-family pin variables, custom headers, discovery and traffic flags; these are not needed for the selected bearer-token adapter and are omitted rather than expanding the launch surface. ANTHROPIC_MODEL is absent from the research and is not invented. The flags section lists --model and explicitly cites local binary help for the flag audit (including absence of a named --profile); the record attributes --model confirmation to installed binary --help on 2026-11-14. Settings files are configuration-file selectors, not named profiles. Preserve the vendor restriction against non-Claude gateway models and the saved-subscription-credential caveat.

Local version output 2.1.325 (Claude Code) appears in the source, but its exact invocation is not supplied; version_probe stays empty. Brand-usage terms are unverified. The icon is the registry identifier claude-code, not a copied asset or Simple Icons slug.

Official sources retained in the record:

- [https://code.claude.com/docs/en/llm-gateway](https://code.claude.com/docs/en/llm-gateway).
- [https://code.claude.com/docs/en/llm-gateway-connect.md](https://code.claude.com/docs/en/llm-gateway-connect.md).
- [https://code.claude.com/docs/en/llm-gateway-protocol.md](https://code.claude.com/docs/en/llm-gateway-protocol.md).
- [https://code.claude.com/docs/en/setup](https://code.claude.com/docs/en/setup).
- [https://github.com/anthropics/claude-code/releases](https://github.com/anthropics/claude-code/releases).

### OpenAI Codex CLI (`codex`)

- Command: `codex`; aliases: `[]`.
- Adapter: `codex_config`; config style: `toml`; icon: `openai`.
- Protocols: `["openai_responses"]`.
- Environment roles: `[]`.
- Model flag: `--model`; configuration profile flag: `--profile`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://learn.chatgpt.com/docs](https://learn.chatgpt.com/docs).

The user-level config reference supplies model_providers, base_url, env_key and the Responses-only wire API. The --model selector is listed in the flags section. The --profile / -p separate-file layering behavior is explicitly supported by the archived local binary help: $CODEX_HOME/<name>.config.toml overlays the base user configuration. This differs from older assumptions about profiles being only a table in the base TOML file. Project configuration ignores provider and profile keys.

OPENAI_BASE_URL, OPENAI_API_KEY and CODEX_API_KEY are explicitly unverified in the research and are absent from env. The maintainer issue about OPENAI_BASE_URL is not promoted to verified documentation. An application-selected env_key name is not a vendor-defined role and is not seeded. Chat Completions is omitted because wire_api=chat was removed. Local codex-cli 0.167.2 output lacks an exact invocation in the archive, so version_probe is empty. OpenAI brand terms are unverified; openai is an app-neutral icon ID.

Official sources retained in the record:

- [https://learn.chatgpt.com/docs/config-file/config-reference](https://learn.chatgpt.com/docs/config-file/config-reference).
- [https://learn.chatgpt.com/docs/cli/reference](https://learn.chatgpt.com/docs/cli/reference).
- [https://github.com/openai/codex](https://github.com/openai/codex).
- [https://github.com/openai/codex/releases](https://github.com/openai/codex/releases).

### OpenCode v1 (`opencode-v1`)

- Command: `opencode`; aliases: `[]`.
- Adapter: `opencode_v1`; config style: `jsonc`; icon: `opencode`.
- Protocols: `["openai_chat", "openai_responses"]`.
- Environment roles: `[]`.
- Model flag: `--model`; configuration profile flag: `null`.
- Version probe: `["--version"]`; major pattern: `^(?:opencode\s+)?v?(1)\.[0-9]+\.[0-9]+(?:[^0-9].*)?$`.
- Official documentation entry: [https://opencode.ai/v1/docs/](https://opencode.ai/v1/docs/).

The V1 provider documentation explicitly distinguishes the OpenAI-compatible Chat Completions package from the OpenAI Responses package. A custom Anthropic URL is not explicitly confirmed and anthropic_messages is omitted. The native V1 format uses provider, npm and options; OPENCODE_CONFIG selects a file and is not a named profile. --model / -m and --version / -v are documented.

The requested --version probe is retained because the research documents that invocation. Exact V1 output is explicitly UNVERIFIED. The major regex is a registry detection rule, not an observed output claim: it accepts plain or opencode-prefixed semantic versions, optional v, and captures only major 1. A future V1 output sample must confirm or revise it. No environment roles are exposed: config-file selection and user-chosen credential names do not need to become fixed vendor bindings. The icon opencode is a registry ID shared with V2.

Official sources retained in the record:

- [https://opencode.ai/v1/docs/](https://opencode.ai/v1/docs/).
- [https://opencode.ai/v1/docs/providers/](https://opencode.ai/v1/docs/providers/).
- [https://opencode.ai/v1/docs/cli/](https://opencode.ai/v1/docs/cli/).
- [https://github.com/anomalyco/opencode/releases](https://github.com/anomalyco/opencode/releases).

### OpenCode v2 (`opencode-v2`)

- Command: `opencode`; aliases: `[]`.
- Adapter: `opencode_v2`; config style: `jsonc`; icon: `opencode`.
- Protocols: `["openai_chat", "anthropic_messages"]`.
- Environment roles: `[]`.
- Model flag: `null`; configuration profile flag: `null`.
- Version probe: `["--version"]`; major pattern: `^opencode\s+v(2)\.[0-9]+\.[0-9]+(?:[^0-9].*)?$`.
- Official documentation entry: [https://opencode.ai/docs/](https://opencode.ai/docs/).

The native provider example names an OpenAI-compatible package, and the providers documentation names an Anthropic-compatible package. These establish openai_chat and anthropic_messages. Although V1 configuration is accepted and normalized in memory, that migration promise is not enough to assert a native V2 Responses package or transport: openai_responses is omitted pending explicit evidence. Prefer native V2 providers/package/settings configuration; native V2 values win conflicts with V1 fields, and the migration does not rewrite the source file.

The exact archived invocation opencode --version printed opencode v2.2.7. The major regex captures 2 in that documented output family. V2 --model / -m is explicitly UNVERIFIED and model_flag is null; V1 flags are not inherited. No named profile is documented. Earlier V2.0.x/2.1.x release existence is unverified. Config-format and version-major selection are adapter policy; opencode is the shared icon ID.

Official sources retained in the record:

- [https://opencode.ai/docs/](https://opencode.ai/docs/).
- [https://opencode.ai/docs/migrate-v1/](https://opencode.ai/docs/migrate-v1/).
- [https://opencode.ai/docs/providers/](https://opencode.ai/docs/providers/).
- [https://opencode.ai/v2/docs/config](https://opencode.ai/v2/docs/config).
- [https://opencode.ai/v2/docs/cli](https://opencode.ai/v2/docs/cli).
- [https://github.com/anomalyco/opencode/releases/tag/v2.3.0](https://github.com/anomalyco/opencode/releases/tag/v2.3.0).
- [https://github.com/anomalyco/opencode/releases/tag/v2.2.0](https://github.com/anomalyco/opencode/releases/tag/v2.2.0).

### Aider (`aider`)

- Command: `aider`; aliases: `[]`.
- Adapter: `env_generic`; config style: `env`; icon: `aider`.
- Protocols: `["openai_chat"]`.
- Environment roles: `OPENAI_API_BASE` → `base_url`, `OPENAI_API_KEY` → `api_key`.
- Model flag: `--model`; configuration profile flag: `null`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://aider.chat/docs/](https://aider.chat/docs/).

The OpenAI-compatible page supplies OPENAI_API_BASE, OPENAI_API_KEY, Chat Completions, and the openai/ model-name convention. --model is retained. The optional --config / -c YAML-file selector is not a named profile. The record chooses environment configuration rather than a YAML adapter, so config_style is the short label env. AIDER_OPENAI_API_BASE, --openai-api-base and --set-env are documented alternatives, not necessary additional bindings for the selected path.

Anthropic custom base URL behavior is explicitly unverified and is omitted despite the documented Anthropic credential option. Last release in the research is v0.86.0 on 2025-08-09; the note preserves that age without asserting the project is abandoned. No working version invocation/output is established, so version_probe is empty. Aider brand terms are unverified. Icon aider is an app-neutral ID; the registry ships no SVG.

Official sources retained in the record:

- [https://aider.chat/docs/llms/openai-compat.html](https://aider.chat/docs/llms/openai-compat.html).
- [https://aider.chat/docs/config/options.html](https://aider.chat/docs/config/options.html).
- [https://aider.chat/docs/llms/anthropic.html](https://aider.chat/docs/llms/anthropic.html).
- [https://aider.chat/docs/install.html](https://aider.chat/docs/install.html).
- [https://github.com/Aider-AI/aider/releases](https://github.com/Aider-AI/aider/releases).

### GitHub Copilot CLI (`copilot-cli`)

- Command: `copilot`; aliases: `[]`.
- Adapter: `config_snippet`; config style: `json`; icon: `github-copilot`.
- Protocols: `["openai_chat", "openai_responses", "anthropic_messages"]`.
- Environment roles: `[]`.
- Model flag: `--model`; configuration profile flag: `null`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://docs.github.com/copilot/concepts/agents/about-copilot-cli](https://docs.github.com/copilot/concepts/agents/about-copilot-cli).

The official BYOK page establishes providers.json under COPILOT_HOME (default ~/.copilot), the COPILOT_PROVIDERS_CONFIG path override, provider type and wireApi selectors. Together these support Chat Completions, Responses and Messages. --model selects PROVIDER-NAME/MODEL-NAME. config_snippet is the adapter category and JSON the format label; the record contains no executable configuration. Exact providers.json JSON nesting is explicitly unverified, so consumers cannot generate a verified full snippet from this record alone. Nonempty providers.json takes precedence over the legacy environment path, and environment references in strings are literal.

All COPILOT_PROVIDER_* names are omitted from env, including documented API_KEY, API_KEY_COMMAND and HEADERS names, to keep the selected adapter file-based. COPILOT_PROVIDER_BASE_URL and COPILOT_PROVIDER_TYPE are unverified and must not be inferred. COPILOT_MODEL, COPILOT_HOME and COPILOT_OFFLINE are documented auxiliary choices, not necessary retained bindings. No profile flag or working version invocation/output is established. github-copilot is a registry icon ID rather than the upstream githubcopilot slug.

Official sources retained in the record:

- [https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models).
- [https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference).
- [https://github.blog/changelog/2026-04-07-copilot-cli-now-supports-byok-and-local-models/](https://github.blog/changelog/2026-04-07-copilot-cli-now-supports-byok-and-local-models/).
- [https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli).
- [https://github.com/github/copilot-cli/releases](https://github.com/github/copilot-cli/releases).

### OpenHands CLI (`openhands`)

- Command: `openhands`; aliases: `[]`.
- Adapter: `detect_only`; config style: `null`; icon: `openhands`.
- Protocols: `[]`.
- Environment roles: `[]`.
- Model flag: `null`; configuration profile flag: `null`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://docs.openhands.dev/openhands/usage/cli/installation](https://docs.openhands.dev/openhands/usage/cli/installation).

The official documentation says the CLI is no longer actively maintained. Known LLM_API_KEY, LLM_MODEL and LLM_BASE_URL settings apply only with --override-with-envs and are not persisted. Because the custom-endpoint wire protocol is unverified, the record is detect_only with protocols=[], env=[], config_style=null, and null profile/model flags. The note retains the override requirement without presenting environment roles as a usable gateway integration. The research says there is no --model and no profile selector.

The persistent settings field names are partly unverified; no executable config is emitted. Agent Canvas npm-package identification and the custom LiteLLM wire mapping remain unverified. The newer main OpenHands release must not be mistaken for a maintained CLI release. No working version invocation/output is established. Brand terms are unverified; openhands is an app-neutral icon ID.

Official sources retained in the record:

- [https://docs.openhands.dev/openhands/usage/cli/installation](https://docs.openhands.dev/openhands/usage/cli/installation).
- [https://docs.openhands.dev/openhands/usage/cli/command-reference](https://docs.openhands.dev/openhands/usage/cli/command-reference).
- [https://github.com/OpenHands/OpenHands-CLI/releases](https://github.com/OpenHands/OpenHands-CLI/releases).
- [https://github.com/OpenHands/OpenHands/releases](https://github.com/OpenHands/OpenHands/releases).

### OpenClaw (`openclaw`)

- Command: `openclaw`; aliases: `[]`.
- Adapter: `config_snippet`; config style: `json5`; icon: `openclaw`.
- Protocols: `["openai_chat", "anthropic_messages"]`.
- Environment roles: `[]`.
- Model flag: `null`; configuration profile flag: `--profile`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://docs.openclaw.ai](https://docs.openclaw.ai).

The custom-provider source explicitly names api selectors openai-completions and anthropic-messages, mapped to openai_chat and anthropic_messages. models.providers configuration lives in ~/.openclaw/openclaw.json using JSON5; OPENCLAW_CONFIG_PATH can select another file. --profile isolates state under ~/.openclaw-<name> and is retained as the configuration/state profile selector. The record explains that OpenClaw is mainly a personal assistant gateway for chat applications, even though it offers terminal and agent commands.

Other API values, including openai-responses and Gemini, are unverified and omitted. A --model flag is undocumented and therefore null; model selection is documented via models set. Onboarding flags and auxiliary config/state environment names are not required runtime bindings and are omitted from env. No working version invocation/output is established. Brand terms are unverified. Icon openclaw is a registry identifier.

Official sources retained in the record:

- [https://docs.openclaw.ai/install](https://docs.openclaw.ai/install).
- [https://docs.openclaw.ai/gateway/configuration](https://docs.openclaw.ai/gateway/configuration).
- [https://docs.openclaw.ai/concepts/model-providers/custom-providers](https://docs.openclaw.ai/concepts/model-providers/custom-providers).
- [https://docs.openclaw.ai/cli](https://docs.openclaw.ai/cli).
- [https://github.com/openclaw/openclaw](https://github.com/openclaw/openclaw).

### Hermes Agent (`hermes-agent`)

- Command: `hermes`; aliases: `[]`.
- Adapter: `config_snippet`; config style: `yaml`; icon: `hermes-agent`.
- Protocols: `["openai_chat", "anthropic_messages", "openai_responses"]`.
- Environment roles: `[]`.
- Model flag: `--model`; configuration profile flag: `--profile`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs).

The provider source supplies the custom provider, ~/.hermes/config.yaml, base_url, api_key/key_env and transport / api_mode selectors. chat_completions, anthropic_messages and codex_responses map directly to the three retained protocols. --profile / -p is global and uses profile directories under ~/.hermes/profiles/ through HERMES_HOME. --model / -m is valid for hermes chat; the record note restricts its scope instead of implying every subcommand accepts it.

OPENAI_BASE_URL applies only to openai-api, not custom, so it is not a generic base_url env role here. Credential names chosen through key_env are application data and not fixed vendor names. No working version invocation/output is established. The Simple Icons hermes asset belongs to a parcel company and is deliberately not reused; hermes-agent is an app-neutral registry ID. Nous brand terms remain unverified.

Official sources retained in the record:

- [https://hermes-agent.nousresearch.com/docs/integrations/providers](https://hermes-agent.nousresearch.com/docs/integrations/providers).
- [https://hermes-agent.nousresearch.com/docs/user-guide/profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles).
- [https://hermes-agent.nousresearch.com/docs/reference/cli-commands](https://hermes-agent.nousresearch.com/docs/reference/cli-commands).
- [https://hermes-agent.nousresearch.com/docs/getting-started/installation](https://hermes-agent.nousresearch.com/docs/getting-started/installation).
- [https://github.com/NousResearch/hermes-agent/releases](https://github.com/NousResearch/hermes-agent/releases).

### Google Antigravity CLI (`antigravity`)

- Command: `agy`; aliases: `[]`.
- Adapter: `env_generic`; config style: `env`; icon: `antigravity`.
- Protocols: `["gemini_generate"]`.
- Environment roles: `GEMINI_API_KEY` → `api_key`, `GOOGLE_GEMINI_BASE_URL` → `base_url`.
- Model flag: `--model`; configuration profile flag: `null`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://antigravity.google/docs/cli/reference/](https://antigravity.google/docs/cli/reference/).

The official CLI docs name agy, not antigravity. They establish GEMINI_API_KEY and GOOGLE_GEMINI_BASE_URL for a Gemini-compatible endpoint, with Gemini model-provider selection in ~/.gemini/antigravity-cli/settings.json required. GEMINI_API_KEY alone has no effect; .env is not loaded. The record uses env_generic and the short env format label; its note preserves the required JSON provider-selection prerequisite. --model is documented; no named profile is documented.

The research calls this the Gemini API rather than an Interactions endpoint. It is mapped to the requested gemini_generate vocabulary; gemini_interactions is not asserted. The antigravity binary alias and CLI v1.5.8 release date are unverified and omitted. The desktop application version is not a CLI version probe. No working CLI version invocation/output is established. Icon antigravity is a registry ID and does not reuse the merely related googlegemini brand.

Official sources retained in the record:

- [https://antigravity.google/docs/install/](https://antigravity.google/docs/install/).
- [https://antigravity.google/docs/cli/reference/](https://antigravity.google/docs/cli/reference/).
- [https://antigravity.google/docs/getting-started?tab=cli](https://antigravity.google/docs/getting-started?tab=cli).
- [https://antigravity.google/docs/changelog/](https://antigravity.google/docs/changelog/).

### Grok Build (`grok-build`)

- Command: `grok`; aliases: `[]`.
- Adapter: `config_snippet`; config style: `toml`; icon: `xai`.
- Protocols: `["openai_chat", "openai_responses", "anthropic_messages"]`.
- Environment roles: `[]`.
- Model flag: `--model`; configuration profile flag: `null`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://docs.x.ai/build/overview](https://docs.x.ai/build/overview).

The official name is Grok Build. TOML model entries use base_url, env_key and api_backend; chat_completions, responses and messages establish the three recorded protocols. ~/.grok/config.toml is the default config path, with GROK_HOME selecting its directory. --model / -m is documented in the research, with installed grok --help in the cited evidence set on 2026-11-14; the record explicitly attributes that help confirmation. -p / --single is a one-shot headless prompt, not a config profile. --sandbox profiles are a different concern; profile_flag is null.

GROK_MODELS_BASE_URL and XAI_API_KEY are known alternatives but are omitted because this row chooses TOML config. api_backend default is explicitly unverified on the docs site, even though the official GitHub guide says chat_completions; the record does not assign a default. Release date is unverified. The optional local agent symlink is omitted to avoid collision with Cursor's prescribed alias. Local grok 1.0.77 output has no exact version invocation, so version_probe is empty. Icon xai is not the social-network x asset; brand terms are unverified.

Official sources retained in the record:

- [https://x.ai/news/grok-build-cli](https://x.ai/news/grok-build-cli).
- [https://docs.x.ai/build/overview](https://docs.x.ai/build/overview).
- [https://docs.x.ai/build/settings/reference](https://docs.x.ai/build/settings/reference).
- [https://github.com/xai-org/grok-build](https://github.com/xai-org/grok-build).

### Muse Code (`muse-code`)

- Command: `muse`; aliases: `[]`.
- Adapter: `detect_only`; config style: `null`; icon: `meta`.
- Protocols: `[]`.
- Environment roles: `[]`.
- Model flag: `--model`; configuration profile flag: `null`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://dev.meta.ai/docs](https://dev.meta.ai/docs).

The Meta blog, developer docs and archived local launcher identify this as Muse Code, Meta's terminal coding agent. --model and a Meta provider base URL override are confirmed by the archived muse --help on 2026-11-14. The official docs URL is retained for provenance; no local path is used in sources. --permission-profile governs permissions rather than configuration and is not recorded as profile_flag.

The custom-endpoint wire protocol and bearer behavior remain explicitly unverified. Meta's separate model API serving several familiar endpoints does not prove this CLI uses any particular one. Therefore adapter=detect_only, protocols=[], env=[], config_style=null; META_API_KEY and provider-base-URL flags are not promoted into usable generic gateway bindings. Settings JSON provider keys, release date and a Muse-specific logo remain unverified. Local Muse Code 1.4.20 output has no exact version invocation, so version_probe is empty. Icon meta is a neutral registry identifier, not a claim that a Muse-specific asset exists.

Official sources retained in the record:

- [https://research.meta.ai/blog/introducing-muse-code-and-muse-spark-1-2](https://research.meta.ai/blog/introducing-muse-code-and-muse-spark-1-2).
- [https://dev.meta.ai/docs/coding-agents](https://dev.meta.ai/docs/coding-agents).
- [https://dev.meta.ai/docs/muse-code/changelog](https://dev.meta.ai/docs/muse-code/changelog).

### Cursor CLI (`cursor-cli`)

- Command: `cursor-agent`; aliases: `["agent"]`.
- Adapter: `detect_only`; config style: `null`; icon: `cursor`.
- Protocols: `[]`.
- Environment roles: `[]`.
- Model flag: `--model`; configuration profile flag: `null`.
- Version probe: `[]`; major pattern: `null`.
- Official documentation entry: [https://cursor.com/docs/cli/installation](https://cursor.com/docs/cli/installation).

Official docs name agent; the archived installed launcher is cursor-agent. The record uses cursor-agent as command and agent as the sole alias. --model is confirmed via installed cursor-agent --help on 2026-11-14, with official parameter docs included in sources. No config profile is documented. Brand guidelines call the product Cursor, not Cursor AI or Cursor Code.

The endpoint option and CURSOR_API_ENDPOINT point to Cursor's proprietary backend. They are not verified model-provider base-URL controls. Consequently adapter=detect_only, protocols=[], env=[], config_style=null; CURSOR_API_KEY and endpoint controls are not retained as model API roles. The editor's OpenAI base-URL override does not establish CLI support. No version probe is inferred from the installed version-directory name. Icon cursor is the registry identifier and no icon pack is shipped.

Official sources retained in the record:

- [https://cursor.com/docs/cli/installation](https://cursor.com/docs/cli/installation).
- [https://cursor.com/docs/cli/reference/parameters](https://cursor.com/docs/cli/reference/parameters).
- [https://cursor.com/docs/cli/reference/authentication](https://cursor.com/docs/cli/reference/authentication).
- [https://cursor.com/brand](https://cursor.com/brand).

## Cross-record omissions, conflicts and limits

- The supplied research summary is not stronger evidence than its detailed
  sections or explicit UNVERIFIED list. Where they differ, conservative detail
  wins. In particular, Codex summary environment claims are omitted; OpenCode
  V1 Anthropic custom routing and V2 model flags are omitted; OpenHands and Muse
  remain detection-only despite having endpoint-related controls.
- OpenCode V2 accepts V1 config, but that is not independent confirmation of a
  native V2 Responses transport. Only Chat Completions and Messages are listed.
  The V1 regex is a registry parsing policy with no archived exact output sample;
  the V2 regex matches the recorded opencode v2.2.7 output family. Neither regex
  is a vendor compatibility guarantee.
- Only OpenCode records carry version probes. Claude, Codex, Grok and Muse
  research contains version strings but does not specify their exact version
  invocation. Other CLIs have no established working probe; release tags and
  install-directory names are not substituted for one.
- Copilot receives no legacy COPILOT_PROVIDER_* environment bindings, even for
  documented names. Exact providers.json nesting remains unverified and blocks
  claiming that a complete executable snippet has been audited.
- OpenHands known environment controls are omitted from env rather than
  presenting detection metadata as a ready gateway adapter. The override flag
  requirement remains explicit. Muse and Cursor likewise expose no model API
  environment roles merely because an endpoint or vendor key control exists.
- Named configuration profiles are limited to Codex, OpenClaw and Hermes.
  Settings/config-file selectors, permission profiles, sandbox profiles and
  Grok headless prompt flags are not treated as named configuration profiles.
- The only alias is Cursor agent. The optional Grok local agent symlink is
  deliberately omitted; Antigravity launcher naming is unverified. Two
  OpenCode records share one command and must be distinguished by version.
- Gemini CLI is excluded from this 13-record scope. No additional harness is
  inferred from the archived research.
- Unverified brand terms for Anthropic, OpenAI, xAI, Nous, OpenClaw, OpenHands
  and Aider remain unresolved. A registry icon ID is not permission to ship a
  vendor asset. Hermes parcel-company artwork and the X social-network icon are
  not substitutes for Nous Hermes Agent and xAI Grok Build.

All vendor statements above are bounded by the archived 2026-11-14 evidence.
Integrated validation, independent review and acceptance receipts belong to the
R3 owner and are recorded after this source audit.


## R3 local implementation and verification receipt

### What was built

Added the 13 audited harnesses and made harness `protocols` required, unique and
bounded to zero through four values in the five requested custom-endpoint
protocols. Semantic validation enforces empty if and only if `detect_only`.
Provider protocols are unchanged. All fixture harnesses, the README example,
architecture, icon inventory and ADR 0004 move together; `schema_version` stays 1.

The integration audit corrected initially verbose config-format labels to the
requested lowercase short labels (`env`, `toml`, `jsonc`, `json`, `json5`, `yaml`)
or null, with prerequisites retained in notes. The schema's existing free-text
format-label contract was not broadened or replaced with an unrelated enum.

### Verification evidence

Base: `33f7beb675ff95a1f0e4e133dced477af4dfccd3` (`main`), repository `VERSION`
`0.2.0`, unchanged. Python 3.12.3; standard library only. Final check started at
2026-11-14T23:39:56Z. Implementation/data fingerprint:
`a651efc2c47b03d9fde75590ce8e3fd3892342ac097627afcb86aba4d62d2a41`.

Fingerprint algorithm: sort all relative `.json`/`.py` paths recursively under
`schema`, `scripts`, `tests`, `providers`, `models`, and `harnesses`; feed each
UTF-8 relative path, a NUL byte, and the raw SHA-256 digest of its contents to
SHA-256. Documentation, bytecode and ignored research/logs are excluded so adding
this receipt does not change its own implementation/data identity.

| Area | Command / scope | Observed result |
| --- | --- | --- |
| Final registry | `python3 scripts/validate.py` | `31 files checked; 0 problems; clean`, exit 0 |
| Final complete suite | `python3 -m unittest discover -s tests` | `Ran 89 tests in 9.436s`, `OK`, exit 0 |
| Repository verbose-suite requirement | `python3 -m unittest discover -s tests -v` | `Ran 89 tests in 11.047s`, `OK`, exit 0 before the format-label correction; code and fixtures unchanged afterward |
| Required contract regression | `python3 -m unittest discover -s tests -p test_harness_protocols.py -v` | Initial old contract: 8 tests, 17 failures including subtests; fixed contract: 8 tests, `OK` |
| Valid fixture tree | `python3 scripts/validate.py --root tests/fixtures/valid` | `3 files checked; 0 problems; clean`, exit 0 |
| Patch whitespace | `git diff --check` | No output, exit 0 |
| Research/record audit | All 13 IDs, format labels, per-section URLs/docs/date and major matching | Passed; source V2 banner and synthetic V1/version-12 discrimination checked |
| Required record summary | Script loading sorted `harnesses/*.json` and printing ID, command, adapter, protocols | 13 rows printed; identical mapping to the table above |
| Git status | `git status --short` | R3 edits/new files only; final path listing appended below |

The final suite was rerun because the integration audit changed the record bytes;
the earlier green schema/test result did not establish compliance with the short
format labels. Initial integrated receipt:
`.research/2026-11-14/r3-validation-d04fe179.log`; final raw receipt:
`.research/2026-11-14/r3-final-validation-d04fe179.log`. Both remain ignored and
retained. The initial failing regression output remains in this lane's tool
transcript; its decisive counts are preserved above. No failed/inconclusive
experiment was relabeled as a pass.

The research input SHA-256 remained
`afac8b783b0e9795b16012dc4491c4856e85dbad5cd6102e67a9032aa413659e`.
The archived research is provenance, not a network request made by R3 or proof
that a current gateway/CLI runtime integration works. No runtime launch occurred.

Model/ownership ledger: one implementation worker dispatched as `gpt-6.1-sol` at
`high` owned the 13 records and initial field audit. The R3 owner integrated the
protocol contract/tests, corrected format labels, audited sources, and ran the
integrated checks. Provider runtime model identity and token spend were not
measured. The worker's lightweight pre-final-wording validation is not claimed
as an independent final gate. Independent coordinator review remains pending.

### Assumptions and limits

Only OpenCode's documented version invocations are encoded; a version string
without its exact invocation is insufficient to invent a probe. `jsonc` labels
OpenCode's documented JSON/JSONC family. Antigravity's selected environment mapping
is labeled `env`; required JSON provider selection stays explicit in the note.
Other choices and all research exclusions are documented per CLI above. There
are no unresolved conflicts requiring a decision; the brief expressly permits
OpenHands detection-only treatment and source-driven protocol/flag omissions.

All 31 expanded items in the research UNVERIFIED list are individually retained
in BACKLOG, plus conservative V2 Responses uncertainty. An editor-only
basedpyright report-loop type-inference diagnostic is also recorded there; the
reported loop and report construction are unchanged from HEAD, and no standalone
baseline type-check was run. These receipts claim validator and unittest passes,
not a type-check pass or release acceptance.

### Close-out boundary and hygiene

R3 is done locally; the coordinator owns independent review and any later
checkpoint/release. No version bump, commit, tag, push, network lookup, installed
CLI execution, dependency installation, image asset, signing operation, database,
service or background process was introduced. Existing LICENSE is unchanged.
No worktree or build-output directory was created. Test temporary fixtures use
the existing unittest cleanup. All source files, research and raw receipts are
retained for coordinator review. Only proven regenerable, idle Python bytecode
caches were removed; the measurement below counts their allocated file blocks,
not a net free-space delta on this concurrently used host.


### Hygiene disposition and storage snapshot

Read-only inspection confirmed four regular Python 3.12 bytecode cache files
with matching interpreter magic, corresponding source files, and no extra cache
directory entries. No other Python process had this repository as its working
directory. `lsof +D` printed no open handles for either cache directory; it warned
only about unrelated mqueue/hugetlbfs/binfmt mount metadata. After inspection,
`rm -r -- scripts/__pycache__` and `rm -r -- tests/__pycache__` each ran alone and
exited 0. Both directories are now absent. The removed files accounted for
139,264 allocated bytes (`st_blocks * 512`); directory blocks and a host-wide
free-space change are not included. Regeneration, if wanted, is
`python3 -m compileall scripts tests`. No research, log, report, state, source,
branch or worktree was removed. No worktree/build target was created.

Allocated-file snapshot before appending this final status/storage section
(`stat.st_blocks * 512`, directory blocks excluded):

| Retained group | Allocated bytes |
| --- | ---: |
| Harness JSON source files (13) | 53,248 |
| New protocol test source | 8,192 |
| New ADR, source report and handoff | 45,056 |
| Ignored raw validation receipts | 20,480 |

These are current allocations of named files, not an incremental disk-growth or
reclaimed-space claim; appending this section/status grows the report and log.
Owner is R3 until handback, then the coordinator. Product source/documents are
retained for independent review and the coordinator's source checkpoint; there
is no disposable source-generation command. Raw logs are unique execution
receipts and stay ignored, with next review at coordinator acceptance. Existing
research is retained in place with unchanged hash; it is an input, not newly
created validation scratch. Tests used the existing self-cleaning temporary
fixtures. No large generated working data or persistent process remains.

The live admitted final run measured load 11.36 on 28 logical cores and 41,046 MiB
available memory. Earlier orange load was observed during record production;
no heavy check was admitted then. Disk inspection showed about 51 GiB available
on the working filesystem, above the local 3% floor, and `/dev/shm` empty.
No resource or storage boundary was bypassed.

### Reproduce the required record summary

```python
import json
from pathlib import Path

for path in sorted(Path("harnesses").glob("*.json")):
    record = json.loads(path.read_text())
    print(record["id"], record["command"], record["adapter"], record["protocols"])
```

### Final Git state

`HEAD`, `VERSION`, and `LICENSE` are unchanged, the index is empty, research
remains ignored, and the final implementation/data fingerprint still matches.
No code/data changed after the final passing gate; only documentation receipts
were completed. `git status --short` returned exit 0:

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
 M scripts/validate.py
 M tests/fixtures/invalid/command-path/harnesses/example-cli.json
 M tests/fixtures/invalid/http-url/harnesses/example-cli.json
 M tests/fixtures/invalid/missing-verified/harnesses/example-cli.json
 M tests/fixtures/invalid/negative-price/harnesses/example-cli.json
 M tests/fixtures/invalid/two-probes/harnesses/example-cli.json
 M tests/fixtures/invalid/unknown-key/harnesses/example-cli.json
 M tests/fixtures/valid/harnesses/example-cli.json
 M tests/test_cache_pricing.py
?? docs/adr/0004-harness-protocols-field.md
?? docs/handoffs/2026-11-14-r3-harness-records-handoff.md
?? docs/reports/2026-11-14-harness-records.md
?? harnesses/aider.json
?? harnesses/antigravity.json
?? harnesses/claude-code.json
?? harnesses/codex.json
?? harnesses/copilot-cli.json
?? harnesses/cursor-cli.json
?? harnesses/grok-build.json
?? harnesses/hermes-agent.json
?? harnesses/muse-code.json
?? harnesses/openclaw.json
?? harnesses/opencode-v1.json
?? harnesses/opencode-v2.json
?? harnesses/openhands.json
?? tests/test_harness_protocols.py
```
