# 🧠 Explanation — how to read this audit

The deep explanation behind the paper's design: what each owner means, why the interventions look the way they do, and how to read the numbers.

## 1. The claim in one sentence

A published attack-success number is the output of a **contract**, not a property of the model — and the paper measures the share of each contract owner by freezing everything and moving one owner at a time.

## 2. The five owners, concretely

| Owner | The question it answers | The intervention | What "moving it" means |
|---|---|---|---|
| **Admission** | does the evaluator's rule change the verdict on the *same* programs? | regrade the frozen outputs under a different rule | programs and outcomes stay byte-identical; only the acceptance rule moves |
| **Information contract** | which prompt disclosure decides the outcome? | a 2×2 over the zero-reference premise and the oracle channel | the task is identical; the sentence is stated or withheld |
| **Session wrapper** | does an interactive loop help? | interactive vs one-shot, same fixture | same model, same budget, different turn structure |
| **Compute allowance** | how much of the number is the token budget? | re-run the published protocol at a declared vs raised allowance | same inputs; only `max_output_tokens` moves |
| **Execution evidence** | does the retained record *prove* the claimed execution? | attribution ablations (joins-only vs signatures-only vs both) | the claim is tested against its own evidence chain |

## 3. Why paired contrasts, never pooled rates

The estimand is

> Δ = P(accept | slot varied) − P(accept | slot held),

computed **per cohort on shared seeds** and reported as an exact-binomial discordance with its interval. Three reasons:

1. **No exchangeability across cohorts**: each cohort has its own label, fixture, floor, and allowance — a pooled rate would average incomparable populations.
2. **The null is part of the answer**: RC4 4/4, ECDSA 32/32 withheld, and GCM-SIV accepting nothing in any cell are registered *nulls* that bracket the collapse — they are claims, not caveats.
3. **Multiplicity is honest**: the 16-member family carries a Holm step-down at FWER 0.05, and the one borderline (P010P 5/0) prints as its own bound instead of being absorbed.

## 4. The censoring finding, in plain terms

The M1 audit re-ran a published protocol on its own frozen inputs. At the protocol's **declared 12,000-token allowance**, 30 of 60 sessions produced *no visible action at all*: every turn spent the entire budget in hidden reasoning, zero submissions. Six of ten task-level pairs were therefore **unmeasured, not failed**. Raising the allowance (32k, then 64k — each change a numbered amendment recorded before it ran) recovered the censored slots: the scored set closed at 28/50 and 8/10 task-level pairs, identical under all five evaluator rules.

**The lesson generalizes**: any published rate is a function of the allowance it was measured at. A rate that does not state its allowance has not stated its own meaning.

## 5. Reading the ownership ledger

Table 4 of the paper (and the README hero) gives one row per owner: the intervention, the registered result, and the **bound** — the null or limit that stays attached to that row. The Bound column is the paper's honesty mechanism: every claim carries its own boundary in the same cell.

## 6. What the external record does — and refuses to do

The external cohorts mount **published benchmarks' own graders** on frozen outputs and register where the instrument travels and where it stops. Each stop is named by its owner (transport, answer normalization, admission interface, benchmark domain, capability floor). No third-party published number is regraded end-to-end — those releases ship no records to regrade — and no benchmark-quality claim is made about any audited system.

## 7. The transfer rule

The design travels to any domain with a **binarizable oracle verdict** and a **load-bearing task premise**. The first out-of-domain witness (a non-crypto audit-forensics task) reproduced the premise effect 8/8 vs 0/8 (Fisher 7.8e-5) — a first witness, not a universal claim; broader coverage is registered-open.

## 8. Further reading

- The paper itself (delivered through the venue during review)
- [The Guide](GUIDE.md) — running and verifying
- [The experiments index](experiments/INDEX.md) — every cohort, its registration, and its rows
- [The rendered documentation](https://0xlab-art.github.io/YHZ-Floor/) — diagrams and search
