# R5 mechanical focused repair review — credential reflection

CONFIRMED: initial finding M1 is fixed on the pinned script/test bytes below; no new blocker found in this focused repair boundary.

REFUTED: the initial raw-credential model-ID and pagination-cursor leak reproductions no longer succeed through `run`, `check_vendor`, or direct `fetch_pages`.

UNVERIFIED: workflow lifecycle repair and its interactions are outside this focused review; live vendors, hosted Actions, and the final integrated broad gate remain separate.

Date: 2026-11-15. Dev mode: `mvp`. Base remains `8a2a00c434aba3885bb4195699e5621da20d694c`; this is review of frozen working files, not a new commit. Initial `findings.md`, cold-read note, and failure evidence remain preserved.

| Input | SHA-256 |
| --- | --- |
| `scripts/model_watch.py` | `6cb77ceb5a319ebe2014d81c5928b00f522876f8ff2822438e48a84e654d6d92` |
| `tests/test_model_watch.py` | `7e4f24aee532a9caff7203d320d63c1308e8a8fa42584a1c06d4440384b5d16f` |

## Source assessment

`_known_secrets` collects the stripped, valid named environment credentials. `check_vendor` supplies this set to both fetching and ID parsing, including public OpenRouter. `_refuse_reflection` refuses strings containing any known credential with the constant safe error `response reflects a credential`.

The guard runs on raw model IDs before admission or worksheet rendering, and on Anthropic `last_id` and Gemini `nextPageToken` before query URL construction. A direct call to `fetch_pages(vendor, key)` defaults the cursor guard to that key. The run returns an error before candidate/PR-body/step-output publication; this preserves the incomplete-listing failure semantics rather than dropping the reflected entry and continuing.

## Independently executed focused checks

Command:

```sh
PYTHONPATH=tests python3 -m unittest -v \
  test_model_watch.CredentialsAndHostility.test_reflected_key_in_vendor_model_ids_fails_without_publication \
  test_model_watch.CredentialsAndHostility.test_reflected_keys_never_enter_pagination_urls
```

Result: exit 0; **2 tests in 0.039s; OK**, exercising six ID subcases and both pagination subcases.

Additional no-network reproduction used the real `run`/`check_vendor`/`fetch_pages` paths with the existing test module's invented registry and mocked `FakeOpener`. Each named vendor key was distinct (`fixture-review-<vendor>-secret`). For each vendor, a syntactically admissible model ID embedded a supplied credential between a prefix and suffix; OpenRouter embedded the DeepSeek key within a routed OpenAI ID. Every case returned exit 1, reported `check_vendor` status `error`, produced safe output and URLs, and created no candidates directory, PR body, or GitHub step-output file. Safe diagnostic summaries may be written on error; the captured files contained no fake credential.

Direct Anthropic/Gemini `fetch_pages(vendor, key)` calls, with no explicit `secret_values`, received a reflected cursor on the first mocked response. Both raised the safe credential-reflection error after **one request**, with no credential in the requested URL. All assertions passed. Per-case results are retained in `fix-focused-checks.json`.

## Shared evidence and limitations

Inspected root evidence under `.research/r5-reflection-3m5z8olg/`: the initial regression run recorded **8 failing subcases** (`3 != 1`); the repaired watcher suite recorded **34 tests in 0.326s; OK**. These are shared root executions, not independent repetitions by this lane. This lane independently ran only the two focused regression methods and the additional reproduction matrix described above.

Same-family, fresh-context reviewer on the shared filesystem. Script/tests were held stable by the coordinator during this review; no sibling review outputs were opened. No network, real credentials, source changes, installation, repository Git writes, or subagents. The final integrated candidate still needs the coordinator's broad validation after the separate workflow repair lands.
