# Releasing registry data

Dev mode: mvp. This is a local, manual ceremony. Signing never runs in CI.
No real signing key or registry release has been created by R4 development.
Use Python 3.11+ with its standard library; signing and verification require
OpenSSL >= 3.0. Publication additionally uses an authenticated `gh` CLI and the
network. The repository's `origin` is the publication destination: a GitHub.com
HTTPS, `git@github.com:owner/repo.git`, or Git SSH URL, with no embedded password.
Other hosts and local remotes are refused. All API calls pin `github.com` and
the explicit owner/repository; create/download pass an explicit `--repo`, so
`GH_REPO`, `GH_HOST` and gh's configured default repository cannot redirect them.

## Threat and trust boundary

A contributor or release attacker could supply changed endpoints, prices, model
IDs or launcher bindings. Validation checks data constraints; signature checking
authenticates exact manifest bytes using a separately trusted key; hashing and
strict archive membership bind all payload bytes. Verification never extracts
files. Private-key bytes are read only by OpenSSL, from a regular, owned, 0600
file outside the resolved repository; symlink keys are refused. The signing
command suppresses OpenSSL diagnostics rather than risk printing key material.
An authentic signature does not establish vendor accuracy or freshness. Consumers
must retain their own minimum accepted registry number to resist replay.

## Assets and byte format

Tags are `registry/1`, `registry/2`, and so on, independently of source `VERSION`.
Each release has exactly three uploaded assets:

| Asset | Contract |
| --- | --- |
| `registry.tar` | Uncompressed POSIX ustar from Python `tarfile`, only `*.json` under `providers/`, `models/`, `harnesses/`, `schema/`, sorted by full relative path. |
| `manifest.json` | UTF-8 JSON, sorted keys, `separators=(",", ":")`, `ensure_ascii=False`, and one trailing newline. |
| `manifest.json.sig` | Raw 64-byte Ed25519 signature over the exact manifest bytes. |

Every tar member is a regular file, mode 0644, mtime/uid/gid 0, uname/gname empty.
There are **no directory entries**: ustar does not require them, and consumers
can create parents in their own staging directory after verification. There are
no links, devices, PAX/GNU extension headers, `.gitkeep` markers, scripts, keys,
research files, `media/`, or self-referential manifest/signature entries. Python
`tarfile` emits two zero end blocks and zero padding to a 10,240-byte record
boundary. Verification checks canonical headers, member padding and the entire
trailer, so appended or hidden members cannot pass. Same input file paths/bytes
produce byte-identical archives, regardless of source permissions or timestamps.

The manifest has exactly this shape (example hashes elided here, not an artifact):

```json
{"format":1,"registry":1,"created":"YYYY-MM-DD","repo_version":"VERSION","min_client":{"the-operator":"0.17.0"},"files":{"providers/example.json":{"sha256":"<64 lowercase hex characters>","bytes":123}},"tar":{"sha256":"<64 lowercase hex characters>","bytes":10240}}
```

The actual canonical serialization sorts every object's keys. `created` is the
build's UTC calendar date. `repo_version` is the bare source `VERSION` string.
`files` hashes exact payload bytes; `tar` hashes the complete archive. The
manifest never hashes itself or the signature. Building on another UTC date
changes the manifest, even when the tar remains identical.

## Ceremony

1. Review and checkpoint the intended source and data through the coordinator's
   normal workflow. Commit and push the target source commit to `origin`; the
   publisher targets the **current local HEAD**. Check `git remote -v` and
   `git rev-parse HEAD`. The archive must represent that intended source commit.
   Builds refuse any staged, modified or untracked change under the four data
   paths. Unrelated documentation/tooling changes do not fail that data-only
   check. Do not edit the release directory after signing.
2. Run the offline gates:

   ```sh
   python3 scripts/validate.py
   python3 -m unittest discover -s tests
   openssl version
   ```

   Signing tests generate only temporary throwaway Ed25519 keys; they skip with
   a clear message if OpenSSL >= 3.0 is absent. Builds and validator tests still
   run without OpenSSL. The release tests shadow `gh` with a fake executable and
   use local clones; no real GitHub request is made.
3. For the first release, Michel follows
   [the one-time key procedure](../scripts/new_signing_key.md). Commit only the
   public PEM and its raw 32-byte base64/history in [keys/README.md](../keys/README.md).
   Clients pin the public key through their own trusted source/client releases.
   Never obtain the trust key solely from the same untrusted assets being checked.
4. Choose the next positive number `N`. The publisher checks every page of
   GitHub releases, including draft/prerelease entries. The highest canonical
   `registry/N` plus one is required; unrelated source-version releases are
   ignored. A malformed `registry/*` release fails closed. With no registry
   release, the first number is 1. Only one maintainer publishes at a time:
   GitHub CLI preflight checks do not constitute a distributed publication lock.
5. Build into a new output directory, or an existing empty one:

   ```sh
   python3 scripts/build_release.py --registry 1 --out dist/registry-1
   ```

   Substitute the chosen `N` throughout. Validation runs first; Git cleanliness
   is checked next. No key is needed. Output beneath a data path or through a
   final directory symlink is refused. Existing nonempty directories and files
   are never overwritten. Retain partially built artifacts for diagnosis and
   use another new directory for a retry.
6. Sign locally. The private key must belong to the current user, have exact
   mode 0600, be outside this repository after path resolution, and not itself
   be a symlink. Confirm the trusted public PEM is committed first:

   ```sh
   python3 scripts/sign_release.py --dir dist/registry-1 --key ~/.config/ai-model-registry/signing-key.pem
   ```

   The script first checks the unsigned manifest and archive, then invokes
   OpenSSL and immediately verifies with `keys/registry-signing-key.pub.pem`.
   A wrong key leaves no final signature. An existing signature is preserved;
   the script refuses to overwrite it. Python never reads, logs or copies the
   private key. Temporary signature files contain only public signature bytes.
7. Verify the final three assets:

   ```sh
   python3 scripts/verify_release.py --dir dist/registry-1
   ```

   Exit 0 means signature, canonical manifest format, every SHA-256 and size,
   exact sorted membership, safe paths, regular file types, canonical ustar
   headers and zero padding all passed. Operational refusals exit 1; argparse
   reports usage errors with exit 2. Missing public PEM, unavailable/old OpenSSL,
   malformed inputs and bad signatures fail cleanly without a traceback.
8. Check `gh auth status --hostname github.com` and the intended `origin`, then publish:

   ```sh
   python3 scripts/publish_release.py --dir dist/registry-1
   ```

   Verification runs **before any `gh` invocation**. The script refuses an
   existing target tag, even if it has no release, and never moves/deletes tags
   or releases. `gh release create registry/N --target <HEAD> ...` creates the
   remote tag and release with exactly the three assets. Before creation, the
   publisher copies only these public assets into a private temporary directory,
   verifies the staged copy, and supplies fixed asset basenames from that cwd.
   This preserves literal directories containing `#` or glob characters despite
   gh's `filename#label`/pattern operand syntax; no private key is copied.
   GitHub's automatically
   generated source-code archives are not uploaded release assets. The script
   then checks the remote asset list, downloads the three files into a temporary
   directory and compares every byte with the verified staged originals. Success prints
   the registry number, file count and tar SHA-256. Preserve those receipts and
   the local assets as publication evidence.
9. Confirm consumer acceptance separately: authenticate the downloaded release,
   enforce minimum-client and rollback rules, validate data, stage safely, and
   activate only after every check. Source tests or upload success alone do not
   establish client integration.

## Client reference verification

`verify_release.py` is the reference behavior. Authenticate the exact manifest
bytes **before parsing its JSON**, using the client's pinned Ed25519 key. Require
a 64-byte signature, closed format 1, positive integer registry number, real
`YYYY-MM-DD` date, version string, supported minimum-client map, safe relative
JSON paths and canonical serialization. Reject duplicate JSON keys. Check the
whole tar's hash and byte length; inspect each regular member's hash and byte
length, prohibit absolute paths, `..`, backslashes, drive/colon paths, links,
devices and duplicate/extra/missing members. Require the sorted canonical ustar
headers and zero padding described above. The reference inspects all bytes and
does not call `extractall`.

After those checks, a client can create its own fresh staging directory, create
parents safely, and write only the verified regular files. Apply schema and
semantic validation before activating data. Client application version checks,
persisted anti-rollback state, transaction/activation and old-key selection are
consumer responsibilities, separate from this command's integrity check.

## Failure and recovery

A preflight refusal creates no remote state. A failure during release creation,
asset inspection, download or comparison may leave a tag and a partial or fully
uploaded release on GitHub. The script intentionally performs no rollback,
deletion, replacement, tag movement or `--clobber`. Inspect
`gh release view registry/N --repo github.com/OWNER/REPO --json tagName,assets,isDraft,isPrerelease`
and the tag before deciding manual recovery. Replace `OWNER/REPO` with the
validated publication origin's owner/repository and `N` with the attempted number;
keep the explicit host/repository even if `GH_REPO` or gh defaults point elsewhere.
Do not blindly rerun publication or skip a
reserved number. A timeout is uncertain remote state, not proof nothing happened.
Serialize maintainers and resolve partial publication explicitly.

Backup and rotation are manual; follow
[the rotation procedure](../scripts/new_signing_key.md#rotation) and retain old
public keys/ranges in [keys/README.md](../keys/README.md). Old releases remain
unchanged and require their original trusted key. A rotation drill and possible
transparency log are tracked in [BACKLOG.md](../BACKLOG.md).
