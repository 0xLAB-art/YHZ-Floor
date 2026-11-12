# PQC family reconciliation

This record joins the canonical deterministic PQC artifacts to the existing
81-family graph without treating catalog families as independent physical
trials. It is an additive reconciliation; the frozen source files and prior
summaries are unchanged.

## Family joins

| graph family | graph result statement | canonical source | observed unit | admissible interpretation |
|---|---|---|---|---|
| `PQC_endpoint_policy` (`FAM-2292f491ef93d899694c`) | `HIST-C2-four` (`ACTS-E-275210128340d4def669`) | `ACTS-ATTACK/data/C2_pqc_generality.json` | four local target demonstrations: three named hybrid groups plus one cross-curve configuration | deterministic endpoint-policy downgrade demonstrations in the recorded provider configuration; not an ML-KEM break, on-path MITM result, or all-deployment generality |
| `PQC_policy_control` (`FAM-6cf1291f276e4bb2da47`) | `HIST-C2b-PQ45` (`ACTS-E-a957cda12c6477489695`) | `ACTS-ATTACK/data/c2b_hybrid_required_control.json` | 45 trace-backed handshakes, nine cells, five repetitions per cell, zero trace disagreements | local configuration-enforcement contrast: allowing server accepted classical-only 5/5 while requiring server rejected it 5/5; not a model result |
| `PQC_message_edit` (`FAM-c8ef2edaed204a823171`) | `HIST-C2t1-edit` | `ACTS-ATTACK/data/c2t1_open_source_reproduction.json`, `ACTS-ATTACK/data/c2t1_toolchain_diversity_repro.json` | retained historical message-edit/reproduction family | retained as a distinct historical family; not merged with the endpoint-policy or C2b control result |

The first two rows are related by mechanism and environment, but they are not
pooled: the first varies the client offer across four target configurations,
whereas C2b varies server policy and client offer in a pre-registered 3x3
matrix. The third row remains separate because message editing and endpoint
policy are different attack interfaces and have different evidence contracts.

## Source and parser checks

- `C2_pqc_generality.json` SHA-256:
  `3d62b9581783a94af88a77cc1fe31fbf45cf7ad708b3e1230c4222db704c97f8`.
- `c2b_hybrid_required_control.json` SHA-256:
  `826686ac374ea999745080f72b45a08d0f54575de08aed65b5c6f846947774f5`.
- A fresh parse of the archived C2b endpoint traces in a temporary copy using
  `ACTS-ATTACK/harness/c2b_parse.py` reproduced 45 records, nine unanimous
  five-repetition cells, zero endpoint disagreements, and the exact archived
  `c2b_verdicts.json` SHA-256 `6b2e231a3a06877e286966bb0fda2ce664a631d5a7837b82962166d9a03b9c71`.

## Limits retained

The C2 source names unavailable groups in its recorded OpenSSL/provider
configuration, and C2b explicitly differs from the pre-registered E3
environment. The reconciliation therefore supports a bounded local policy
mechanism finding only. It licenses no claim about AI construction, an
on-path downgrade, ML-KEM cryptanalysis, or deployment prevalence.
