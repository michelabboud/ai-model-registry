# One-time signing-key ceremony for Michel

This is a manual procedure, not an executable script. Do not run it in CI or
during ordinary development. Python 3.11+, Git and OpenSSL >= 3.0 must be
available. Check `openssl version` first. This repository has no real key yet.

## First key

1. In a trusted local checkout, confirm that neither
   `~/.config/ai-model-registry/signing-key.pem` nor
   `keys/registry-signing-key.pub.pem` exists, including dangling symlinks.
   If either exists, inspect it; do not overwrite it or repeat key generation.
2. Create the private directory and key, outside every checkout:

   ```sh
   install -d -m 0700 ~/.config/ai-model-registry
   (umask 077; openssl genpkey -algorithm ed25519 -out ~/.config/ai-model-registry/signing-key.pem)
   ```

   Check owner and mode with
   `stat -c '%U %a' ~/.config/ai-model-registry/signing-key.pem` on Linux.
   Mode must be exactly 0600 and the owner must be the user running the signer.
   Do not print or inspect the private PEM contents. Do not use a symlink.
3. Export only its public key:

   ```sh
   openssl pkey -in ~/.config/ai-model-registry/signing-key.pem -pubout -out keys/registry-signing-key.pub.pem
   ```

4. Derive the raw 32-byte public key for compiled clients. This pipeline emits
   only public bytes (the final 32 bytes of Ed25519 SubjectPublicKeyInfo DER):

   ```sh
   openssl pkey -in ~/.config/ai-model-registry/signing-key.pem -pubout -outform DER | tail -c 32 | base64
   ```

   Record that base64 string, public PEM filename, date and first registry number
   in `keys/README.md`. Check that a client's decoded base64 is exactly 32 bytes
   and matches the PEM before distributing it. Pin this key through a trusted
   client release; an untrusted download of a public key is not a trust anchor.
5. Back up the private key to encrypted offline storage controlled by Michel,
   outside the repository and CI. Record the backup's location privately, never
   its contents. Test a restore into a private directory outside the repository,
   restore mode 0600, derive the public key with OpenSSL and compare it with the
   committed public PEM. Backup media access, encryption credentials and retention
   are Michel's manual responsibility. Do not delete the working key or backup.
6. Review the public files. Commit only `keys/registry-signing-key.pub.pem` and
   the public-key history update in `keys/README.md` through the normal source
   workflow. Never force-add an ignored PEM. Distribute the trusted public key to
   consumers, then follow [releasing.md](../docs/releasing.md).

The signer's exact signing command is
`openssl pkeyutl -sign -rawin -inkey <key> -in manifest.json -out manifest.json.sig`.
It immediately runs
`openssl pkeyutl -verify -rawin -pubin -inkey <pub.pem> -in manifest.json -sigfile manifest.json.sig`.
The resulting detached signature is exactly 64 raw bytes, without base64 or a
tool-specific wrapper. OpenSSL alone reads the private key.

## Rotation

1. Choose a new, unused private filename outside the repository, such as
   `~/.config/ai-model-registry/signing-key-YYYY-MM-DD.pem`. Create a new
   Ed25519 key with the same 0700-directory/0600-file procedure. Retain the old
   private key and its encrypted backup until Michel decides their disposition.
2. Preserve the old **public** PEM as
   `keys/registry-signing-key-YYYY-MM-DD.pub.pem`. List that file, its raw
   public-key base64, and its registry-number range in `keys/README.md`.
   Record the new key's activation and first registry number as a separate row.
3. Export the new public PEM to a new temporary **public** filename, review it,
   then update `keys/registry-signing-key.pub.pem` in a source change together
   with the history. This is an intentional key rotation, never an automatic
   signer action. Do not replace an existing private key.
4. Release updated clients carrying the new key before signing registry data
   that requires it. Clients that need historical releases retain a trusted
   old-key mapping; a compromised-key response additionally needs an explicit
   revocation and rollback policy in the client.
5. Sign the next consecutive registry release using `--key` with the new private
   filename. Verify and publish through the normal ceremony. Do not re-sign,
   replace, delete or retag old releases. Old releases stay verifiable with the
   old public key (and a verifier from its trusted historical source revision).
6. Run a documented rotation drill with throwaway keys before relying on this
   procedure in a real incident; the drill remains a backlog item.
