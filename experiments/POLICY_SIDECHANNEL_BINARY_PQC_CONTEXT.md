# Policy, side-channel, binary, and PQC context map

This map distinguishes direct repository evidence from adjacent context. It
does not convert policy, timing, or availability observations into crypto
attack success.

| Context | Direct repository evidence | Scientific role | Boundary |
|---|---|---|---|
| Hybrid TLS policy | Frozen C3 `tls_policy_hybrid` card; local endpoint, weak-parameter negotiation, reserved-session oracle | Protocol-policy opportunity contrast; the task asks whether a declared weak policy can be demonstrated | Not evidence of an on-path downgrade, a new TLS flaw, or general model capability without admissible runs |
| Weak SSH negotiation | Frozen C3 `ssh_weak_algo_negotiation` card; legacy KEX/host-key negotiation and reserved transcript oracle | Second protocol-policy opportunity contrast with different negotiation surface | No wire-path or model-backed result is promoted here; the card defines a qualified target, not an observed success |
| Binary / parser surface | Frozen `parsing_overflow_service` and `known_vulnerable_service` task families; V4 feasibility matrix separates source, environment, execution, candidate, and oracle linkage | Adjacent implementation-exploitation context and provenance stress case | Not pooled with cryptographic primitive attacks or deterministic CBC controls |
| Side-channel / timing | E3 one-host clock calibration; 67/71 dual-clock rows within 1 ms, four breaches; retained median and factor-level definitions | Evaluator-clock and measurement-boundary science | Timing calibration is not a cache/side-channel attack and does not establish secret leakage |
| PQC / hybrid KEM policy | Canonical `C2_pqc_generality.json` records four local hybrid-KEM downgrade targets; `c2b_hybrid_required_control.json` records 45 trace-backed policy-control handshakes | Deterministic local attack and causal configuration-enforcement evidence | Not an ML-KEM break, not an AI/model capability result, not all-deployment generality, and not the pre-registered E3 environment |

The actionable conclusion is that ACTS has direct crypto implementation
observations for RC4, ChaCha20, and ECDSA; direct CBC evidence only as a
deterministic control; historical model-backed TLS/SSH policy trajectories;
and direct deterministic hybrid-KEM policy evidence. The PQC evidence is
kept separate from model capability and from the pre-registered E3 environment.

Primary artifacts: `sp2027/pre-registration/cards_v3/tls_policy_hybrid.json`,
`sp2027/pre-registration/cards_v3/ssh_weak_algo_negotiation.json`,
`sp2027/analysis/clean_v4_timing_provenance_feasibility_20261014/REAL_AGENT_H1_FEASIBILITY_MATRIX.csv`,
and `sp2027/analysis/clean_v4_timing_provenance_feasibility_20261014/EXP035_VS_NETWORKED_AGENT_ENVIRONMENT.md`.
The PQC-specific audit is `PQC_POLICY_ATTACK_AUDIT.md`.
