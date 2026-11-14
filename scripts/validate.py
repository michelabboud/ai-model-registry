#!/usr/bin/env python3
"""Validate registry data offline with Python 3.11+ and no dependencies.

This is deliberately a closed JSON Schema subset, not a general-purpose engine.
The schema guard fails closed before any data is inspected. --root selects data;
policy always comes from schema/ beside this script's repository.
"""
import argparse
from datetime import date, datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import urlsplit

MAX_BYTES = 1024 * 1024
MAX_DEPTH = 32
MAX_VALUE_CHARS = 80
EARLIEST_VERIFIED = date(2024, 1, 1)
REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILES = {'providers': 'provider.schema.json', 'models': 'models.schema.json',
                'harnesses': 'harness.schema.json'}
KEYWORDS = frozenset(('$schema', '$id', 'title', 'description', 'type', 'properties',
                      'required', 'additionalProperties', 'enum', 'const', 'pattern',
                      'minLength', 'maxLength', 'minimum', 'maximum', 'items',
                      'minItems', 'maxItems', 'uniqueItems', 'not', '$defs', '$ref', 'if', 'then'))
TYPES = frozenset(('object', 'array', 'string', 'integer', 'number', 'boolean', 'null'))
BARE_COMMAND = re.compile(r'^[A-Za-z0-9._-]{1,64}$')
ENV_NAME = re.compile(r'^[A-Z_][A-Z0-9_]{0,63}$')
DENIED_ENV_NAMES = frozenset(('PATH', 'HOME', 'SHELL', 'IFS', 'ENV', 'BASH_ENV', 'PS4',
                             'NODE_OPTIONS', 'NODE_PATH', 'PYTHONPATH', 'PYTHONSTARTUP',
                             'PERL5OPT', 'PERL5LIB', 'RUBYOPT', 'RUBYLIB'))
DENIED_ENV_PREFIXES = ('LD_', 'DYLD_', 'GIT_', 'SSH_')
DATE_PATTERN = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$')


class InputError(ValueError):
    """Untrusted bytes do not meet the input contract."""


class SchemaError(ValueError):
    """A schema asks for unsupported or malformed policy."""


def pointer(parent, token):
    return parent + '/' + str(token).replace('~', '~0').replace('/', '~1')


def preview(value):
    rendered = repr(value)
    return rendered if len(rendered) <= MAX_VALUE_CHARS else rendered[:MAX_VALUE_CHARS - 3] + '...'


def reject_constant(value):
    raise InputError('non-finite JSON number is forbidden: ' + preview(value))


def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise InputError('non-finite JSON number is forbidden: ' + preview(value))
    return result


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError('duplicate JSON key: ' + preview(key))
        result[key] = value
    return result


def check_depth(text):
    """Count containers before json.loads, respecting quoted/escaped delimiters."""
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '{[':
            depth += 1
            if depth > MAX_DEPTH:
                raise InputError(f'JSON nesting exceeds {MAX_DEPTH}')
        elif char in '}]':
            depth -= 1


def read_json(path):
    """Bound reads and refuse links/nonregular files, including policy files."""
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        if path.is_symlink():
            raise InputError('symlinks are forbidden')
        with os.fdopen(os.open(path, flags), 'rb') as handle:
            metadata = os.fstat(handle.fileno())
            if not stat.S_ISREG(metadata.st_mode):
                raise InputError('expected a regular file')
            if metadata.st_size > MAX_BYTES:
                raise InputError(f'file exceeds {MAX_BYTES} bytes (1 MiB)')
            raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise InputError(f'file exceeds {MAX_BYTES} bytes (1 MiB)')
        text = raw.decode('utf-8', errors='strict')
        check_depth(text)
        return json.loads(text, object_pairs_hook=unique_object,
                          parse_constant=reject_constant, parse_float=finite_float)
    except UnicodeDecodeError as exc:
        raise InputError('file is not UTF-8') from exc
    except json.JSONDecodeError as exc:
        raise InputError(f'invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}') from exc
    except (OSError, RecursionError) as exc:
        raise InputError('cannot read JSON: ' + preview(str(exc))) from exc
    except ValueError as exc:
        if isinstance(exc, InputError):
            raise
        raise InputError('invalid JSON: ' + preview(str(exc))) from exc


def resolve_ref(root, reference):
    if not isinstance(reference, str) or not reference.startswith('#/$defs/'):
        raise SchemaError('only local #/$defs/... references are supported')
    node = root
    try:
        for part in reference[2:].split('/'):
            node = node[part.replace('~1', '/').replace('~0', '~')]
    except (KeyError, TypeError) as exc:
        raise SchemaError('unresolved reference ' + preview(reference)) from exc
    if not isinstance(node, dict):
        raise SchemaError('reference must resolve to an object schema')
    return node


def check_schema(schema):
    """Check keywords AND their shapes recursively, never silently ignore policy."""
    def visit(node, location=''):
        if not isinstance(node, dict):
            raise SchemaError(location + ': expected an object schema')
        unknown = node.keys() - KEYWORDS
        if unknown:
            raise SchemaError(location + ': unsupported schema keyword ' + preview(sorted(unknown)[0]))
        for key, value in node.items():
            at = pointer(location, key)
            if key in ('$schema', '$id', 'title', 'description'):
                if not isinstance(value, str):
                    raise SchemaError(at + ': expected string')
            elif key == 'type':
                values = value if isinstance(value, list) else [value]
                if not values or any(not isinstance(t, str) or t not in TYPES for t in values):
                    raise SchemaError(at + ': unsupported type')
                if len(set(values)) != len(values):
                    raise SchemaError(at + ': duplicate types')
            elif key in ('properties', '$defs'):
                if not isinstance(value, dict):
                    raise SchemaError(at + ': expected object')
                for name, child in value.items():
                    visit(child, pointer(at, name))
            elif key in ('items', 'not', 'if', 'then'):
                visit(value, at)
            elif key == 'required':
                if (not isinstance(value, list) or any(not isinstance(x, str) for x in value)
                        or len(set(value)) != len(value)):
                    raise SchemaError(at + ': expected unique string array')
            elif key == 'additionalProperties':
                if value is not False:
                    raise SchemaError(at + ': only false is supported')
            elif key == 'enum':
                if not isinstance(value, list) or not value:
                    raise SchemaError(at + ': expected nonempty array')
                if any(json_equal(value[i], value[j]) for i in range(len(value)) for j in range(i)):
                    raise SchemaError(at + ': enum must contain unique values')
            elif key == 'pattern':
                if not isinstance(value, str) or not value.startswith('^') or not value.endswith('$'):
                    raise SchemaError(at + ': patterns must be strings anchored with ^ and $')
                try:
                    re.compile(value)
                except re.error as exc:
                    raise SchemaError(at + ': invalid pattern: ' + preview(str(exc))) from exc
            elif key in ('minLength', 'maxLength', 'minItems', 'maxItems'):
                if type(value) is not int or value < 0:
                    raise SchemaError(at + ': expected nonnegative integer')
            elif key in ('minimum', 'maximum'):
                if not is_number(value):
                    raise SchemaError(at + ': expected finite number')
            elif key == 'uniqueItems':
                if type(value) is not bool:
                    raise SchemaError(at + ': expected boolean')
            elif key == '$ref':
                resolve_ref(schema, value)
        if 'then' in node and 'if' not in node:
            raise SchemaError(location + ': then requires if')

    visit(schema)
    # Reject reference cycles, including those below properties/conditionals.
    def walk(node, ancestors):
        identity = id(node)
        if identity in ancestors:
            raise SchemaError('cyclic schema references are unsupported')
        ancestors = ancestors | {identity}
        if '$ref' in node:
            walk(resolve_ref(schema, node['$ref']), ancestors)
        for key in ('properties', '$defs'):
            for child in node.get(key, {}).values():
                walk(child, ancestors)
        for key in ('items', 'not', 'if', 'then'):
            if key in node:
                walk(node[key], ancestors)
    walk(schema, set())


def is_number(value):
    return type(value) is int or (type(value) is float and math.isfinite(value))


def matches_type(value, name):
    return {'object': lambda: isinstance(value, dict), 'array': lambda: isinstance(value, list),
            'string': lambda: isinstance(value, str), 'boolean': lambda: type(value) is bool,
            'null': lambda: value is None, 'number': lambda: is_number(value),
            'integer': lambda: is_number(value) and (type(value) is int or value.is_integer())}[name]()


def json_equal(left, right):
    """JSON Schema equality: booleans differ from numbers; 1 equals 1.0."""
    if is_number(left) and is_number(right):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        return len(left) == len(right) and all(json_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(json_equal(left[k], right[k]) for k in left)
    return left == right


def schema_problems(value, schema, root=None, at=''):
    """Return (JSON Pointer, message) pairs for the complete supported subset."""
    root = schema if root is None else root
    errors = []
    if '$ref' in schema:
        errors.extend(schema_problems(value, resolve_ref(root, schema['$ref']), root, at))
    types = schema.get('type')
    if types is not None:
        types = types if isinstance(types, list) else [types]
        if not any(matches_type(value, t) for t in types):
            return errors + [(at, 'expected ' + ' or '.join(types) + ', got ' + preview(value))]
    if 'const' in schema and not json_equal(value, schema['const']):
        errors.append((at, 'expected constant ' + preview(schema['const'])))
    if 'enum' in schema and not any(json_equal(value, option) for option in schema['enum']):
        errors.append((at, 'value is outside the allowed enum: ' + preview(value)))
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                errors.append((pointer(at, key), 'required property is missing'))
        props = schema.get('properties', {})
        for key, child in value.items():
            if key in props:
                errors.extend(schema_problems(child, props[key], root, pointer(at, key)))
            elif schema.get('additionalProperties') is False:
                errors.append((pointer(at, key), 'unknown property'))
    if isinstance(value, list):
        for key, comparison in (('minItems', len(value) < schema.get('minItems', 0)),
                                ('maxItems', len(value) > schema.get('maxItems', len(value)))):
            if comparison:
                errors.append((at, f'array violates {key}={schema[key]}'))
        if schema.get('uniqueItems'):
            for index, item in enumerate(value):
                if any(json_equal(item, previous) for previous in value[:index]):
                    errors.append((pointer(at, index), 'duplicate array item'))
        if 'items' in schema:
            for index, item in enumerate(value):
                errors.extend(schema_problems(item, schema['items'], root, pointer(at, index)))
    if isinstance(value, str):
        if 'pattern' in schema and re.fullmatch(schema['pattern'], value) is None:
            errors.append((at, 'value does not match required pattern: ' + preview(value)))
        for key, violation in (('minLength', len(value) < schema.get('minLength', 0)),
                               ('maxLength', len(value) > schema.get('maxLength', len(value)))):
            if violation:
                errors.append((at, f'string violates {key}={schema[key]}: ' + preview(value)))
    if is_number(value):
        if 'minimum' in schema and value < schema['minimum']:
            errors.append((at, f'number must be >= {schema["minimum"]}'))
        if 'maximum' in schema and value > schema['maximum']:
            errors.append((at, f'number must be <= {schema["maximum"]}'))
    if 'not' in schema and not schema_problems(value, schema['not'], root, at):
        errors.append((at, 'value matches a forbidden schema'))
    if 'if' in schema and not schema_problems(value, schema['if'], root, at) and 'then' in schema:
        errors.extend(schema_problems(value, schema['then'], root, at))
    return errors


def valid_date(value):
    if not isinstance(value, str) or DATE_PATTERN.fullmatch(value) is None:
        raise ValueError('expected YYYY-MM-DD')
    return date.fromisoformat(value)


def url_problem(value, base=False):
    if not isinstance(value, str):
        return None  # Type errors are reported by the schema pass.
    if any(ord(c) <= 32 or ord(c) == 127 for c in value) or '\\' in value:
        return 'URL must not contain whitespace, control characters or backslashes'
    candidate = value
    if base:
        candidate = candidate.replace('{region}', 'example-region').replace('{project}', 'example-project')
        if '{' in candidate or '}' in candidate:
            return 'base_url permits only {region} and {project} placeholders'
        if '?' in candidate or '#' in candidate:
            return 'base_url must not contain a query or fragment'
    elif '{' in candidate or '}' in candidate:
        return 'placeholders are permitted only in base_url'
    try:
        parsed = urlsplit(candidate)
        if parsed.scheme != 'https' or not candidate.startswith('https://') or not parsed.hostname:
            return 'URL requires https:// and a host'
        if parsed.username is not None or parsed.password is not None or '@' in parsed.netloc:
            return 'URL userinfo is forbidden'
        # Accessing port rejects malformed and out-of-range port numbers.
        _ = parsed.port
        if '%' in parsed.hostname:
            return 'URL host must not contain percent escapes'
        host = parsed.hostname
        if ':' not in host:
            # DNS names, including internationalized names, are accepted; no DNS/network lookup.
            ascii_host = host.encode('idna').decode('ascii')
            labels = ascii_host.rstrip('.').split('.')
            if len(ascii_host) > 253 or any(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', label) is None for label in labels):
                return 'URL host is invalid'
    except (ValueError, UnicodeError) as exc:
        return 'invalid URL: ' + preview(str(exc))
    return None


def semantic_problems(data, kind, stem, provider_stems, today):
    errors = []
    if not isinstance(data, dict):
        return errors
    id_key = 'provider' if kind == 'models' else 'id'
    if data.get(id_key) != stem:
        errors.append(('/' + id_key, 'must equal the file stem ' + preview(stem)))
    if kind == 'models' and stem not in provider_stems:
        errors.append(('/provider', 'matching providers/' + preview(stem) + '.json is required'))

    def check_metadata(record, at):
        if 'verified' in record:
            try:
                verified = valid_date(record['verified'])
                if not EARLIEST_VERIFIED <= verified <= today:
                    errors.append((pointer(at, 'verified'), f'verified must be between {EARLIEST_VERIFIED} and {today} (UTC)'))
            except ValueError:
                errors.append((pointer(at, 'verified'), 'verified must be a real YYYY-MM-DD date'))
        for key in ('base_url', 'docs_url'):
            if key in record:
                problem = url_problem(record[key], base=(key == 'base_url'))
                if problem:
                    errors.append((pointer(at, key), problem))
        if isinstance(record.get('sources'), list):
            for index, source in enumerate(record['sources']):
                problem = url_problem(source)
                if problem:
                    errors.append((pointer(pointer(at, 'sources'), index), problem))

    if kind != 'models':
        check_metadata(data, '')
    if kind == 'models' and isinstance(data.get('models'), list):
        models = data['models']
        seen = set()
        for index, model in enumerate(models):
            if not isinstance(model, dict):
                continue
            at = pointer('/models', index)
            check_metadata(model, at)
            model_id = model.get('id')
            if isinstance(model_id, str):
                if model_id in seen:
                    errors.append((pointer(at, 'id'), 'model id must be unique within this file'))
                seen.add(model_id)
            if model.get('status') == 'deprecated' and 'shutdown' not in model:
                errors.append((pointer(at, 'shutdown'), 'deprecated model requires shutdown date'))
            if model.get('status') != 'deprecated' and 'shutdown' in model:
                errors.append((pointer(at, 'shutdown'), 'shutdown is permitted only for deprecated models'))
            if 'shutdown' in model:
                try:
                    valid_date(model['shutdown'])
                except ValueError:
                    errors.append((pointer(at, 'shutdown'), 'shutdown must be a real YYYY-MM-DD date'))
            modalities = model.get('input_modalities')
            if isinstance(modalities, list) and 'text' not in modalities:
                errors.append((pointer(at, 'input_modalities'), 'input_modalities must include text'))
            for flag in ('probe', 'default'):
                if model.get(flag) is True and model.get('status') != 'ga':
                    errors.append((pointer(at, flag), flag + ' must select a ga model'))
        for flag in ('probe', 'default'):
            selected = [(i, m) for i, m in enumerate(models) if isinstance(m, dict) and m.get(flag) is True]
            if len(selected) != 1:
                errors.append(('/models', f'exactly one {flag}: true is required; found {len(selected)}'))
            if flag == 'probe' and len(selected) == 1:
                index, probe = selected[0]
                pricing = probe.get('pricing')
                cost = pricing.get('input') if isinstance(pricing, dict) else None
                at = f'/models/{index}/pricing/input'
                if cost is None:
                    errors.append((at, 'probe input price must be published (not null)'))
                elif is_number(cost):
                    for other in models:
                        if not isinstance(other, dict) or other.get('status') != 'ga':
                            continue
                        modalities = other.get('input_modalities')
                        other_prices = other.get('pricing')
                        other_cost = other_prices.get('input') if isinstance(other_prices, dict) else None
                        if isinstance(modalities, list) and 'text' in modalities and is_number(other_cost) and cost > other_cost:
                            errors.append((at, 'probe must have the cheapest non-null ga text input price'))
                            break
    if kind == 'harness':
        # These restrictions deliberately survive edits to the published schema.
        commands = [('/command', data.get('command'))]
        if isinstance(data.get('aliases'), list):
            commands.extend((f'/aliases/{i}', alias) for i, alias in enumerate(data['aliases']))
        for at, command in commands:
            if isinstance(command, str) and (BARE_COMMAND.fullmatch(command) is None or command in ('.', '..')):
                errors.append((at, 'command must be a bare name, excluding . and ..'))
        if isinstance(data.get('env'), list):
            seen = set()
            for index, entry in enumerate(data['env']):
                if not isinstance(entry, dict) or not isinstance(entry.get('name'), str):
                    continue
                name = entry['name']
                at = f'/env/{index}/name'
                if ENV_NAME.fullmatch(name) is None or name in DENIED_ENV_NAMES or name.startswith(DENIED_ENV_PREFIXES):
                    errors.append((at, 'environment name is forbidden: ' + preview(name)))
                if name in seen:
                    errors.append((at, 'environment names must be unique'))
                seen.add(name)
        version_match = data.get('version_match')
        if isinstance(version_match, dict) and isinstance(version_match.get('major_pattern'), str):
            try:
                compiled = re.compile(version_match['major_pattern'])
                if compiled.groups == 0:
                    errors.append(('/version_match/major_pattern', 'regex requires at least one capture group'))
            except (re.error, OverflowError, RecursionError) as exc:
                errors.append(('/version_match/major_pattern', 'invalid regex: ' + preview(str(exc))))
    return errors


def validate(root, schema_dir=None):
    schemas, problems, files = {}, [], []

    def add(path, at, message):
        problem = {'path': path, 'pointer': at, 'message': message}
        if problem not in problems:
            problems.append(problem)

    schema_dir = REPO_ROOT / 'schema' if schema_dir is None else schema_dir
    for directory, filename in SCHEMA_FILES.items():
        try:
            schema = read_json(schema_dir / filename)
            check_schema(schema)
            schemas[directory] = schema
        except (InputError, SchemaError) as exc:
            add('schema/' + filename, '', str(exc))
    if problems:
        return make_report(0, problems)
    for directory in SCHEMA_FILES:
        folder = root / directory
        if folder.is_symlink() or not folder.is_dir():
            add(directory, '', 'expected a directory, not a symlink')
            continue
        try:
            entries = sorted(folder.iterdir(), key=lambda path: path.name)
            for path in entries:
                display = directory + '/' + path.name
                metadata = path.lstat()
                if not stat.S_ISREG(metadata.st_mode):
                    add(display, '', 'only regular JSON files and an empty .gitkeep are allowed; no subdirectories or symlinks')
                elif path.name == '.gitkeep' and metadata.st_size == 0:
                    continue
                elif path.suffix != '.json':
                    add(display, '', 'unexpected file; only *.json and an empty .gitkeep are allowed')
                else:
                    files.append((directory, path, display))
        except OSError as exc:
            add(directory, '', 'cannot inspect directory: ' + preview(str(exc)))
    provider_stems = {path.stem for kind, path, _ in files if kind == 'providers'}
    today = datetime.now(timezone.utc).date()
    for directory, path, display in files:
        try:
            data = read_json(path)
        except InputError as exc:
            add(display, '', str(exc))
            continue
        kind = {'providers': 'provider', 'models': 'models', 'harnesses': 'harness'}[directory]
        for at, message in schema_problems(data, schemas[directory]):
            add(display, at, message)
        for at, message in semantic_problems(data, kind, path.stem, provider_stems, today):
            add(display, at, message)
    return make_report(len(files), problems)


def make_report(count, problems):
    return {'valid': not problems, 'files_checked': count, 'problem_count': len(problems), 'problems': problems}


def display_text(value):
    # Paths and pointers are untrusted too; guarantee one physical line per error.
    return json.dumps(value, ensure_ascii=True)[1:-1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=REPO_ROOT, help='data root (policy stays beside this script)')
    parser.add_argument('--json', action='store_true', help='emit one machine-readable JSON report')
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error('--root must be an existing directory')
    report = validate(args.root)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        for problem in report['problems']:
            print(f'{display_text(problem["path"])}: {display_text(problem["pointer"])}: {display_text(problem["message"])}')
        print(f'{report["files_checked"]} files checked; {report["problem_count"]} problems; ' + ('clean' if report['valid'] else 'invalid'))
    return 0 if report['valid'] else 1


if __name__ == '__main__':
    sys.exit(main())
