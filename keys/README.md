# Registry verification keys

public key added at the first release ceremony

No signing key exists in this checkout. The first ceremony adds only the public
Ed25519 PEM as `keys/registry-signing-key.pub.pem`. The private key stays outside
the repository, owned by Michel, mode 0600. Signing and verification commands
refuse cleanly until the public PEM exists; data validation and builds do not
require it.

During that ceremony, record the **raw 32-byte public key as base64** below for
clients that compile it in. The conversion command and key creation procedure
are in [new_signing_key.md](../scripts/new_signing_key.md). Do not put a private
PEM, its contents, or a private-key backup here. `*.pem` is ignored except public
PEMs directly under `keys/`.

## Trusted key history

There are no keys or registry releases to list yet. At the first ceremony add
the public PEM filename, raw public-key base64, activation date, and first
`registry/N`. On rotation, retain the old public PEM under a dated `.pub.pem`
filename here and list its registry-number range. Public-key history must remain
available so old releases can still be authenticated with their original keys.
No example or throwaway test key is a trust anchor.

## Backup and rotation

Keep encrypted offline private-key backups outside this checkout and outside CI;
test restoration to a private 0700 directory and compare the derived public key.
Follow [the manual rotation procedure](../scripts/new_signing_key.md#rotation)
before changing the current public PEM. Publish a client release carrying the
new trusted key before it must consume newly signed registry data. An old
signature remains verifiable with its old public key; switching the current PEM
does not re-sign historical releases or let the current verifier authenticate
them automatically.
