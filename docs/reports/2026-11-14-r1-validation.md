# R1 validation receipt — 2026-11-14

Dev mode: mvp. Lane: `96dbb202-15cc-4708-99ec-7ba056fc658a`.
Scope: local R1 implementation; no source checkpoint or release acceptance.
Runtime: Python 3.12.3. No network access, package installation, signing, commit,
tag, or push was attempted. The task requires Python 3.11+; Python
3.11 itself was not separately exercised, and hosted CI was not run.

## Check matrix

| Changed area | Required command | Result |
| --- | --- | --- |
| Empty registry | `python3 scripts/validate.py` | Exit 0; `0 files checked; 0 problems; clean` |
| Valid example data | `python3 scripts/validate.py --root tests/fixtures/valid` | Exit 0; `3 files checked; 0 problems; clean` |
| Schemas, semantics, input handling, CLI | `python3 -m unittest discover -s tests -v` | Exit 0; `Ran 73 tests in 11.791s`; `OK` |
| Python syntax | `python3 -m py_compile scripts/validate.py` | Exit 0; no output |
| Working tree | `git status --short` | Exit 0; new files untracked, including pre-existing `LICENSE`; nothing staged or committed |

The documentation worker separately parsed all three README examples and ran them
as a single invented fixture tree: `3 files checked; 0 problems; clean`, exit 0.
The initial positive contract test failed before `scripts/validate.py` existed;
its failure was `2 != 0` because Python could not open the missing script. The
first implementation run passed 49 tests; the final run adds direct interpreter,
policy-independence, boundary, and malformed-shape coverage and passes 73 tests.

Raw final command stdout/stderr, receipt metadata, and candidate hashes are retained
in `/tmp/ai-model-registry-r1-96dbb202-evidence/`. This is local evidence, not a
published artifact. The initial failure and the intermediate 49-test pass remain
in the lane transcript; neither is presented as the final candidate result.

## Contract and implementation decisions

Supported schema keywords: `$schema`, `$id`, `title`, `description`, `type`, `properties`, `required`, `additionalProperties: false`, `enum`, `const`, `pattern`, `minLength`, `maxLength`, `minimum`, `maximum`, `items`, `minItems`, `maxItems`, `uniqueItems`, `not`, `$defs`, local `$ref`, `if`, and `then`.
The loader checks unknown keywords recursively, rejects malformed keyword shapes,
invalid patterns, external or unresolved references, and cyclic references before
reading data. `$schema`, `$id`, `title`, and `description` are annotations, not
external resources to fetch. Patterns are anchored and use `re.fullmatch`.
Booleans are distinct from numbers; mathematical integers such as JSON `1.0` are
accepted as integers, as required by JSON Schema semantics.

Schema-only constraints include object closure, field types, enums, counts, token
and price bounds, required text modality, and conditional shutdown presence.
Semantic-only checks include filename identity, provider existence, model and env
name uniqueness, exactly one GA probe/default, cheapest published probe input,
real dates and UTC date bounds, parsed URL validity, and version regex compilation
with a capture group. Shutdown presence and command/env restrictions are also
checked semantically. Tests prove the actual schemas and the semantic pass each
independently reject every denylisted environment name and unsafe command form.

The input envelope rejects oversized files, duplicate keys, non-UTF-8, non-finite
numbers (including exponent overflow), nesting beyond 32, and unexpected files,
subdirectories, or symlinks. Empty regular `.gitkeep` files are the necessary
explicit exception to JSON-only directories. `media/` is ignored. `--root`
selects data only; schemas remain beside the installed script.

Assumptions: display names use the shared 1–80-character bound, optional record
notes use 500 characters, and each environment entry requires the specified
`name`, `role`, and `note`. Later R3 details were not supplied, so its scope is
referenced to the approved upstream plan. Release payload coverage and trust-key
distribution stay in R4. There is no R1 scope deviation.

## Candidate and review boundary

The validated source/policy hashes are:

```text
6e159029b4e35872908ae0f94a0951cc18024b0075acaef12e9a188aabbe36a1  scripts/validate.py
e9c60e3bc063a8d47dfa00a1ebdbc75ffd78bd5cc3fd23c9fddaee89c01902d2  schema/provider.schema.json
7a261077900eb3c13c6330b205a8042a4b19098788f523ee2ca2398daf12ef2e  schema/models.schema.json
f840ebd56a5a72b36ed29d924b9229a2399847c70b97b9914e3957f98e94c542  schema/harness.schema.json
ce5a4fa7639f12d95bc7d81b3d9b6d85c24568162336224e7dbcff9059d2037f  tests/test_validate.py
9a907021aa226a9ccbafb4231ff1b9bd8ee0db45719a2cd786e533511d2a4b0e  .github/workflows/validate.yml
```

`LICENSE` remained byte-identical to its initial SHA-256:
`a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499`.
Independent mechanical/deep review, staging, commit, checkpoint tag, source push,
and later-task admission belong to the coordinator. No review was claimed from a
moving, uncommitted working tree. R2–R5 and M1 remain open.

The dashboard helper located the existing shared view at
`/home/michel/.local/state/build-task-dashboard/tasks.html`. Its browser URL was
unavailable because WSL path conversion failed. Its publisher directory is outside
this lane's writable roots; no write or alternate publisher was attempted.

Host load was checked before verification. An intermediate measurement was orange
(38.83 on 28 cores); lightweight source work continued. The final suite started
at load 18.7075 on 28 cores with available memory above the floor. No heavy work
was started to bypass host admission. No service or watcher remains running.

## Hygiene disposition

The lane created no worktree, service, database, vendor data, or long-running
process. Its generated `scripts/__pycache__/` (44 KiB) and
`tests/__pycache__/` (76 KiB) were inspected as Python-generated `.pyc` output,
with no open users reported by `fuser`, and removed separately with `rm -r`.
Those allocated sizes came from `du -sh`; removing 120 KiB of generated output
is not a claim about a filesystem-wide free-space delta. The disposable schema
construction helper `/tmp/r1-write-schemas.py` was also removed; its reclaimed
bytes were not separately measured. Required schemas are retained as source.
Test-created isolated trees were disposed of by `TemporaryDirectory` cleanup.

Retained allocated bytes (`du -s -B1`):

```text
36864	/tmp/ai-model-registry-r1-96dbb202-evidence
233472	tests/fixtures
```

The evidence directory is owned by this R1 lane, referenced by this report and
the handoff, and retained until the coordinator accepts the R1 review and source
checkpoint. Exact past command output is not regenerable; the receipt records
commands for new runs. Fixture trees are intentional repository source, owned
by the registry maintainers and needed by the test suite; review them whenever
the data contract changes. No protected files or evidence were deleted.
