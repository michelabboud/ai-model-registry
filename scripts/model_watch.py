#!/usr/bin/env python3
# Adapted from michelabboud/genie-registry scripts/model_watch.py (Michel's own repository), 2026-11-15.
"""Propose-only text-model watch; Python 3.11+ standard library only.

The only generated registry-tree files are six named candidates/*.md worksheets.
No record edits, signing, release, git operation or command execution occurs here.
Vendor data is untrusted; keys travel in headers only. See docs/model-watch.md.
Exit codes: 0 no fresh differences, 3 differences, 1 error. A skipped vendor is
not a successful check: its previous worksheet must be carried forward by CI.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import http.client
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

EXIT_NO_CHANGES = 0
EXIT_ERROR = 1
EXIT_CHANGES = 3
MAX_RESPONSE_BYTES = 4 * 1024 * 1024  # cumulative wire bytes per vendor listing
MAX_LISTED_MODELS = 2000             # raw entries, including excluded/hostile IDs
MAX_PAGES = 10
MAX_REGISTRY_BYTES = 1024 * 1024
MAX_MODEL_ID_LEN = 128              # schema v1 bound; stricter traversal checks below
REQUEST_TIMEOUT_SECONDS = 30
KEY_RE = re.compile(r'[\x21-\x7e]+')
MODEL_ID_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:/@-]*')
PAGE_TOKEN_RE = re.compile(r'[A-Za-z0-9_\-=.~+/]{1,512}')
USER_AGENT = 'ai-model-registry-model-watch/1'
TO_VERIFY = 'TO VERIFY'
# Token boundaries keep a text/vision model whose name merely contains letters
# resembling an excluded family. These heuristics are proposals, not capabilities.
NON_TEXT = (r'(?:^|[-_./:])(?:embed(?:ding)?s?|image(?:gen|generation)?|audio|tts|'
            r'whisper|moderation|realtime|ocr|transcribe|transcription|speech|video)'
            r'(?:[-_./:]|$)')


class WatchError(Exception):
    """Safe diagnostic: never include a key, header, raw ID or response body."""


@dataclass(frozen=True)
class Vendor:
    name: str
    display: str
    list_url: str
    env_key: str | None
    auth_header: str = ''
    auth_prefix: str = ''
    collection: str = 'data'
    pagination: str = ''
    extra_headers: tuple[tuple[str, str], ...] = ()
    exclusions: tuple[str, ...] = (NON_TEXT,)
    allowed_prefixes: tuple[str, ...] = ()
    forbidden_suffixes: tuple[str, ...] = ()


# All vendor policy is here. Anthropic/DeepSeek/xAI shapes are UNVERIFIED until
# a coordinator's first live check; parsers never fall back to a guessed shape.
VENDORS = (
    Vendor('openai', 'OpenAI', 'https://api.openai.com/v1/models',
           'OPENAI_MODELS_KEY', 'Authorization', 'Bearer ',
           exclusions=(NON_TEXT, r'^(?:dall-e|sora)(?:[-_.]|$)')),
    Vendor('anthropic', 'Anthropic', 'https://api.anthropic.com/v1/models?limit=1000',
           'ANTHROPIC_MODELS_KEY', 'x-api-key', pagination='anthropic',
           extra_headers=(('anthropic-version', '2023-06-01'),)),
    Vendor('gemini', 'Google Gemini',
           'https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000',
           'GEMINI_MODELS_KEY', 'x-goog-api-key', collection='models', pagination='gemini',
           exclusions=(NON_TEXT, r'^(?:imagen|veo)(?:[-_.]|$)')),
    Vendor('xai', 'xAI', 'https://api.x.ai/v1/models',
           'XAI_MODELS_KEY', 'Authorization', 'Bearer '),
    Vendor('deepseek', 'DeepSeek', 'https://api.deepseek.com/models',
           'DEEPSEEK_MODELS_KEY', 'Authorization', 'Bearer '),
    Vendor('openrouter', 'OpenRouter', 'https://openrouter.ai/api/v1/models', None,
           exclusions=(NON_TEXT, r'^(?:openai/)?(?:dall-e|sora)(?:[-_.]|$)',
                       r'^google/(?:imagen|veo)(?:[-_.]|$)'),
           allowed_prefixes=('openai/', 'anthropic/', 'google/', 'deepseek/', 'z-ai/', 'x-ai/'),
           forbidden_suffixes=(':batch',)),
)
KNOWN_WORKSHEETS = frozenset(v.name + '.md' for v in VENDORS)


@dataclass
class ByteBudget:
    used: int = 0


@dataclass
class Listing:
    text_ids: set[str] = field(default_factory=set)
    all_ids: set[str] = field(default_factory=set)
    dropped: int = 0


@dataclass
class Registry:
    docs_url: str
    records: list[dict]


@dataclass
class VendorResult:
    vendor: Vendor
    status: str
    message: str = ''
    added: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    dropped: int = 0
    registry: Registry | None = None

    @property
    def changed(self):
        return bool(self.added or self.missing)


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise WatchError(f'refused HTTP {code} redirect')


_OPENER = urllib.request.build_opener(_RefuseRedirects())


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError('non-finite JSON constant')


def _json_loads(body):
    return json.loads(body, object_pairs_hook=_unique_object, parse_constant=_reject_constant)


def fetch_json(url: str, headers: dict, budget: ByteBudget | None = None):
    """Fetch bounded JSON; all transport exceptions have non-reflective messages."""
    if urllib.parse.urlsplit(url).scheme != 'https':
        raise WatchError('refused non-HTTPS URL')
    budget = ByteBudget() if budget is None else budget
    remaining = MAX_RESPONSE_BYTES - budget.used
    try:
        request = urllib.request.Request(url, method='GET')
        for name, value in headers.items():
            request.add_header(name, value)
        request.add_header('Accept', 'application/json')
        request.add_header('User-Agent', USER_AGENT)
        with _OPENER.open(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = response.read(remaining + 1)
    except WatchError:
        raise
    except urllib.error.HTTPError as error:
        error.close()
        raise WatchError(f'HTTP {error.code}') from None
    except urllib.error.URLError:
        raise WatchError('network error (URLError)') from None
    except TimeoutError:
        raise WatchError('request timed out') from None
    except http.client.HTTPException:
        raise WatchError('protocol error (HTTPException)') from None
    except OSError:
        raise WatchError('network error (OSError)') from None
    except ValueError:
        # http.client's invalid-header errors can contain the entire key.
        raise WatchError('invalid request') from None
    budget.used += len(body)
    if budget.used > MAX_RESPONSE_BYTES:
        raise WatchError(f'listing exceeds {MAX_RESPONSE_BYTES} bytes')
    try:
        return _json_loads(body)
    except (ValueError, RecursionError):
        raise WatchError('response is not valid JSON') from None


def valid_model_id(value, *, routed=False):
    if not (isinstance(value, str) and 0 < len(value) <= MAX_MODEL_ID_LEN
            and MODEL_ID_RE.fullmatch(value) and '..' not in value):
        return False
    # Only OpenRouter needs a vendor separator. No path traversal, empty part,
    # or extra slash can be smuggled into Markdown or a worksheet filename.
    parts = value.split('/')
    return (len(parts) == 2 and all(parts)) if routed else len(parts) == 1


def is_text_candidate(vendor: Vendor, model_id: str):
    if vendor.allowed_prefixes and not model_id.startswith(vendor.allowed_prefixes):
        return False
    if any(model_id.lower().endswith(s) for s in vendor.forbidden_suffixes):
        return False
    return not any(re.search(p, model_id, flags=re.IGNORECASE) for p in vendor.exclusions)


def _entries(vendor: Vendor, payload):
    if not isinstance(payload, dict) or not isinstance(payload.get(vendor.collection), list):
        raise WatchError(f"response has no '{vendor.collection}' array")
    entries = payload[vendor.collection]
    id_key = 'name' if vendor.name == 'gemini' else 'id'
    if any(not isinstance(entry, dict) or id_key not in entry for entry in entries):
        raise WatchError('response contains an unexpected model entry shape')
    return entries


def _refuse_reflection(value, secret_values):
    # A syntactically valid model ID/cursor can still be an echoed credential.
    # Fail the vendor before rendering an artifact or constructing a query URL.
    if isinstance(value, str) and any(secret in value for secret in secret_values if secret):
        raise WatchError('response reflects a credential')


def _known_secrets(env):
    values = (env.get(v.env_key, '').strip() for v in VENDORS if v.env_key)
    return tuple({value for value in values if KEY_RE.fullmatch(value)})


def _next_url(vendor: Vendor, payload, secret_values):
    if vendor.pagination == 'anthropic':
        if not isinstance(payload.get('has_more'), bool):
            raise WatchError("response has no boolean 'has_more'")
        if not payload['has_more']:
            return None
        cursor = payload.get('last_id')
        _refuse_reflection(cursor, secret_values)
        entries = payload[vendor.collection]
        if not valid_model_id(cursor) or not entries or entries[-1].get('id') != cursor:
            raise WatchError('invalid last_id page cursor in response')
        return vendor.list_url + '&after_id=' + urllib.parse.quote(cursor, safe='')
    if vendor.pagination == 'gemini':
        if 'nextPageToken' not in payload or payload['nextPageToken'] == '':
            return None
        cursor = payload['nextPageToken']
        _refuse_reflection(cursor, secret_values)
        if not isinstance(cursor, str) or not PAGE_TOKEN_RE.fullmatch(cursor):
            raise WatchError('invalid page token in response')
        return vendor.list_url + '&pageToken=' + urllib.parse.quote(cursor, safe='')
    if payload.get('has_more') or payload.get('nextPageToken'):
        raise WatchError('unexpected pagination indicator in response')
    return None


def fetch_pages(vendor: Vendor, key: str, *, secret_values=()):
    secret_values = secret_values or ((key,) if key else ())
    headers = dict(vendor.extra_headers)
    if vendor.env_key:
        headers[vendor.auth_header] = vendor.auth_prefix + key
    budget = ByteBudget()
    url, pages, count = vendor.list_url, [], 0
    for _ in range(MAX_PAGES):
        payload = fetch_json(url, headers, budget)
        count += len(_entries(vendor, payload))
        if count > MAX_LISTED_MODELS:
            raise WatchError(f'listing exceeds {MAX_LISTED_MODELS} entries')
        pages.append(payload)
        url = _next_url(vendor, payload, secret_values)
        if url is None:
            return pages
    raise WatchError(f'listing exceeds {MAX_PAGES} pages')


def parse_listing(vendor: Vendor, payloads, *, secret_values=()):
    listing = Listing()
    count = 0
    for payload in payloads:
        entries = _entries(vendor, payload)
        count += len(entries)
        if count > MAX_LISTED_MODELS:
            raise WatchError(f'listing exceeds {MAX_LISTED_MODELS} entries')
        for entry in entries:
            raw_id = entry.get('name' if vendor.name == 'gemini' else 'id')
            _refuse_reflection(raw_id, secret_values)
            if vendor.name == 'gemini':
                raw_id = raw_id[len('models/'):] if isinstance(raw_id, str) and raw_id.startswith('models/') else None
            if not valid_model_id(raw_id, routed=bool(vendor.allowed_prefixes)):
                listing.dropped += 1
                continue
            listing.all_ids.add(raw_id)
            if vendor.name == 'gemini':
                methods = entry.get('supportedGenerationMethods')
                if not isinstance(methods, list) or any(not isinstance(m, str) for m in methods):
                    raise WatchError('model entry has no supportedGenerationMethods string array')
                if 'generateContent' not in methods:
                    continue
            if is_text_candidate(vendor, raw_id):
                listing.text_ids.add(raw_id)
    return listing


def _source_url(value):
    if not isinstance(value, str) or any(c.isspace() for c in value):
        return False
    try:
        parts = urllib.parse.urlsplit(value)
        return parts.scheme == 'https' and bool(parts.hostname) and parts.username is None and parts.password is None
    except ValueError:
        return False


def _load_document(path):
    try:
        with path.open('rb') as handle:
            body = handle.read(MAX_REGISTRY_BYTES + 1)
        if len(body) > MAX_REGISTRY_BYTES:
            raise WatchError('registry input exceeds 1 MiB')
        return _json_loads(body)
    except (OSError, ValueError, RecursionError):
        raise WatchError('registry input is missing, unreadable or invalid JSON') from None


def load_registry(root: Path, vendor: Vendor):
    provider = _load_document(root / 'providers' / (vendor.name + '.json'))
    document = _load_document(root / 'models' / (vendor.name + '.json'))
    if not isinstance(provider, dict) or provider.get('id') != vendor.name or not _source_url(provider.get('docs_url')):
        raise WatchError('provider record has no valid id/docs_url')
    if not isinstance(document, dict) or document.get('provider') != vendor.name or not isinstance(document.get('models'), list):
        raise WatchError('models record has no matching provider/models array')
    records = document['models']
    seen = set()
    for record in records:
        if not isinstance(record, dict) or not valid_model_id(record.get('id'), routed=bool(vendor.allowed_prefixes)):
            raise WatchError('registry contains an invalid model id')
        if record['id'] in seen or record.get('status') not in ('ga', 'preview', 'deprecated'):
            raise WatchError('registry contains a duplicate model id or invalid status')
        seen.add(record['id'])
        sources = record.get('sources')
        if not isinstance(sources, list) or not sources or not all(_source_url(s) for s in sources):
            raise WatchError('registry model has no valid sources')
    if not records:
        raise WatchError('registry models array is empty; no pricing sources to cite')
    return Registry(provider['docs_url'], records)


def check_vendor(root, vendor, env):
    key = env.get(vendor.env_key, '').strip() if vendor.env_key else ''
    if vendor.env_key and not key:
        return VendorResult(vendor, 'skipped', f'{vendor.env_key} is not set')
    if vendor.env_key and not KEY_RE.fullmatch(key):
        return VendorResult(vendor, 'error', f'{vendor.env_key} contains invalid characters')
    try:
        registry = load_registry(root, vendor)
        secrets = _known_secrets(env)
        listing = parse_listing(vendor, fetch_pages(vendor, key, secret_values=secrets),
                                secret_values=secrets)
    except WatchError as error:
        return VendorResult(vendor, 'error', str(error))
    registry_ids = {r['id'] for r in registry.records}
    active_ids = {r['id'] for r in registry.records if r['status'] in ('ga', 'preview')}
    return VendorResult(vendor, 'checked',
        added=sorted(listing.text_ids - registry_ids),
        missing=sorted(active_ids - listing.all_ids),
        unchanged=sorted(registry_ids & listing.all_ids), dropped=listing.dropped,
        registry=registry)


MODEL_FIELDS = ('display_name', 'status', 'tier', 'context_window', 'max_output_tokens',
                'input_modalities', 'probe', 'default', 'verified', 'sources')
PRICING_FIELDS = ('input', 'output', 'cache_read', 'cache_writes', 'batch_discount_percent',
                  'long_context (if applicable)', 'cache_storage_per_mtok_hour (if applicable)')


def _markdown_url(url):
    return urllib.parse.quote(url, safe='/:?#=&%+@~._-')


def candidate_markdown(result: VendorResult):
    registry, vendor = result.registry, result.vendor
    sources = sorted({s for r in registry.records for s in r['sources']})
    out = [f'# {vendor.display} model candidates', '',
        'Generated by the weekly model watch. **Nothing here is verified.**',
        'Every proposed value is TO VERIFY, including the listed identifier.',
        f'Compare with `models/{vendor.name}.json`; verify every field by hand.', '',
        f'[docs]: {_markdown_url(registry.docs_url)}',
        '', 'Official documentation from the provider record: [docs][docs].', '',
        'Existing model/pricing sources (their applicability is TO VERIFY):', '']
    for i, source in enumerate(sources, 1):
        out += [f'- [source {i}](<{_markdown_url(source)}>)']
    out += ['', 'The documentation and existing pricing sources above apply to every',
            'TO VERIFY cell below. No prices, limits, capabilities or status are inferred.', '']
    if result.added:
        out += ['## New', '']
        for model_id in result.added:
            out += [f'### `{model_id}`', '',
                f'Listed by the vendor and absent from `models/{vendor.name}.json` after text-family filters.',
                '', '| Field | Proposed value |', '|---|---|',
                f'| `id` | TO VERIFY: `{model_id}` |']
            out += [f'| `{name}` | TO VERIFY |' for name in MODEL_FIELDS]
            out += [f'| `pricing.{name}` | TO VERIFY |' for name in PRICING_FIELDS]
            out += ['| `shutdown` (only if independently deprecated) | TO VERIFY |',
                    '| `note` (if needed) | TO VERIFY |', '']
    if result.missing:
        out += ['## Missing — prompt to check, not a fact', '']
        for model_id in result.missing:
            out.append(f'- TO VERIFY: `{model_id}` is declared in `models/{vendor.name}.json` but no longer listed. '
                "Confirm the retirement in the vendor's deprecation notes before removing it; "
                'a key without access to a model also hides it.')
        out.append('')
    return '\n'.join(out)


def report(results):
    out = ['| Vendor | Status | New | Missing | Unchanged | Dropped ids |',
           '|---|---|---|---|---|---|']
    notes = []
    for result in results:
        if result.status == 'checked':
            out.append(f'| {result.vendor.display} | checked | {len(result.added)} | '
                f'{len(result.missing)} | {len(result.unchanged)} | {result.dropped} |')
        else:
            out.append(f'| {result.vendor.display} | {result.status}: {result.message} | - | - | - | - |')
        if result.status == 'skipped':
            notes.append(f'- {result.vendor.display}: `{result.vendor.env_key}` secret is absent. '
                'Any previous worksheet is carried forward, possibly stale; it was not re-checked against models/.')
        if result.dropped:
            notes.append(f'- {result.vendor.display}: {result.dropped} listed ids failed the id grammar '
                         'and were dropped unread, never echoed.')
    return '\n'.join(out + ([''] + notes if notes else []))


def pr_body(results):
    lines = ['Automated weekly text-model watch. **Unverified:** every proposed value is TO VERIFY.',
        'Only known `candidates/` worksheets are proposed. No `providers/` or `models/` edits,',
        'signing, release, or main push is part of this watch.', '', report(results), '', 'Fresh worksheets:', '']
    lines += [f'- `candidates/{r.vendor.name}.md`' for r in results if r.changed]
    lines += ['', 'A missing model is a prompt to check, not a retirement fact.',
        'Follow `docs/model-watch.md`: source every field, update `verified` and `sources`,',
        'move verified records into `models/<provider>.json`, validate, and remove handled worksheets',
        'before merging a human-owned branch. Signing stays local and outside CI.',
        '', 'Do not push human commits to `model-watch/auto`; branch from it instead.', '']
    return '\n'.join(lines)


def _check_file_target(path):
    """Reject links/special files without following a worksheet into user data."""
    for part in (path, *path.parents):
        if part.is_symlink():
            raise WatchError('output path contains a symlink')
    if path.exists() and (not path.is_file() or path.stat().st_nlink != 1):
        raise WatchError('output target is not a single regular file')


def _preflight_outputs(root, outputs):
    directory = root / 'candidates'
    for part in (directory, *directory.parents):
        if part.is_symlink():
            raise WatchError('candidates directory contains a symlink')
    if directory.exists() and not directory.is_dir():
        raise WatchError('candidates path is not a directory')
    for name in KNOWN_WORKSHEETS:
        _check_file_target(directory / name)
    seen = set()
    protected = [root / d for d in ('providers', 'models', 'harnesses', 'schema', '.git', 'candidates')]
    for path in outputs:
        if path is None:
            continue
        _check_file_target(path)
        resolved = path.resolve()
        if any(resolved == d.resolve() or d.resolve() in resolved.parents for d in protected):
            raise WatchError('metadata output cannot target registry data or candidates')
        if resolved in seen:
            raise WatchError('metadata outputs must use distinct files')
        seen.add(resolved)


def write_candidates(root, results):
    for result in results:
        if result.status != 'checked':
            continue
        path = root / 'candidates' / (result.vendor.name + '.md')
        if result.changed:
            path.parent.mkdir(exist_ok=True)
            path.write_text(candidate_markdown(result) + '\n', encoding='utf-8')
        elif path.exists():
            path.unlink()


def _write_metadata(path, text, *, append=False):
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a' if append else 'w', encoding='utf-8') as handle:
        handle.write(text)


def run(argv=None, env=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help='registry checkout root')
    parser.add_argument('--pr-body', type=Path, help='write PR body (parent directories created)')
    parser.add_argument('--summary', type=Path, help='append a Markdown job summary')
    parser.add_argument('--github-output', type=Path, help='append complete/skipped step outputs')
    args = parser.parse_args(argv)
    env = os.environ if env is None else env
    try:
        _preflight_outputs(args.root, (args.pr_body, args.summary, args.github_output))
        results = [check_vendor(args.root, v, env) for v in VENDORS]
        text = report(results)
        print(text)
        _write_metadata(args.summary, '## Model watch\n\n' + text + '\n', append=True)
        errors = [r for r in results if r.status == 'error']
        for result in errors:
            print(f'model-watch: {result.vendor.display} failed: {result.message}', file=sys.stderr)
        if errors:
            return EXIT_ERROR  # no partial worksheet mutation or artifact publication
        write_candidates(args.root, results)
        _write_metadata(args.pr_body, pr_body(results))
        complete = all(r.status == 'checked' for r in results)
        skipped = ' '.join(r.vendor.name for r in results if r.status == 'skipped')
        _write_metadata(args.github_output, f"complete={'true' if complete else 'false'}\nskipped={skipped}\n", append=True)
        return EXIT_CHANGES if any(r.changed for r in results) else EXIT_NO_CHANGES
    except (OSError, WatchError) as error:
        # Paths and OS messages can contain private data; expose only the class.
        print(f'model-watch: cannot read/write watch outputs ({type(error).__name__})', file=sys.stderr)
        return EXIT_ERROR


if __name__ == '__main__':
    sys.exit(run())
