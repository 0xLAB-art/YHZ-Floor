# HEB-1 Evaluation Report — Cross-Boundary Verdict Promotion

**Date:** 2026-10-19 · **Status:** evaluation complete (dev + single held-out pass) ·
**Scope:** offline, frozen-byte experimental evaluation of the HEB-1 hypothesis ·
**Spend:** $0 marginal; 0 model/provider calls; no network.

## 1. Question tested

Does cross-boundary composition of evaluation evidence produce a reproducible,
security-relevant false-attribution mechanism: schema/hash-integrity systems
promote composed bundles to the full requested claim strength (attribution),
while claim-binding systems reject them — with cryptographic correctness,
execution identity, target effect, and attribution kept separate throughout?

Assessment basis: `HEB1_PRIOR_ART_ASSESSMENT_20261019.md` (five-element filter,
provisional GO, falsification conditions F1–F4). Protocol authority:
`HEB1_EXPERIMENT_PROTOCOL_20261019.md` (v1 design freeze).

## 2. Procedure executed

1. **Dev suite** (54 cases: coherent B0 8; defect B1–B4b 32; controls C1–C5 14)
   built by `build/heb1_fixtures.py`; adjudicator truth computed by an
   independent re-computation path (`build/heb1_adjudicator.py`, own
   secp256k1/ChaCha20 code; never reads labels).
2. **Design freeze** (`freeze/HEB1_CONFIG_FREEZE.json`,
   `freeze/HEB1_VALIDATOR_FREEZE.json`): sha256 locks on protocol, fixtures,
   common helpers, crypto lib, dev runner, adjudicator, certificate schema,
   and systems V0/V1/V2.
3. **Held-out generation** (`heldout/heb1_heldout_gen.py`, written and run
   *after* the freeze): 64 cases with opaque sha256-derived public ids
   (`hx-…`), reusing the frozen constructors for known families (3+3 per
   primitive) plus **one genuinely new composition pattern B5** (split-half
   session composition) unused during V2 development. No case dropped.
4. **Suite-integrity pre-check** (adjudicator only, systems untouched):
   64/64 cases matched their composition intent, 0 failures — performed
   before the systems pass.
5. **Single recorded evaluation pass** (`heldout/heb1_heldout_runner.py`):
   frozen bytes re-verified against both freeze manifests immediately
   before the pass; three frozen systems + frozen adjudicator invoked as
   blind subprocesses per case; no retuning; all outcomes preserved.
6. Safeguards per protocol §10: protected hashes before/after; label-isolation
   flip test; static audit; forbidden-field and private-path audits over every
   public input; run manifest records 0 model calls / 0 provider calls / no
   network.

## 3. Results

### 3.1 Dev pass (`build/runs/dev_run_20261019_073337/results.json`)

| System | false promotions (defect suite) | B0 true-accept | C1 true-accept |
|---|---|---|---|
| V0 (schema + declared claims) | 32/32 | 8/8 | 4/4 |
| V1 (hash integrity) | 32/32 | 8/8 | 4/4 |
| V2 (claim binding) | 0/32 | 8/8 | 4/4 |

Gates: **N1 PASS** (max FP(V0,V1) = 1.00 ≥ 0.5) · **N2 PASS** (FP(V2) = 0.00
≤ 0.10; B0 8/8; C1 4/4). 0 fixture-validation failures; label isolation
identical; protected hashes ok.

### 3.2 Held-out pass (`heldout/heldout_results.json`)

64 cases; 0 fixture-validation failures; frozen bytes verified; audits clean;
protected hashes ok; isolation identical and labels restored.

| Family (held-out) | n | V0 FP | V1 FP | V2 FP |
|---|---|---|---|---|
| B1 cross-run join | 6 | 6/6 | 6/6 | 0/6 |
| B2 cross-condition join | 6 | 6/6 | 6/6 | 0/6 |
| B3 stale target/instance | 6 | 6/6 | 6/6 | 0/6 |
| B4a missing evidence + strong claims | 6 | 6/6 | 6/6 | 0/6 |
| B4b failed run + strong claims | 6 | 6/6 | 6/6 | 0/6 |
| **B5 split-half session composition (new)** | **6** | **6/6** | **6/6** | **0/6** |
| Defect total | 36 | 36/36 | 36/36 | 0/36 |

Controls: B0 8/8, C1 4/4 true-accept for all three systems; C2/C5 rejected by
V2 while V0/V1 emit at their declared lower levels; C3 malformed rejected by
all; C4 rejected by V2 (V0/V1 emit-6 — the designed lure). Any-positive-above-
truth: V0/V1 40, V2 0. Errors 0. V2 stated-vs-adjudicated level agreement:
38/38 (all rejection reasons carrying `supported=`).

Gates: **N3 mechanism PASS** (max FP(V0,V1) = 1.00 ≥ 0.5) ·
**N3 mitigation PASS** (FP(V2) = 0.00 ≤ 0.15).

### 3.3 Mechanism illustration (B5, new pattern)

Two real runs produced the same valid candidate bytes: run X (failed outcome:
effect NOT_OBSERVED, reference not accepted) and run Y (successful). The
composed bundle keeps Y's agent-artifact/effect/acceptance/binding/verifier
records and the certificate's execution session, but presents **X's execution
trace**. Hash chain fully intact; registry consistent; the only violated join
is J2 (session consistency across trace / certificate execution / effect).
Result on all 6 cases: V0 and V1 emit level 6 ("attribution PROVEN"); the
adjudicator computes level 1, truth unsupported; V2 rejects with
`claim-overreach supported=1; violations=J2,attribution`. No crypto failure
and no hash mismatch exists in this pattern — cross-record session consistency
is the entire detection surface.

## 4. Falsification conditions (F1–F4)

| Condition | Status |
|---|---|
| F1 — V0/V1 show no false promotions on defect suites → NO-GO | **Falsified**: 32/32 dev, 36/36 held-out |
| F2 — V2 yields no reduction vs V1 → NO-GO | **Falsified**: V1 36/36 → V2 0/36 |
| F3 — V2 over-rejects clean controls → invalid measurement | **Falsified**: V2 B0 8/8, C1 4/4, 0 false rejects |
| F4 — new post-freeze pattern does not reproduce → bounded result | **Falsified**: B5 6/6 promoted by V0/V1; V2 caught all; held-out did not break the mechanism |

## 5. Determination

**Mechanism confirmed.** HEB-1 is supported by reproducible, blind,
independently adjudicated measurements: schema/hash-integrity evaluation
systems promote cross-boundary-composed bundles to full claim strength, and
claim-binding validation eliminates the promotions with no control loss in
this fixture set.

**Genuinely new finding — yes, with explicit scope.** Against the assessed
prior art (SimGlot single-harness oracle integrity; "Grounded but Wrong"
claim–computation binding, statistics domain; TRAP/ReplayBench runtime
misbinding; NGCC practice report; governance-layer crypto binding), no work
demonstrates the five-element combination — cross-boundary composition →
claim-strength promotion → in security-claim evaluation machinery → measured
blind against an independent adjudicator → with a detection surface consisting
only of boundary-enforcement joins. The held-out B5 pattern sharpens the
delta: a session-split composition with an intact hash chain survives
schema-level and hash-level gates and is detectable only by cross-record
consistency — a class not covered by source-binding or hash-integrity gates
in the closest prior work.

**Not claimed:** novelty about any deployed evaluator; exploitability against
real systems; open-world coverage. External validity is limited to the
controlled synthetic fixture domain (self-designed faults, single held-out
pass, fixtures instantiated from a frozen deterministic seed).

### 5.1 Adjudication addendum (2026-10-19, post-review)

External review confirmed the synthetic mechanism and the B5 held-out result,
but adjudicated: novelty relative to the closest prior art **not established**;
real evaluator security impact **not demonstrated**; further independent
replication **GO**. The reviewer identified RFC 9334 (RATS), in-toto, the
`evidence.*` family, and TRAP/ReplayBench as closest prior art for binding
evidence to execution context.

The "Genuinely new finding — yes, with explicit scope" paragraph above is
**withdrawn as a novelty claim**. It records the assessment made before those
works were considered; it is not the current adjudicated status. The remaining
candidate contribution is the controlled empirical measurement of
false-attribution promotion in AI-authored cryptographic-exploitation
evaluation. Whether that contribution is novel is pending the independent
adversarial replication specified in
`HEB1_ADJUDICATION_RESPONSE_20261019.md`. The experimental results in
Sections 3–4 are unchanged.

## 6. Limitations and anti-overclaim

- Synthetic, controllable fixtures only; defect mechanisms were designed by
  the same party as the mitigation. The claim is a mechanism demonstration,
  not a detection benchmark.
- B5's materiality: the underlying candidate works in both runs; the promoted
  bundle misattributes provenance (a failed run's execution record inside a
  successful provenance chain). B1–B4b additionally include substance-false
  lures (faulty candidate, deleted evidence). Severity of any specific
  composition class is context-dependent.
- Single held-out pass by protocol design (no repeated sampling); the outcome
  is deterministic and fully re-runnable from the frozen bytes.
- All outcomes are preserved in the results JSONs; nothing was dropped,
  relabeled, or pooled across incomparable cohorts. Bounded mitigation only:
  V2 rejects the designed composition families; universal detection is not
  claimed.

## 7. Provenance

- `heldout/heldout_results.json` sha256 `4bda7b8f4183b577d1b6ab6dd998d7147e086e70ee2e1f202b7eb3726d1f7265`
- `heldout/heb1_heldout_gen.py` sha256 `076c56144775b93f36677479056bddd6127e69ce659763d4722bd4d2f85dd146`
- `heldout/heb1_heldout_runner.py` sha256 `5f74d9ab9c04bc81f016df4da390bd809979042141d3d0a55a9eae691ce69ecb`
- `build/runs/dev_run_20261019_073337/results.json` sha256 `db6e85cf5e909774bab1d7cf381d71cc6c98ee46656efc2b9ced8a21fd3dde4d`
- `freeze/HEB1_CONFIG_FREEZE.json` sha256 `a538c3df9c9b6179a75561a8e4073a0efd22ae431921e5bbbd4d74d58d1cb360`
- `freeze/HEB1_VALIDATOR_FREEZE.json` sha256 `0424eaa326130a7a8fb0ee708330aa9085414ff59efa283d583c5149c093c5fb`
- Protected files (RESULTS_LOCKs, paper .tex/.pdf) verified unchanged before
  and after both passes. Historical campaigns (H1, R0/R1, P010) were not
  reopened, rerun, or reused as evidence here.
