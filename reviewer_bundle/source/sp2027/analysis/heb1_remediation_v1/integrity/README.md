# Bounded integrity remediation v1

This directory is a **new, standalone helper** for future HEB/B2/IAR-C-style
runs. It does not rewrite, freeze, validate retroactively, or rerun historical
manifests/results. The existing B2 and IAR-C artifacts remain read-only
context: the audit identified that B2 did not check all declared freeze fields
and IAR-C did not verify its frozen case-manifest hash.

## Contract

`manifest_verifier.py` accepts `acts-integrity-remediation/1` manifests with:

- a repo-relative, SHA-256-bound protocol and measurement runner;
- an explicit non-empty map of all executable/supporting components;
- separately bound labels and trust files; and
- an exact recursive case inventory (`root`, relative `files`→SHA-256 map, and
  `count`). Missing, changed, duplicated, unsafe, symlinked, or unexpected
  files fail the preflight.

Paths must be relative and cannot contain `..`; resolved paths must remain
inside the supplied repository root. Hashes are lowercase SHA-256 values.

Call `preflight_then_execute(manifest, repo_root, callback)` from a future
runner. It performs the complete preflight first and invokes the callback only
on success. A failed preflight raises `PreflightError`, so no measurement code
is reached. The CLI prints a JSON report and exits 0/1 for pass/fail.

The verifier deliberately does not infer missing paths or reconstruct the
historical B2 case-inventory hashing convention. An adapter may produce this
explicit manifest for a new run, but must not claim that doing so repairs old
results.

## Focused tests

From this directory:

```sh
pytest -q test_manifest_verifier.py
```

The tests create temporary synthetic bundles only. They cover a clean bundle,
component tampering, missing trust material, unexpected recursive case files,
path escape, and both sides of the preflight-before-execution ordering.

## Limitations

This is file-integrity and inventory preflight, not cryptographic signature
verification, semantic certificate adjudication, provider/network isolation,
process sandboxing, or immutable runtime attestation. It cannot establish a
retroactive freeze or upgrade historical evidence. A future runner must still
bind its emitted results to the verified manifest and preserve raw failures.

## Read-only adjudication audit

`../adjudication/audit_recompute.py` is a separate, read-only utility for the
HEB/IAR audit questions. It can:

- compare HEB public target fields with private target state, including every
  primitive-specific cryptographic field, and compare the certificate target
  hash with the private target hash;
- report, rather than erase, every JSON-pointer difference between IAR-A public
  and private certificates; and
- recompute common-contract metrics with raw denominators. Malformed cases are
  excluded from substantive rates, and partial-claim functionality is `N/A`
  when no eligible partial cases exist.

The utility reports integrity status separately from semantic differences. A
parseable public/private certificate pair may have intentional private-only
truth fields; that is evidence to review, not permission to assert semantic
equivalence. It does not rerun HEB, IAR-A, V2, or any provider. Historical
limitations remain: target-hash conventions are taken from the preserved
certificate/private metadata, and metrics cannot establish claims outside the
preserved case rows.

For the common-contract recomputation:

```sh
python3 ../adjudication/audit_recompute.py \
  ../../experiment_b_20261019/iar_c/runs/20261019_121621/results.json
```

### TOCTOU boundary

Preflight hashes are a point-in-time observation. They do not guarantee that
the bytes remain unchanged during the callback: a file can change after
preflight and before or during execution. A production runner must use an
immutable snapshot, trusted read-only mount, or equivalent OS-level control if
that stronger guarantee is required; this helper does not provide it.
