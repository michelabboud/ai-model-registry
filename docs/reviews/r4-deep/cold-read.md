# R4 deep review cold read

Status: UNVERIFIED initial source assessment; immutable first-read record.

Created: 2026-11-15T02:08:10.285557+00:00
Baseline: `08d9fcb03744a188fe7f26b8305efe21ee8dc125` (confirmed local HEAD).
Candidate: dirty uncommitted R4 working-tree source listed below. Dev mode: mvp.
Reviewer configuration supplied by coordinator: gpt-6.1-sol, xhigh. Actual provider/model identity, queue time and token measurements: unavailable. Fresh same-family context; shared filesystem; no process or filesystem isolation claim.

The complete assigned source/doc/test scope was read before this note. No sibling review, adjudication, or validation receipt has been opened. No network, real gh, real key, source edit, commit, tag, or push has occurred.

Initial assessment:

- Architecture follows the approved four-command split. The build validates before inspecting cleanliness or creating output. It uses sorted exact source bytes, fixed POSIX ustar metadata, canonical manifest bytes and exclusive output creation.
- Verification reads only a bounded manifest and fixed-length signature before OpenSSL authentication, then parses canonical closed JSON, checks complete-tar and member digests/sizes, exact safe membership, actual canonical headers and all padding. No extraction occurs. No reachable unsigned-payload or traversal bypass is evident from the cold read.
- The signer inspects private-key metadata and delegates key reads to OpenSSL; it validates unsigned artifacts and immediately verifies a temporary signature before exclusively creating the final signature. Wrong-key and missing-public-key paths preserve existing artifacts.
- Publication verifies before gh, paginates release/tag listings, checks the next number and existing target tag, creates exactly three assets, then checks the remote list and downloaded bytes. Recovery deliberately preserves remote partial state and instructs manual inspection.
- Key ceremony, backups, rotation, old-key retention, client pinning, minimum-client enforcement, anti-rollback state and activation responsibilities are stated. No real key or client integration is claimed.

Bounded follow-up questions, not findings:

1. Does inherited GitHub CLI repository selection (especially GH_REPO or a configured default repository) invalidate the guide's statement that origin is always the publication destination? All gh calls use cwd only and omit an explicit repository selector.
2. Does accepting a 64-byte signature through a configured OpenSSL public PEM sufficiently enforce the declared Ed25519-only protocol? The manual ceremony creates Ed25519, but code does not explicitly inspect the public key algorithm; a configuration-controlled mismatch would be hardening unless a realistic entry point is established.
3. Verify supplied receipt hashes against this exact source set and check that the complete offline suite executed signing and fake-gh paths, rather than silently skipping them.

No confirmed blocking finding at this stage. These are provisional conclusions before receipt/provenance checks and any focused reproduction.

## Read source hashes

- `scripts/release_common.py`: `f6a779eb367184a1f05fcb315a1e0fa693033dee74a102a5fbe5906cf21ba904` (20208 bytes)
- `scripts/build_release.py`: `f24a5ff769bf2baad423a8dc059c377d39f6cd0408607fb6cc553de6581151f2` (756 bytes)
- `scripts/sign_release.py`: `26895e8451dd7194dc638f4d2b7e910225fb0e396428d110f36f0affe169a066` (769 bytes)
- `scripts/verify_release.py`: `26cea1bacf4becd8bdd70e14f4080625c047d5fabfebd4037ffe53c56cd28ef9` (647 bytes)
- `scripts/publish_release.py`: `5329c76fefd64b063dce9ec8d2e880ee3c94c8655af642ac36baf440f043fe9c` (816 bytes)
- `tests/test_release.py`: `ec6442de39bc42c6f59b59ab914a37a24196238e12b01f680d1e927e58058781` (24022 bytes)
- `.gitignore`: `f2c6edc78905a1ed84d2d56d14622ced06527944a03615d72f01e772164c3c57` (78 bytes)
- `docs/releasing.md`: `fa3cc9fa7bfca074b8ae031c5b93da18d8a1e6998181965a14685e080fa725a2` (10031 bytes)
- `scripts/new_signing_key.md`: `da0034a4878ac7731d47a9240726a12dca1a0b9e6bb533681a5e47fdffd3e0fb` (4604 bytes)
- `keys/README.md`: `f19e1b3f6f47fa0efdeeb36ffbad64ff700192addc5bd6b8614e8c3116b98ab9` (1823 bytes)
- `docs/adr/0006-signing-with-openssl.md`: `2e250067ac4b20135530cc1ad0e9a94d2b86d20f664862dd21c8784a590cd6c7` (3404 bytes)
- `README.md`: `7b1de876d36ec021c59cc85ea36a4992ff7cb69a39d0fd51f917ba08ad229f6b` (12622 bytes)
- `ARCHITECTURE.md`: `f06905ccf6e305d58e0d4e109b8ae2b9e07f13a38625bf414c8a9956a88fc2ad` (13119 bytes)
