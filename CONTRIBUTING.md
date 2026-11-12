# Working with this bundle

How to verify, re-run, and extend the evidence in this repository.

## 1. Verify first (no execution)

```sh
cd reviewer_bundle
python3 -B offline_checks.py verify     # SHA-256 over all 24,023 payloads
python3 -B offline_checks.py census     # the frozen verdict rows, read-only
```

Expected: `integrity: PASS`, 0 errors. Nothing executes; nothing contacts a provider.

## 2. Check a specific number

Every cohort directory in [`experiments/`](experiments/INDEX.md) carries its registration, per-session `results.jsonl` rows, and analyzer outputs. The worked example re-derives the 96/0 paired contrast in ten lines of stdlib Python — see [Verifying results](https://0xlab-art.github.io/YHZ-Floor/verifying/).

## 3. Run an experiment yourself

Each cohort is a frozen protocol: preregistration → `FREEZE.json` → runner → append-only `results.jsonl` → analyzer → evidence gate. The M1 audit is the worked example end-to-end (60 slots, amendments 1–16, the censoring finding):

```sh
cd experiments/external_published_audit_20261110/
export AGENTROUTER_API_KEY="sk-your-own-key"    # environment only — never in files
python3 run_published_audit_sessions.py
```

Gateway behaviour, key handling, budget discipline, and halt rules: [Setup & API](https://0xlab-art.github.io/YHZ-Floor/setup_and_api/).

## 4. Extend

- New cohort: write the preregistration, freeze the inputs, clone a runner, record amendments before they run.
- New gateway: probe the label unregistered first; register it in `_REGISTRATION.json`; substitute labels are disclosed per-label, never pooled.
- Keep the discipline: append-only results, per-call attestation, no pooled statistics.

The full rendered guide lives at **https://0xlab-art.github.io/YHZ-Floor/** — start with [the audit model](https://0xlab-art.github.io/YHZ-Floor/guide/).
