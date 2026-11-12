# Contribution audit — 2026-10-21

User authorized all four proposed analyses and five subagents, then explicitly
selected GPT-6-Luna with medium reasoning. Root orchestrates, verifies and
synthesizes. At most three child agents run concurrently; five agents total run in
two waves.

Ownership:
- policy_mechanism/: admission mechanisms, conservative unused-import interventions, fresh derivative execution.
- paired_effects/: paired policy-by-representation contrasts and uncertainty.
- attribution_evidence/: raw attribution corpora, ablations, population/claim reconstruction.
- abc_prior/: full-text ABC comparison and exact incremental-claim assessment.
- agentsuite_prior/: full-text AgentSuite comparison and exact incremental-claim assessment.
- Root: this ledger, input freeze, independent verification, consolidated claim/evidence/prior-art matrix and synthesis.

No agent edits the manuscript, raw/frozen records, protected locks or other agents' files. All new numerical analyses are exploratory. No hosted experiment calls or new model-generation cohorts. Negative results and unresolved cases remain visible. Representation arms are not model comparisons; replay adds no independent model session.

The requested generic worker role was rejected by the role-routing hook. Registered lazycodex-worker-medium profiles with explicit user-authorized model/reasoning overrides were accepted. No approval or hook was bypassed.

Wave 1: policy_mechanism, paired_effects, attribution_evidence.
Wave 2: abc_prior, agentsuite_prior.

## Completion ledger

**Models actually used.** The author first selected GPT-6-Luna, then re-specified
the run to use the free route `minimax/minimax-m3.1-flash:free`. Wave 2 was run on
that route. The first wave-2 spawn on `gpt-6-luna` was stopped within a minute of
spawning and before it wrote any file; both wave-2 agents were then spawned on the
free route and completed there. Recorded so the release provenance is exact.

| Component | Status | Key output |
|---|---|---|
| policy_mechanism | **complete** | `REPORT.md`, `.omo/evidence/run01/{FULL_CENSUS,CASE_LEDGER,VALIDATION}.json` |
| paired_effects | **complete** | `REPORT.md`, `results.json`, `contrasts.csv`, `preregistered_L3_reproduction.json` |
| attribution_evidence | **complete** | `REPORT.md`, `recomputed_summary.json`, `claim_ledger.json`, `supplementary_census.json` |
| abc_prior | **complete** | `abc_prior/REPORT.md`, `abc_prior/claim_comparison.json` |
| agentsuite_prior | **complete** | `agentsuite_prior/REPORT.md`, `agentsuite_prior/claim_comparison.json` |
| Root verification | **complete** | `root_verify.py` — 43/43 independent checks |
| Root synthesis | **complete** | `SYNTHESIS_MATRIX.{md,json}`, `CENTRAL_CLAIM.md`, `VALIDATION_STUDY.md`, `AUDIT_REPORT.md` |

**`policy_mechanism` was resumed, not restarted.** Its scripts and a partial run
existed from wave 1; the finalizer had never run. `finalize.py` was executed and
validated: PASS, 852 rows, 128 derivatives, 15 tests, 7,670 input files unchanged.

**Root verification is independent.** `root_verify.py` does not import any worker's
analysis code. It re-derives the headline numbers from the frozen H1-R3 records
and the attribution corpora and compares them against the worker artifacts.

**Manuscript untouched.** `verify_freeze.py` re-checked all 26,181 frozen inputs
after the run: PASS, nothing changed. No `.tex` file in the manuscript tree was
modified inside the audit window.

## Verdict in one line

The contribution is a **domain-specific instantiation with a new measurement
instrument (byte-fixed admission counterfactual) and a new evidence contract
(claim-specific attribution), not a new general principle** — ABC owns the
validity taxonomy and the "flaws distort performance" finding with a security
case study; AgentSuite owns the component-wise decomposition and the large-scale
version of the same finding.