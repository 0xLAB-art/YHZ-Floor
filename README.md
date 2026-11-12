<div align="center">

<img src="assets/owners_3d.svg" width="820" alt="Five isometric pillars — the five owners of a published attack-success rate, with the YHZ floor beneath them"/>

# YHZ-Floor

**The complete, verifiable evidence bundle for a pre-registered, hash-frozen,
five-owner audit of AI-agent attack success.**

[![pre-registration](https://img.shields.io/badge/preregistration-all%20cohorts%20hash--frozen-8a63d2)](docs/RUNNING_EXPERIMENTS.md)
[![integrity](https://img.shields.io/badge/integrity-24%2C023%20payloads%20verified%20%C2%B7%200%20errors-2ea043)](#verify-before-you-read--10-seconds-no-trust-required)
[![release](https://img.shields.io/badge/release-v1.0.0--codes--results-blue)](../../releases/tag/v1.0.0-codes-results)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![docs](https://img.shields.io/badge/docs-rendered%20site-0969da)](https://0xlab-art.github.io/YHZ-Floor/)

[Guide](GUIDE.md) &nbsp;·&nbsp; [Explanation](EXPLANATION.md) &nbsp;·&nbsp; [Experiments index](experiments/INDEX.md) &nbsp;·&nbsp; [Rendered docs](https://0xlab-art.github.io/YHZ-Floor/) &nbsp;·&nbsp; [Contributing](CONTRIBUTING.md) &nbsp;·&nbsp; [Security](SECURITY.md) &nbsp;·&nbsp; [Cite](CITATION.cff)

</div>

## What this is

A published AI-agent attack-success rate is not a property of the model. It is the output of a **measurement contract** with five identifiable owners: the evaluator's acceptance rule, the task prompt's information contract, the session wrapper, the compute allowance, and the evidence binding a verdict to an execution.

This repository freezes that contract and moves **one owner at a time** on matched cryptographic tasks — then serves every frozen row the numbers were measured on:

- **33 registered cohorts · 3,562 retained sessions** — every design pre-specified before the first model call
- a **separate 60-session published-protocol audit** of a public benchmark, run under its own declared rules
- one append-only `results.jsonl` per cohort — every printed statistic regenerates from those rows by closed-form enumeration, standard library only

## Verify before you read — 10 seconds, no trust required

```sh
cd reviewer_bundle
python3 -B offline_checks.py verify
```

```
integrity: PASS  ·  24,023 payloads  ·  0 errors
```

Every payload's SHA-256 is checked against `MANIFEST.json`. Nothing executes, nothing contacts a provider. That is the entry point: **every number below traces to rows you can open and recount yourself.** [docs/VERIFYING.md](docs/VERIFYING.md) re-derives the headline contrast in ten lines of standard-library Python.

## The five owners, and what moving each one did

> **How to read the table.** *pp* = percentage points. *a/b* = a paired discordance on shared seeds: *a* sessions succeeded with the owner moved, *b* with it held. *Holm* = family-wise correction across the 16 registered contrasts. *Wilson* = 95% confidence upper bound.

| Owner | Question it answers | Registered result | Bound that stays attached |
|---|---|---|---|
| **Admission** | does the evaluator's rule change the verdict on the *same* programs? | regrade of fixed bytes: −0.8 → −32.8 → +3.9 pp | trigger executes in 100/101 retained traces |
| **Information contract** | which prompt disclosure decides the outcome? | 2×2 over the zero-reference premise — paired one-way in all 16 registered contrasts (96/0, Holm 4.0×10⁻²⁸) | RC4 4/4 · ECDSA 32/32 withheld · AES-GCM-SIV accepts nothing in any cell |
| **Session wrapper** | does an interactive loop help? | interactive vs one-shot: 0/32 each direction at the powered size | advantage ≤ 10.7% (Wilson 95%) |
| **Compute allowance** | how much of the number is the token budget? | declared 12,000 vs raised: 20/50 → 28/50, 8/10 task-level pairs | 17 slots transport-unmeasured |
| **Execution evidence** | does the record *prove* the claimed execution? | attribution ablations: 0/44 combined (16/44, 28/44 alone) | constructed cases, not deployment rates |

### Finding 1 — the information contract dominates

Withhold the zero-reference premise and **no withheld seed ever beats its stated counterpart** — across every cohort, model label, and replication. The one borderline cohort prints as its own bound instead of being absorbed into the family. The negative controls bracket the claim from both sides: the honest-null cipher, the second fixture family, and the registered AES-GCM-SIV control that accepts nothing in any cell.

### Finding 2 — the allowance censors the number

Re-running a published benchmark protocol on its own frozen inputs, at that protocol's declared 12,000-token allowance: **30 of 60 sessions never act** — every turn spent in hidden reasoning, zero submissions. Six of ten task-level pairs are *unmeasured, not failed*. Raising the allowance (32k, then 64k — each change a numbered amendment recorded before it ran) recovers them: 28/50, 8/10 pairs, identical under all five evaluator rules.

**A published rate is only as strong as the allowance it was measured under.**

## Explore

| You want to… | Go to |
|---|---|
| check a specific number | [experiments/INDEX.md](experiments/INDEX.md) → the cohort's `results.jsonl` |
| understand the audit model | [EXPLANATION.md](EXPLANATION.md) — the estimand, the censoring, reading the ledger |
| run a cohort yourself | [docs/RUNNING_EXPERIMENTS.md](docs/RUNNING_EXPERIMENTS.md) — the M1 audit end-to-end |
| plug in your own API key | [docs/SETUP_AND_API.md](docs/SETUP_AND_API.md) — environment-only keys, gateway behaviour |
| re-derive the printed statistics | [docs/VERIFYING.md](docs/VERIFYING.md) — three verification layers |
| execute the retained programs | `reviewer_bundle/h1r3/h1r3_complete_replay_v1/execute_replay.py` — sandboxed; see [SECURITY.md](SECURITY.md) |
| read it as a rendered site | [0xlab-art.github.io/YHZ-Floor](https://0xlab-art.github.io/YHZ-Floor/) |
| cite this artifact | [CITATION.cff](CITATION.cff) |

## Repository layout

```
YHZ-Floor/
├── experiments/         ← 80 record directories + INDEX.md (registrations, per-session
│                           results.jsonl, analyses, sweeps, the cost ledger)
├── analysis/            ← the campaign's working trees: E2/E5/RQ4, evaluators,
│                           the H1-R3 replay validation (see analysis/README.md)
├── reviewer_bundle/     ← the curated offline projection (24,023 manifest payloads)
│                           offline_checks.py · MANIFEST.json · COPY_LINEAGE.json ·
│                           ANONYMITY_SCOPE.json · h1r3/ (852 sessions + sandboxed
│                           replay) · source/sp2027/ (the cited wave trees)
├── GUIDE.md + docs/     ← the guide: setup, running, verifying (mermaid + examples)
├── EXPLANATION.md       ← how to read the audit
├── tools/               ← regenerates INDEX.md and the asset figures
└── assets/              ← the animated SVG figures (+ gen_animations.py)
```

## The three counts, reconciled

- **80 record directories** serve here — registered cohorts, diagnostics, controls, and superseded first passes, every one listed in [experiments/INDEX.md](experiments/INDEX.md).
- **33 registered cohorts · 3,562 retained sessions** — the pre-specified session inventory; populations are never pooled.
- **60 sessions** — the M1 published-protocol audit, a separate population by design.
- **24,023 payloads** — the curated `reviewer_bundle` projection checked by `offline_checks.py`; the [release bundle](../../releases/tag/v1.0.0-codes-results) ships its own 70,337-entry SHA-256 manifest over the full codes+results tree.

## Provenance & scope

- **Byte-preserving packaging** — `COPY_LINEAGE.json` records source→destination SHA-256 for every payload; no trial was added or removed.
- **No rerun during packaging** — no attack program, mutation test, or provider call was executed while preparing the bundle; the component-level validation is bound to its exact archive.
- **Identity hygiene** — a campaign-wide direct-identifier scan returns 0 hits (`reviewer_bundle/ANONYMITY_SCOPE.json`); frozen records keep a bare mount prefix, which is a filesystem location, not an identity.
- **The manuscript is not here** — during double-blind review it travels through the venue's submission system only; the `§` markers in the index point at it.
- **Not in the bundle** — raw per-turn provider responses remain with the authors and are shareable on request; the per-slot rows and summaries carry every recorded outcome.

---

<details>
<summary>Retained-programs notice</summary>

Retained records are provided for review purposes. Retained attack programs target local, self-contained fixtures — containers with reserved secrets and a same-host reference oracle, no reachable production target. Execute them only inside the provided sandboxed replay (`reviewer_bundle/h1r3/h1r3_complete_replay_v1/`) or your own equivalent isolation. See [SECURITY.md](SECURITY.md).

</details>
