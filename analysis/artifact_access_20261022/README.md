# ACTS-Attack full local reviewer candidate

This package supplies retained evidence and evaluator sources absent from the reduced reviewer projection. It is **locally staged, not publicly published or anonymous-release ready**. Original signed records, synthetic fixture truth, test signing keys, provider records, local paths, and the declared-author paper source are preserved. Read `DISTRIBUTION_REVIEW.json` before any external distribution. No original evidence or original manifest was rewritten to conceal those properties.

## Safe default inspection: no experimental rerun

Python 3.10+ and the standard library suffice:

```sh
python3 -B offline_checks.py verify
python3 -B offline_checks.py census --output /tmp/acts-review-census.json
```

Use a new report path. Outputs must be outside this package. Integrity verification checks every manifest-listed payload and detects missing, changed, unsafe, or unlisted files. The census reads archived records only. It does not run attack programs, evaluate mutations, contact a target or provider, or re-adjudicate cryptographic outcomes.

The census intentionally exits **2** when it reports a scientific/provenance finding: the supplied fixed-executor record has twelve successes but clock medians different from the current manuscript. It does not silently relabel this as a successful verification. Integrity failure exits 1. The twelve recorded success flags support a recorded-outcome census, not independent cryptographic validation of those operations.

`CLAIMS.json` maps central claims to evidence, optional commands and validation scope. `COPY_LINEAGE.json` records original source hashes and unchanged-copy destinations. `MANIFEST.json` separately hashes this assembled package; it does not replace any original nested manifest.

## Optional independent checks for a reviewer

These commands **perform evaluations** and were **not run during packaging**, in accordance with the author's no-rerun instruction. Use them only when deliberately undertaking independent verification. They write only to fresh output/workspace directories outside the package.

### Retained H1-R3 program execution

Requirements: Linux, Python 3.10+, bubblewrap, util-linux/prlimit and working unprivileged namespaces. Do not bypass the sandbox if namespaces are unavailable.

```sh
python3 -B review.py h1r3 --output /tmp/acts-independent-h1r3
```

This launches retained programs and independently checks fresh outputs. It does not regenerate model responses. The original component is included both expanded under `h1r3/` and as its unchanged archive under `original_archives/`. `prior_validation/BINDING.json` binds the existing portable execution report to the exact original archive, runner and retained manifest. That older report covers the component, **not a newly executed end-to-end check of this assembled package**.

### RQ3 property checks

Install the dependencies listed in `requirements-observed.txt` in an environment chosen by the reviewer; no installer runs automatically. The observed environment includes cryptography 50.0.2, in-toto 3.1.0 and securesystemslib 1.5.1. The requirements file records observed versions, not a dependency-lock proof.

```sh
python3 -B review.py property --output /tmp/acts-independent-property
```

The adapter copies the source tree into that output directory and calls the original seeded mutant generator/checker on the four retained certificate inventories, under both frozen semantics. The archived files contain aggregate censuses, not a per-mutant historical decision ledger. The code regenerates mutants only when the reviewer explicitly runs this command. A matching result would support bounded policy behavior, not formal soundness or deployed failure prevalence. Shared implementation assumptions and corpus calibration remain limitations.

### Configured in-toto comparison

```sh
python3 -B review.py intoto --output /tmp/acts-independent-intoto
```

This new packaging adapter selects the reviewer's in-toto executable prefix, uses a copied workspace, relocates historical absolute paths only in unsigned baseline JSON copies and writes a relocation inventory. Signed E2A certificates are unchanged. The SLSA network arm is explicitly skipped and cannot be compared with its historical result. The adapter has been syntax/dependency inspected only; it was not empirically validated during packaging and must not be called a completed independent replication.

### ECDSA correction evidence

The complete H1-R3 component supplies the exact recorded programs, observations, outputs and fixture state. The original correction-diagnostic code and retained per-session diagnostic are supplied under `source/sp2027/analysis/lineage_20261020`. The safe default census recounts the twenty recorded corrected scalars; it does not freshly prove those corrections. The legacy diagnostic uses its original repository-relative layout and invokes recorded programs, so it is not advertised as an already validated portable/sandboxed command. Its further portability work is an explicit remaining boundary.

## What has and has not changed

- Evidence copies are byte-preserving, with source/destination hashes recorded. Failed attempts retained by the source remain separate; copies add no trials.
- Freeze and amendment files are included without describing internal timestamps as third-party preregistration.
- Fixed-executor raw verdicts, RQ3 case records, property generator and certificates, and in-toto inspection sources are supplied rather than hidden behind summary claims.
- New tools check packaging and recorded arithmetic; no new scientific outcome is claimed.
- No hosted-model calls, target campaigns, mutation evaluations, in-toto comparisons, or attack-program replays ran during preparation of this package.
- The public reduced repository is not silently replaced. External access, anonymity, licensing/distribution decisions and a hosted versioned link remain separate from local staging.
