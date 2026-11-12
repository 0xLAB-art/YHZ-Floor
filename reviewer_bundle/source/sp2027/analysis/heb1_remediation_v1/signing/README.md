# HEB-1 remediation v1: protected signing utility

This is a new, standalone, offline utility. It does **not** modify or replace
the frozen HEB-1 validators, fixtures, results, freeze manifests, manuscript,
or any historical rerun.

## Scope

- Ed25519 private keys are generated with `Ed25519PrivateKey.generate()`.
- Private key JSON files are kept in a separate `0700` directory and written
  atomically with `0600` permissions. They are never placed in a public bundle
  or printed. The caller must ensure the private directory and its ancestors
  are trusted and not attacker-controlled; this utility does not establish
  ownership of the filesystem or enforce that the public-bundle destination is
  outside the private directory.
- Public bundles contain only `key_id`, issuer `role`, and public key bytes.
- Every signature covers the fixed domain, evidence `kind`, explicit `context`,
  issuer role, key identity, and payload.
- A role policy authorizes which evidence kinds and contexts each issuer may
  sign. Verification rejects role or context mismatch before accepting a
  signature.

Run the focused offline tests from this directory:

```sh
python3 -m unittest -v test_protected_signing.py
```

The historical finding is independently verified by the regression test: the
old fixture source derives private bytes from the public session identifier and
constant (`sha256("eb-iar-b|key|<session>")`). This remediation deliberately
does not import or alter that fixture generator.

## Incompatibilities and limits

The record format is `heb1-protected-signing-v1`, not the frozen Experiment B
certificate/signature format. Existing frozen bundles cannot be verified by
this utility without an explicit, separately reviewed adapter. This utility
does not provide key rotation, revocation, replay/epoch handling, secure key
storage, process attestation, aggregation authentication, or a production
submission gateway. It demonstrates bounded key provenance and signed
role/kind/context separation only; it is **not a production security claim**.
