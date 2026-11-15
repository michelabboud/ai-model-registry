# 0006: Local Ed25519 signing with OpenSSL

Date: 2026-11-15

## Context

Numbered registry releases authenticate the exact canonical manifest bytes with
an Ed25519 signature. Python 3.11's standard library has no Ed25519 primitive,
and this repository permits no Python dependencies. The coordinator verified
OpenSSL 3.0.13 and its Ed25519 `genpkey`, `pkeyutl -sign -rawin`, and
`pkeyutl -verify -rawin -pubin` commands on the signing machine.

## Decision

Use the OpenSSL CLI, version 3.0 or newer, checked at the start of signing and
verification. Invoke it through `subprocess.run` with argument lists and
`shell=False`. OpenSSL alone reads the private key. Python checks only its path,
ownership, file type and exact 0600 mode. The key must be outside the resolved
repository and must not itself be a symlink. Signing is local, never in CI.
Immediately verify the raw 64-byte signature using the repository's public PEM.
No public key is installed until Michel's first release ceremony.

The archive uses Python's `tarfile` in POSIX ustar mode, with only sorted regular
JSON file entries under `providers/`, `models/`, `harnesses/`, and `schema/`.
No directory entries are emitted: consumers can create parent directories after
verification. Headers fix mtime, uid and gid to zero, clear uname/gname, and use
0644 permissions. Manifest hashes cover payload bytes and the complete tar;
neither manifest nor signature is recursively included. The date is UTC.

Verification authenticates manifest bytes before JSON parsing, then checks the
canonical closed format, tar hash/size, exact membership, safe paths, regular
file type, and each member's hash/size without extracting anything. A client
still validates data and enforces its own anti-rollback policy before activation.

Publication uses `gh` only after verification. It queries all release pages and
existing matching tag refs, admits exactly the next registry number, and creates
one release with the three named assets. It never replaces a tag or release.
The target is the current local HEAD, which must already exist on GitHub.com.
Every GitHub CLI operation explicitly pins the credential-free HTTPS/SSH origin's
host and repository, rather than inheriting `GH_REPO` or gh defaults. Only the
three public assets are copied into private temporary staging and re-verified;
upload operands are fixed basenames from that cwd. This prevents gh's own
`filename#label`/glob grammar from changing the verified literal source paths.
Publication is a single-maintainer ceremony; the read/create sequence is not a
distributed lock. Downloaded assets and the remote asset list are checked after
creation. A failure leaves remote state intact for manual inspection.

## Alternatives rejected

- `cryptography` or PyNaCl: another dependency to vet and install on the signing
  machine, contrary to the standard-library-only requirement.
- Genie's Rust publisher: Genie-specific and unsuitable as this repository's
  independent Python tooling.
- minisign/signify: another installed tool and a different signature format.

## Consequences

Signing and verification require OpenSSL >= 3.0; build and validation do not.
Publishing additionally requires authenticated `gh` and network access. No key
material is printed, copied, or read into Python memory by the release tooling.
OpenSSL errors are reported without echoing subprocess output. Temporary tests
may generate throwaway keys; no real key or signing operation is part of CI.
Key backup, manual rotation, and old-key retention are operator responsibilities.
An authentic signature establishes integrity and publisher identity, not vendor
fact accuracy, freshness, or protection from replay of a valid older release.

## Status

Accepted: coordinator-selected signing backend in the R4 brief.
