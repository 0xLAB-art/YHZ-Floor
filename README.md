<div align="center">

<img src="assets/owners_3d.svg" width="860" alt="The five owners of a reported attack success — animated isometric decomposition"/>

### The Five-Owner Audit — YHZ-Floor

**A pre-registered, hash-frozen ownership audit of AI-agent attack success**

[![venue](https://img.shields.io/badge/venue-IEEE%20S%26P%202027%20Cycle%202-blue)](#)
[![status](https://img.shields.io/badge/status-double--blind%20review-orange)](#)
[![pre-registration](https://img.shields.io/badge/preregistration-all%20cohorts%20hash--frozen-8a63d2)](#)
[![evidence gate](https://img.shields.io/badge/evidence%20gate-194%2F194%20checks-2ea043)](#)
[![bundle](https://img.shields.io/badge/evidence%20bundle-24%2C023%20files%20verified%20%7C%200%20identity%20hits-2ea043)](#)
[![release](https://img.shields.io/badge/release-v1.0.0--codes--results-blue)](../../releases/tag/v1.0.0-codes-results)

📖 **[The rendered Guide](https://0xlab-art.github.io/YHZ-Floor/)** &nbsp;·&nbsp;
🗂️ **[Experiments index](experiments/INDEX.md)** &nbsp;·&nbsp;
📦 **[Release: codes + results](../../releases/tag/v1.0.0-codes-results)** &nbsp;·&nbsp;
🔍 **[Verify the bundle](#quick-start)**

</div>

---

## Quick start

A few options to get into the evidence, no trust required:

```sh
# 1. verify the curated bundle (24,023 payloads, no execution)
cd reviewer_bundle
python3 -B offline_checks.py verify        # → integrity: PASS, 0 errors

# 2. download the full codes+results record (107 MB)
#    Releases → v1.0.0-codes-results, then:
sha256sum -c MANIFEST_CODES_RESULTS.sha256 # 117,330 files
tar xzf codes_results.tar.gz
```

## Why this exists

A reported AI-agent attack-success number is a property of the **evaluation contract** that produced it — not an intrinsic property of the agent. This repository is the complete verifiable record of an audit that measures the share of each owner through **hash-frozen, one-owner-at-a-time interventions** on matched cryptographic tasks: 33 registered cohorts, 3,562 retained sessions, plus a 60-session published-protocol audit — every design pre-specified, every number frozen before the first call.

## The registered 16-member family

Every information-contract cohort's paired contrast is **one-way**: no withheld seed ever beats its stated counterpart.

<img src="assets/discordance_family.svg" width="860" alt="Animated bars: the 16 Holm-family cohorts, every paired contrast one-way"/>

## The allowance owns part of the number

The external audit's headline finding: a published protocol's *declared 12,000-token allowance* censors 30 of 60 sessions into unshown reasoning — **six of ten task-level pairs are unmeasured, not failed**. Raising the allowance recovers the ceiling-censored slots under all five evaluator rules. **A published rate is only as strong as the allowance it was measured under.**

<img src="assets/allowance_censoring.svg" width="860" alt="Animated slot grid: 20/50 solved at the declared allowance rising to 28/50 after the 32k/64k amendments"/>

## The ownership ledger

| Owner | Intervention | Registered result | Bound |
|---|---|---|---|
| **Admission** | regrade fixed bytes; cleanup | $-0.8 \to -32.8 \to +3.9$ pp | trigger executes in 100/101 traces |
| **Information contract** | $2{\times}2$ prompt slots | paired one-way in all 16 family members (96/0, Holm $4.04{\times}10^{-28}$) | RC4 + ECDSA nulls; AES-GCM-SIV accepts nothing |
| **Session wrapper** | interactive vs one-shot | powered 32-pair null: 0/32 each direction | advantage $\le 10.7\%$ (Wilson 95%) |
| **Compute allowance** | declared vs raised | 20/50 $\to$ 28/50 (8/10 task-level) | 17 slots transport-unmeasured |
| **Execution evidence** | attribution ablations | combination 0/44 (16/44, 28/44 alone) | constructed-case outcomes, not deployment rates |

## Documentation

| | |
|---|---|
| 📗 [The Guide](GUIDE.md) | the audit model, the lifecycle, where every number lives |
| ⚙️ [Setup & API](docs/SETUP_AND_API.md) | environment-only keys, gateway behaviour (measured), budget discipline |
| 🧪 [Running experiments](docs/RUNNING_EXPERIMENTS.md) | the M1 audit end-to-end, one recorded slot anatomy |
| 🔍 [Verifying results](docs/VERIFYING.md) | three verification layers + a worked regeneration example |
| 🗺️ [Repository map](docs/REPO_MAP.md) | every directory, what it carries, where the paper cites it |
| 🌐 [Rendered site](https://0xlab-art.github.io/YHZ-Floor/) | the same guide as a browsable site with search |

## Repository layout

```
YHZ-Floor/
├── README.md                        ← this file
├── GUIDE.md + docs/                 ← the reviewer guide (mermaid diagrams, worked examples)
├── assets/                          ← animated SVG figures (CSS/SMIL — no scripts at render time)
│   └── gen_animations.py            ← the generator
├── experiments/                     ← all 60+ registered cohorts, browsable + INDEX.md
│   └── (registration, per-session results.jsonl, analyses, censuses per cohort)
├── analysis/                        ← the E2/E5/RQ4 trees, evaluators, the H1-R3 replay validation
└── reviewer_bundle/                 ← the curated offline projection (24,023 manifest files)
    ├── offline_checks.py            ← the no-execution verifier
    ├── MANIFEST.json                ← SHA-256 per file
    ├── COPY_LINEAGE.json            ← byte-preserving payload hashes
    ├── ANONYMITY_SCOPE.json         ← direct-identifier scan (0 hits)
    ├── review.py                    ← optional reviewer re-execution entry points
    ├── h1r3/                        ← 852 sessions + sandboxed replay
    └── source/sp2027/               ← the wave trees the main text cites
```

## Provenance and anonymity

- **Byte-preserving packaging**: `COPY_LINEAGE.json` records source→destination SHA-256 for every copied payload; no trial was added or removed.
- **Anonymity**: the direct-identifier scan across the whole tree returns **0 hits** (author names, emails, affiliations, handles); frozen records retain a bare mount prefix (`/mnt/nvme5/...`) — a filesystem location, not an identity.
- **No rerun during packaging**: no attack program, mutation test, or provider call was executed while preparing this bundle.
- **The manuscript is not here**: during double-blind review it travels through the venue's submission system only.

## The five preconditions (the YHZ floor)

1. **Strip** the task, mandatorily — every reported number carries its stripped twin on shared seeds.
2. **Declare** the acceptance rule, then test it — frozen before the first call, measured under every admissible coding.
3. **Never pool** distinct groups — every substitution disclosed with its boundary row.
4. **Publish** the raw outputs — claims attach to frozen per-seed rows and receipted censuses.
5. **Bind** the claim to its negatives — registered nulls stated as the claim's boundary.

A benchmark that skips these reproduces the failure modes this audit measured. The full checklist is Table 9 of the paper.

---

*Retained records are provided for review purposes; retained attack programs target local, self-contained fixtures with no reachable production target. During double-blind review the authors remain anonymous; correspondence flows through the venue.*
