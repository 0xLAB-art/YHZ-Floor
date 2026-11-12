<div align="center">

<img src="assets/owners_3d.svg" width="860" alt="The five owners of a reported attack success — animated isometric decomposition with the YHZ floor"/>

# The Five-Owner Audit — YHZ-Floor

**A pre-registered, hash-frozen ownership audit of AI-agent attack success**

[![venue](https://img.shields.io/badge/venue-IEEE%20S%26P%202027%20Cycle%202-blue)](#)
[![status](https://img.shields.io/badge/status-double--blind%20review-orange)](#)
[![pre-registration](https://img.shields.io/badge/preregistration-all%20cohorts%20hash--frozen-8a63d2)](#)
[![evidence gate](https://img.shields.io/badge/evidence%20gate-194%2F194%20checks-2ea043)](#)
[![bundle](https://img.shields.io/badge/evidence%20bundle-24%2C023%20files%20verified%20%7C%200%20identity%20hits-2ea043)](#)
[![release](https://img.shields.io/badge/release-v1.0.0--codes--results-blue)](../../releases/tag/v1.0.0-codes-results)

[**📖 README**](#the-five-owner-audit--yhz-floor) &nbsp;·&nbsp;
[**📗 Guide**](GUIDE.md) &nbsp;·&nbsp;
[**🧠 Explanation**](EXPLANATION.md) &nbsp;·&nbsp;
[**🧪 Experiments & results**](experiments/INDEX.md) &nbsp;·&nbsp;
[**🤝 Contributing**](CONTRIBUTING.md) &nbsp;·&nbsp;
[**🛡️ Security**](SECURITY.md) &nbsp;·&nbsp;
[**🌐 Rendered docs**](https://0xlab-art.github.io/YHZ-Floor/) &nbsp;·&nbsp;
[**📦 Release**](../../releases/tag/v1.0.0-codes-results)

</div>

---

## Verify in 10 seconds — no trust required

```sh
cd reviewer_bundle
python3 -B offline_checks.py verify
```

```
integrity: PASS  ·  24,023 payloads  ·  0 errors
```

Every file's SHA-256 checked against the manifest. Nothing executes, nothing contacts a provider. That is the entry point: **every number below traces to rows you can open and recount yourself.**

## What this repository is

A published AI-agent attack-success rate is an output of the **evaluation contract** that produced it — the evaluator's rule, the prompt's disclosures, the session wrapper, the token allowance, and the evidence that ties a verdict to an execution. The paper measures **how much each owner moves the number** through hash-frozen interventions on matched cryptographic tasks:

- **33 registered cohorts** · **3,562 retained sessions** · every design pre-specified
- a **60-session published-protocol audit** of a public benchmark, run under its own declared rules
- one append-only `results.jsonl` per cohort — every printed statistic regenerates from those rows by closed-form enumeration

Browse everything: [**experiments/INDEX.md**](experiments/INDEX.md) lists all 81 record directories with their paper sections.

## The results the audit registered

| Owner | Intervention | Registered result | Bound |
|---|---|---|---|
| **Admission** | regrade fixed bytes; cleanup | **−0.8 → −32.8 → +3.9 pp** | trigger executes in 100/101 traces |
| **Information contract** | 2×2 prompt slots | **paired one-way in all 16 family members** (96/0; Holm 4.0×10⁻²⁸) | RC4 + ECDSA nulls; AES-GCM-SIV accepts nothing |
| **Session wrapper** | interactive vs one-shot | **0/32 each direction** at the powered size | advantage ≤ 10.7% (Wilson 95%) |
| **Compute allowance** | declared vs raised | **20/50 → 28/50** (8/10 task-level) | 17 slots transport-unmeasured |
| **Execution evidence** | attribution ablations | **0/44 combined** (16/44, 28/44 alone) | constructed-case outcomes, not deployment rates |

The two findings a reviewer should read first:

<details open>
<summary><b>1 — the 16-member family: every paired contrast is one-way</b></summary>
<br/>

Withhold the zero-reference premise and no withheld seed ever beats its stated counterpart — across every cohort, label, and replication. The one borderline (P010P 5/0) prints as its own bound, never absorbed. The negative controls bracket the claim: RC4 4/4, ECDSA 32/32 withheld, AES-GCM-SIV accepting nothing in any cell.

<img src="assets/discordance_family.svg" width="860" alt="The 16 Holm-family cohorts, animated"/>

</details>

<details open>
<summary><b>2 — the allowance censors the number</b></summary>
<br/>

A published benchmark protocol declares a 12,000-token allowance. Re-running that protocol on its own frozen inputs: **30 of 60 sessions never act** — every turn spent in hidden reasoning, zero submissions. Six of ten task-level pairs are *unmeasured, not failed*. Raising the allowance (32k, then 64k — each change a numbered amendment recorded before it ran) recovers them: 28/50, 8/10 pairs, identical under all five evaluator rules.

**A published rate is only as strong as the allowance it was measured under.**

<img src="assets/allowance_censoring.svg" width="860" alt="The censoring-to-recovery slot grid, animated"/>

</details>

## The evidence, in one map

| You want to… | Go to |
|---|---|
| check a specific number | [experiments/INDEX.md](experiments/INDEX.md) → the cohort's `results.jsonl` |
| see the audit model explained | [EXPLANATION.md](EXPLANATION.md) — the estimand, the censoring, reading the ledger |
| run a cohort yourself | [docs/RUNNING_EXPERIMENTS.md](docs/RUNNING_EXPERIMENTS.md) — the M1 audit end-to-end |
| plug in your own API key | [docs/SETUP_AND_API.md](docs/SETUP_AND_API.md) — environment-only keys, gateway behaviour |
| re-derive the printed statistics | [docs/VERIFYING.md](docs/VERIFYING.md) — three verification layers, stdlib only |
| execute the retained programs | [reviewer_bundle/review.py](reviewer_bundle/) — sandboxed replay (optional) |
| read it as a rendered site | [0xlab-art.github.io/YHZ-Floor](https://0xlab-art.github.io/YHZ-Floor/) — search + diagrams |

## Repository layout

```
YHZ-Floor/
├── experiments/         ← all 81 record directories, browsable (+ INDEX.md)
│     registration · per-session results.jsonl · analyses · censuses · sweeps
├── analysis/            ← the E2/E5/RQ4 trees, evaluators, the H1-R3 replay validation
├── reviewer_bundle/     ← the curated offline projection (24,023 manifest files)
│     offline_checks.py · MANIFEST.json · COPY_LINEAGE.json · ANONYMITY_SCOPE.json
│     h1r3/ (852 sessions + sandboxed replay) · source/sp2027/ (the cited wave trees)
├── GUIDE.md + docs/     ← the guide: setup, running, verifying (mermaid + worked examples)
├── EXPLANATION.md       ← how to read the audit: estimand, censoring, ledger
└── assets/              ← animated SVG figures (+ gen_animations.py)
```

## Provenance

- **Byte-preserving packaging** — `COPY_LINEAGE.json` records source→destination SHA-256 for every payload; no trial was added or removed.
- **Identity hygiene** — a campaign-wide scan returns 0 hits for names, emails, affiliations, and handles; frozen records keep a bare mount prefix (`/mnt/nvme5/...`), which is a filesystem location, not an identity.
- **No rerun during packaging** — no attack program, mutation test, or provider call was executed; the component-level prior validation is bound to its exact archive.
- **The manuscript is not here** — during double-blind review it travels through the venue's submission system only.

## The five preconditions (the YHZ floor)

The audit distills into five preconditions any future measurement can adopt — the full checklist with per-condition evidence is Table 9 of the paper:

1. **Strip** the task — every reported number carries its stripped twin on shared seeds.
2. **Declare** the acceptance rule — frozen before the first call, measured under every admissible coding.
3. **Never pool** distinct groups — every substitution disclosed with its boundary row.
4. **Publish** the raw outputs — claims attach to frozen per-seed rows, not summaries.
5. **Bind** the claim to its negatives — registered nulls stated as the claim's boundary.

A benchmark that skips these reproduces the failure modes this audit measured.

---

<details>
<summary>Retained-programs notice</summary>

Retained records are provided for review purposes. Retained attack programs target local, self-contained fixtures — containers with reserved secrets and a same-host oracle, no reachable production target. Execute them only inside the provided sandboxed replay or equivalent isolation. During double-blind review the authors remain anonymous; correspondence flows through the venue.

</details>
