# Stage 6 — Matched Translation into the Native Provenance Models (corrected)

**Project:** ACTS-Attack  
**Date:** 2026-10-20  
**Status:** COMPLETE — corrected after methodological review; the earlier superiority framing is **withdrawn**

## 0. What changed, and why

A review of the first version of this stage found three methodological defects. All three are
correct, all three are fixed here, and the affected claims are withdrawn.

| Reviewer objection | Verdict | What was done |
|---|---|---|
| in-toto was tested with **no artifact rules and no inspection**, so 22/22 shows a *minimally configured* deployment, not an in-toto limitation | **Correct** | Two further arms added: `in_toto_policy` (in-toto's own `REQUIRE` rules **plus** an independent inspection) and `in_toto_policy_stateful` (same, with a shared file-backed ledger) |
| the SLSA arm never reached policy evaluation — it failed at trust setup — so "6/6 false rejections" is not a security comparison | **Correct** | The SLSA arm is reclassified **NOT_COMPARABLE / TRUST-SETUP FAILURE**, with the exact stage recorded per case. The 6/6 figure is withdrawn |
| the "delegated" arm calls the ACTS aggregator, so it is an integration test, not an independent baseline; and "in-toto cannot express cross-case replay" overstates the evidence | **Correct** | The arm is relabelled `in_toto_acts_integration`; the replay claim is withdrawn and replaced by the measured fact that a *stateless* inspection cannot preserve replay state, while a stateful inspection can — and the stateful arm reaches 22/22 agreement |

The first version's artifacts are retained (`translation_results.json`, `run_translation.py`) as
the record of the superseded configuration.

## 1. Arms

| Arm | Guarantee level | Construction |
|---|---|---|
| `acts` | reference | the frozen ACTS aggregator, ledger-bearing, both V2 semantics |
| `in_toto_default` | **G1** | link + layout with one step, **no** artifact rules, **no** inspection: authenticity, functionary authority, threshold, command alignment — nothing else |
| `in_toto_policy` | **G4** | in-toto's own `REQUIRE` artifact rules **plus** an inspection running an **independent** verification policy: it imports nothing from `e2a.aggregator`, re-derives every check from the contract, and adjudicates the predicate with the project's **frozen Stage 01 reference verifier** (pure-Python curve arithmetic, a different implementation from the E2A reference) |
| `in_toto_policy_stateful` | **G5** | the same independent policy, with a **shared, file-backed ledger** so the inspection is stateful across cases |
| `in_toto_acts_integration` | G4 (integration) | an inspection that calls the ACTS aggregator itself — an **integration test**, not an independent baseline |
| `slsa` | — | a SLSA v1.0 provenance statement verified with `slsa-verifier` |

The link is built from the evidence **as presented in the certificate** (not from files on disk), so
a missing evidence record is missing from the link, and in-toto's own artifact rules detect it.

## 2. Results — the identical 22-case evidence

| Arm | Level | Accepted | False promotions (of 16) | False rejections (of 6) | Agreement with ACTS |
|---|---|---|---|---|---|
| `acts` (reference) | — | 6/22 | **0** | 0 | — |
| `in_toto_default` | G1 | 22/22 | **16** | 0 | 6/22 |
| `in_toto_policy` | G4 | 7/22 | **1** (`X_REPLAY`) | 0 | 21/22 |
| `in_toto_policy_stateful` | G5 | 6/22 | **0** | 0 | **22/22** |
| `in_toto_acts_integration` | G4 (integration) | 7/22 | 1 | 0 | 21/22 |
| `slsa` | — | 0/22 | not applicable | not applicable | not applicable |

### The three result classes, separated

**(a) The security property is not supported by the baseline at all.** *No arm of this comparison
falls in this class.* Once in-toto is given the policy, it reproduces the ACTS contract's decisions
exactly (22/22 with a stateful inspection).

**(b) The security policy is weakly configured.** This is exactly what `in_toto_default` measures: a
deployment that turns on in-toto's authenticity, authority, threshold and command-alignment
machinery but supplies no task policy accepts **all 22** cases, promoting **16 of 16**
non-attributable ones. The 16/16 figure is therefore a **default/minimal-configuration
measurement**, and it is *not* evidence about in-toto.

**(c) The policy is present and correctly configured but still fails.** This class contains
**no cases**: the independent policy arm reproduces the reference on 21/22, and the stateful arm on
**22/22**, with zero false promotions and zero false rejections.

### The guarantee ladder, per case

`G0` no evidence binding → `G1` authenticity + authority → `G2` artifact rules → `G3` digest and
context binding → `G4` independently recomputed predicate → `G5` cross-case replay protection.

| Minimum level needed to reach the correct verdict | Cases | Which checks carry the decision |
|---|---|---|
| **G1** | the 6 honest-success cases | authenticity alone already accepts them — and also all 16 others |
| **G4** | 15 of the 16 non-attributable cases | predicate-false (6), declared-source/candidate mismatch (3), context binding (3), evidence missing (2), reference-adjudicates-other-observation (1) |
| **G5** | 1 case (`X_REPLAY`) | the cross-case replay ledger: `context-already-consumed` |

The per-case failed-check table is in `analysis_v2.json` for every case.

**The finding that replaces the old one:** full discrimination of this corpus requires **G5**, and
**G4 is short by exactly one case** — the replay case, which needs state that persists across
cases.

## 3. SLSA — NOT_COMPARABLE, with the exact stage

`slsa-verifier` was run with network access. Per case it stops at:

- `provenance-acquisition-rekor`: "error searching rekor entries: no matching entries found" — the
  verifier looks for a transparency-log entry for the subject digest and the locally produced
  statement has none; or
- `timeout` on the same lookup.

It never reaches a policy stage. `slsa-verifier`'s decision inputs are exactly
{builder identity, source expectations, subject digest, provenance signature}, and its trust model
is keyless: builder provenance published in Rekor with a Fulcio identity. The ACTS evidence is a
*locally signed record set* with no such form, and publishing it to a public transparency log is
neither possible offline nor appropriate here.

**Therefore the SLSA arm is NOT_COMPARABLE, and the earlier "6/6 false rejections" figure is
withdrawn.** What can be said is a *model-level* fact, not a verdict rate: the SLSA provenance model
has no place for a per-case causal chain, an independently recomputed task predicate, or a
per-case signed context binding — those can only be carried as opaque materials, and the verifier
has no hook to evaluate them.

## 4. Can ACTS and in-toto be combined without duplicating guarantees or changing the claim?

**Mechanically: yes. Semantically: only if the two claim types are kept distinct.**

- The guarantees are **disjoint, not duplicated**: in-toto supplies authenticity, functionary
  authority, threshold and artifact rules; the ACTS contract supplies causal binding and the
  predicate adjudication. Neither subsumes the other.
- The measured combination attributes exactly the 6 cases the ACTS contract attributes; the
  in-toto layer adds authenticity and rule checking, and **no discrimination** (it accepts all 22).
- The **meaning** does change if the two are read as one claim. in-toto's final-product attestation
  is about *which artifacts an authorized functionary produced under which layout*; the ACTS claim
  is about *a specific execution producing a candidate that satisfied a task predicate*. A
  combined artifact must therefore state both claims separately — collapsing them would either
  over-claim (reading provenance as attribution) or under-claim (reading attribution as
  provenance). This is a documentation requirement, not a technical obstacle.

## 5. What is now claimed, and what is not

**Withdrawn.** That ACTS is superior to complete provenance systems; that native in-toto
false-promotes 16/16; that native SLSA false-rejects 6/6; and that in-toto cannot express
cross-case replay protection.

**Supported.** That the attribution policy is not supplied by the upstream models: with its own
artifact rules and an independent inspection, in-toto reproduces the ACTS contract's decisions
exactly, which means the upstream frameworks can *host* the policy but do not *contain* it. The
policy itself is 195 lines of independent verification code (plus a 270-line frozen aggregator for
the ACTS-native path); the upstream machinery is what the adopter inherits.

## 6. Limitations

1. The translation is mine and is published so it can be audited; a different translation could
   express more.
2. The independent policy is an *independent re-implementation*, not an independent *design*: it
   follows the same contract, so it measures implementation independence, not design independence.
3. The 22-case corpus is constructed, and the 11,256-evaluation soundness check is **bounded
   mechanized testing, not a formal proof** — the mutation generator's coverage is not exhaustive.
4. SLSA could not be exercised at all in this environment; the comparison for SLSA is a model-level
   statement, and it is the weakest of the three.
5. One corpus; no prevalence claim.

## 7. Evidence

| Item | SHA-256 |
|---|---|
| `stage6_matched_translation/run_translation_v2.py` | `86180c9a07796446fe89aba0e2412c6cd5f8212982a612cd3985d97af7f64626` |
| `stage6_matched_translation/independent_policy.py` | `3c036ef80a3903798df1a8aefbca058da10bd972e3129d21d74cbfa780880fd5` |
| `stage6_matched_translation/translation_results_v2.json` | `be712fa8e1474e8dfc0455d72dd591226bb5e2d1450fba00c42f96378adad8d8` |
| `stage6_matched_translation/analysis_v2.json` | `2b0872ee4a70161e384450d574b8f10010648186182bea70a3489ef6a98879ef` |
| `stage6_matched_translation/delegation_adapter.py` (integration arm) | `863bc747642ded6207e9c914f87cd3c3bb3c1e89134b75aa41d787ca600ee409` |
| `stage6_matched_translation/translation_results.json` | the superseded first version, retained |
| `stage6_matched_translation/failed_run_stale_linkdir/` | a run invalidated by a stale link directory, retained |

The Stage 6 code lives in the stage directory, not in `research/deliverables/`; the deliverables
manifest therefore covers the documents, and the hashes above cover the harnesses and results.