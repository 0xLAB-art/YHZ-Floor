# PREREGISTRATION — P016: within-route cross-label replication on the AES-GCM fixture

**Namespace:** `sp2027/research_execution/info_contract_aesgcm_labels_20261102/`
**Date:** 2026-11-02 · Written before any experiment call under this protocol.
**Status:** registered; runner SHA-256 in `_REGISTRATION.json`, asserted at launch.

## 1. What changed, and why this cohort exists

P015 (cross-**provider** replication) was cancelled with zero sessions because
no funded second provider route exists here: APINEX returns 402, APMix gates
every model behind a plan this key lacks, and the OpenRouter catalog is
unusable (`info_contract_aesgcm_apinex_20261102/CANCELLED.md`).

The only working route serves three labels. So the transfer question is asked in
the strongest form the environment can actually support:

> On the frozen AES-GCM fixture, does the premise effect reproduce on model
> labels **other than** the one P014 used, holding the transport, the key and
> the adapter fixed?

This is a **within-route, cross-label** replication. It is explicitly *not* a
provider-generalization test, and no claim of provider generality may be built
on it.

## 2. Labels

From the measured inventory (`research_execution/labels_probe_20261102.json`,
AgentRouter: `gpt-5.6-sol`, `gpt-6-astra`, `gpt-6.1-sol`), excluding the label
P014 already runs (`gpt-6-astra`):

| label | status |
|---|---|
| `gpt-6.1-sol` | registered |
| `gpt-5.6-sol` | registered |

One label per process, one directory per label, one results file per label. No
label shares a seed set, a results file or an analysis with another.

## 3. Design (frozen, identical to P014 except labels and seeds)

- **Runner:** `run_info_contract_2x2_aesgcm.py`, byte-identical to P014's
  (SHA asserted against `_REGISTRATION.json`). Fixture, cells, slots, oracle,
  policy, sandbox, event log, summary schema untouched.
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−).
- **Seeds:** 601–616 per label — fresh, disjoint from 41–44, 81–84, 101–118,
  121–136, 141–156, 161–176, 181–196, 201–208, 211–218, 221–228, 301–332,
  401–416 (P014) and 501–516 (P015, unused).
- **Sessions:** 4 cells × 16 seeds = 64 per label, **128** total; ≤2 turns; one
  provider call per turn; max_tokens=1400 requested.
- **Transport:** `provider_adapter_agentrouter.py`, unchanged from P014 —
  Anthropic `/v1/messages`, `claude-cli` UA, token floor 2800 recorded per call
  as `max_tokens_sent`, timeout 600 s.
- **Scheduling:** labels run **sequentially**, and only after the P014 process
  exits, so no two cohorts share a key concurrently. Concurrency on one key is
  itself a failure channel (429 → terminal provider failure) and would leak into
  the cell denominators.
- **Provider failures are terminal per session** — never retried, never
  imputed; consecutive provider failures halt that label's launch.

## 4. Analysis plan (frozen before any call)

Per label, reported separately, never pooled with P014 or each other:

- **Primary:** paired C1-vs-C4 discordance on shared seeds, exact binomial
  two-sided, with the full discordance count and the **evaluable-pair**
  denominator, not the registered one.
- **Secondary (descriptive, prespecified):** per-cell acceptance with
  submissions/turns; premise marginal (C1+C3 vs C2+C3) and naming marginal
  (C1+C4 vs C2+C3), Fisher exact one- and two-sided; provider-dropout counts by
  cell, disclosed as a denominator effect.
- **Replication statement:** each label classified in advance as
  **direction replicated** (C1 ≥ 12/16 and C2 ≤ 4/16), **direction not
  replicated**, or **instrument-difficulty** (C1 < 12/16). Classification is by
  these thresholds only; no p-value is invented across labels, and the three
  AgentRouter labels are shown as a descriptive table of direction, never as a
  pooled rate.

**Falsifiers (prespecified):**
- **F1 stated-arm ceiling:** C1 < 12/16 ⇒ instrument-difficulty result for that
  label, not a premise result.
- **F2 naming gates:** C3 materially below C1 ⇒ naming still does work.
- **F3 derive frame:** C2 near C1 ⇒ success without the premise; on a
  hidden-premise fixture that is a real negative, reported as one.
- **F4 label divergence:** if labels disagree in direction, the within-route
  replication claim is withdrawn and the divergence is the finding.

## 5. Discipline

Cost expectation ≤ $2 for 128 sessions (P014's 64-session cohort on this route
is running at ≈ $0.40). Every call appended to
`sp2027/research_execution/BUDGET_LEDGER.jsonl`. Leak scan over every prompt
file before analysis: the per-seed secret and the record content may appear in
zero prompts other than the premise sentence of the stated arms. No mid-cohort
design change; a protocol change during the run forces a new protocol number.
