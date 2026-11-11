# Signed context validation helper

`context_validator.py` is a new, standalone helper for future bundles. It is
not imported by, and does not alter, the frozen V3-full implementation. The
existing V3-full duplicate-evidence check remains authoritative and is not
repeated as a claimed defect here.

## Contract

`validate_signed_context` requires exactly these signed fields:
`kind`, `domain`, `target_id`, `attempt_id`, `epoch`, and `role`. It verifies
the signature over canonical JSON for that exact object, then compares every
field to the caller's expected binding. This binds kind/domain as well as the
target, attempt, epoch, and role; changing any field invalidates the existing
signature or expected binding.

The signature covers the context object only. It does **not** cover payload or
artifact bytes, their hashes, or claim attribution. This helper alone cannot
authenticate evidence contents or establish that a claim came from the signed
artifact; a future adapter must add explicit artifact hashing/signing and
semantic attribution checks.

`confine_bundle_path` rejects absolute paths, `..` traversal, missing/non-file
paths, and symlinks in any path component. It returns a resolved regular file
only when it remains below the bundle root.

Replay is not inferred from a timestamp or claimed as stateless freshness.
Callers that need a replay limit must pass an explicit `ReplayState`, whose
ledger counts the exact six-field context key. Without that state, validation
means signature and binding validation only.

`ReplayState` is an in-memory, nonpersistent, non-atomic and non-thread-safe
ledger. Restarting the process resets it, so it provides no production
exactly-once guarantee. A future production runner needs separately persisted
and synchronized replay state.

Path validation is also subject to the usual filesystem TOCTOU limitation:
the checked path or symlink relation can change after validation and before
consumption. A future runner must use an appropriate atomic/open-by-handle
boundary if that race matters.

## Compatibility and deferred integration

The helper accepts the existing V3-style Ed25519 public-key interface
(`verify(signature, bytes)`) and does not require changing existing
certificate, evidence, or result schemas. Integration into a future runner is
deferred: an adapter must choose where the signed context is stored, what
bundle file it names, and which separately persisted replay ledger is trusted.
No historical result is retroactively revalidated by this helper.

Run the focused tests from this directory:

```sh
pytest -q test_context_validator.py
```
