# Stage 6 — Matched Translation into Native Provenance Models

**Stage:** Matched translation, `sp2027/analysis/acts_next_phase_20261019_v2/stage6_matched_translation/`
**Written:** 2026-10-20, **before** the translation run.
**Corpus:** the 22 cases of the frozen inventory, as executed by the HEB-2 Contract V2 run
(`heb2_contract_v1/runs/20261020T091958Z_v2`), with the identical evidence the ACTS contract
evaluated.

---

## 1. Objective

Stage 2 compared *signatures* (Cosign verified the ACTS signed bytes) and found no native
interoperability. That is not a comparison of **policy capability**: it says nothing about
whether in-toto or SLSA can *decide* the same question the ACTS contract decides.

This stage performs the comparison that Stage 2 could not: it **expresses the ACTS policy in the
upstream models** and runs the identical evidence through them.

## 2. Arms (frozen before execution)

| Arm | What it is |
|---|---|
| `acts` | The reference decision: the frozen ACTS aggregator, both V2 semantics. |
| `in_toto_native` | The evidence translated into an in-toto **link** and a **layout** whose step declares only the command that was executed, with **no artifact rules and no inspection**. This is the upstream model used as it comes. |
| `in_toto_delegated` | The same link and layout **plus one inspection** whose command is an external program that applies the ACTS policy. This is the upstream model used with the policy delegated to it. |
| `slsa` | The evidence translated into a SLSA v1.0 provenance statement, verified with `slsa-verifier`. |

The translation is fixed in advance:

- **link** (the evidence): `materials` = the program source and the public instance actually
  executed; `products` = the candidate output actually captured; `command` = the recorded
  invocation; `byproducts` = the observation and reference digests, the execution status and the
  signed context.
- **layout** (the claim): one step named `execute` whose `expected_command` is the same recorded
  invocation, and whose material/product rules are **empty** in the native arm.
- **inspection** (the delegation): one command, `delegation_adapter.py`, which applies the ACTS
  policy to the case's own evidence and exits 0 only on `ATTRIBUTED_SUCCESS`.

The link and the layout are signed with an Ed25519 key and verified with `in-toto-verify`,
exactly as an upstream deployment would.

## 3. Predictions, stated in advance

- **P1 (native expressiveness).** The native in-toto model cannot distinguish the 6 attributable
  cases from the 16 non-attributable ones on identical evidence, because none of the nine ACTS
  checks has a native counterpart. *Expected: it accepts cases the ACTS contract rejects.*
- **P2 (delegation).** With the ACTS policy delegated, the in-toto verdict reproduces the ACTS
  verdict, and the *cost* of that agreement is the whole ACTS policy, not the upstream model.
- **P3 (SLSA).** The SLSA verifier's model — signed provenance, builder identity, subject digest,
  source expectations — has no place for the ACTS predicate; the verification outcome is
  determined by signature/identity, not by the policy.

## 4. Threats to validity (declared in advance)

1. **The translation is mine.** A different translation could express more of the policy; the
   result is about *this* faithful translation, and the adapter's source is published.
2. **The delegated arm is circular by construction** — it reproduces the ACTS verdict because it
   *is* the ACTS policy. That is the point of the measurement, not a flaw: it isolates how much
   of the decision the upstream model supplies.
3. **The link's materials are the executed bytes**, so a faithful translation may be *more*
   faithful than the claimant's own certificate for the identity-swap fixture. The comparison is
   therefore conservative against the native arm.
4. **SLSA verification needs a verifiable signature.** A locally signed statement is not
   keyless-verifiable; the observed outcome may reflect that rather than the policy question.
   Recorded as observed, not interpreted as a policy result.

## 5. Claims this stage may not support

- That in-toto or SLSA is "worse" than ACTS. The result is about *policy expressiveness in the
  native verification model*, measured on one translation and one corpus.
- Any prevalence or generalisation claim.
- Any novelty claim on its own.