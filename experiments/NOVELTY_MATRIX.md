# Primary-source novelty risk register

This is a provisional comparison, not a novelty certificate. It records what
neighboring work appears to measure and where ACTS-Attack must avoid generic
claims. Source links are primary paper, project, or checklist pages.

| Work | Primary construct | Direct overlap risk | ACTS-Attack differentiator candidate | Safe wording now |
|---|---|---|---|---|
| AICrypto | Broad LLM cryptography evaluation with multiple-choice, CTF, and proof tasks plus an agent framework | Cryptography capability and agent execution | ACTS centers real implementation weaknesses, independent oracle linkage, execution provenance, cost, and failure-stage localization | “Complements broad cryptography evaluation with evidence-bound implementation attack trajectories.” |
| CryptanalysisBench | 191 cryptanalysis tasks across six primitive families, including known breaks, full/scaled variants, and frontier schemes | Automatically verified cryptanalytic success and family breadth | ACTS separates model inference, code construction, execution, oracle authority, contract defects, and deterministic controls | “Studies a different construct: end-to-end exploitation of vulnerable or misconfigured implementations.” |
| Earlier ACTS multi-tier benchmark | Controlled blind cipher identification with metadata tiers, agentic tools, deterministic heuristics, classical ML, perturbation/feature ablations, and ML-KEM-768/classical byte-signal comparisons | Direct overlap with ACTS’s earlier source-gap topics and cipher-identification setup | The flagship focuses on implementation attack trajectories, independent oracle authority, execution/provenance scope, and evaluator-bound evidence after the identification setting | “Does not claim a new multi-tier identification benchmark; contributes the subsequent evidence-bound exploitation analysis.” |
| ExploitGym | 898 real-world vulnerabilities across userspace, V8, and Linux-kernel exploitation in reproducible environments | Real exploit construction by agents and environment interaction | ACTS focuses on cryptographic mechanisms, secret authority, nonce/keystream/padding interfaces, and cryptographic oracle semantics | “Cryptographic exploitation is a specialized complement to general vulnerability exploitation.” |
| ExploitBench | 16-flag capability ladder from vulnerable-code reach to arbitrary code execution, with deterministic challenge-response and coaching/harness arms | Stage-wise exploit progression, deterministic oracles, and feedback ablations | ACTS’s stages are crypto-specific and tie opportunity, inference, construction, oracle verdict, workload, and provenance to the same attack | “Adopts the principle of stage separation while contributing cryptographic attack-stage evidence.” |
| ABC | Agentic Benchmark Checklist for rigorous benchmark design and reporting | Evaluator validity, denominators, controls, and reproducibility | ACTS empirically tests evaluator truth and secret authority as part of actual crypto attack claims, rather than presenting only a checklist | “Uses checklist concerns as evidence safeguards, not as the scientific result.” |
| BenchJack | Automated audit/red-team system for benchmark hackability and reward-hacking paths | Evaluator attack surface, answer leakage, trust boundaries, and proof-of-concept audit | ACTS preserves evaluator science but remains attack-centered on cryptographic exploitation, not benchmark gaming as the primary target | “Treats benchmark integrity as a boundary condition for cryptographic attack evidence.” |

The strongest defensible contribution candidate is therefore not a benchmark
size or a generic capability leaderboard. It is the empirical separation of
cryptographic opportunity, model inference, executable construction, oracle
acceptance, and evaluator/provenance boundaries, including meaningful nulls
and instrument defects. This candidate still requires close full-text review,
matched replication, and claim-by-claim citation checking.

Primary sources:

- AICrypto: <https://arxiv.org/abs/2507.09580>
- CryptanalysisBench: <https://arxiv.org/abs/2607.18538>
- ExploitGym: <https://arxiv.org/abs/2605.11086>
- ExploitBench: <https://arxiv.org/abs/2605.14153>
- ABC checklist: <https://arxiv.org/abs/2507.02825>
- BenchJack: <https://arxiv.org/abs/2605.12673>
- Earlier ACTS multi-tier benchmark: <https://arxiv.org/abs/2609.26893>
