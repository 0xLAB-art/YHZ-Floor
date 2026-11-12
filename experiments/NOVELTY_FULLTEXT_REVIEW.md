# Full-text novelty review

Status: primary HTML full-text review completed for the seven named comparison
sources. This is still a novelty risk register, not a proof of originality.

| Source | Verified full-text construct | Boundary relative to ACTS-Attack |
|---|---|---|
| AICrypto | Three task types: 135 MCQs, 150 CTF challenges, and 30 proof problems; its CTF agent interacts with an environment and uses bounded multi-round attempts with pass@3 scoring. | Directly overlaps cryptographic vulnerability exploitation and agent interaction. ACTS must distinguish its implementation-specific opportunity-to-oracle provenance chain, independent secret authority, failure localization, and evaluator-scope claims. |
| CryptanalysisBench | 191 tasks across six primitive families and three tiers: known practical breaks, full/scaled no-known-break tasks, and frontier production primitives; practical attacks are automatically verified. | Directly overlaps cryptanalysis and automatic verification, including known breaks. ACTS should not claim cryptographic-agent evaluation as a category; its narrower distinction is vulnerable/misconfigured implementation exploitation plus evidence-bound execution and attribution. |
| Earlier ACTS multi-tier benchmark | Controlled metadata deprivation for blind cipher identification across seven cipher families, agentic tools, forced reasoning, deterministic heuristics, classical ML, perturbation and feature-ablation analyses, including ML-KEM-768/classical byte-distribution comparisons. | This is the closest historical overlap and covers several source-gap topics. The flagship must not claim novelty for multi-tier cipher identification, perturbation, ablations, heuristic contrasts, or PQC/classical byte-signal analysis; its distinct claim is the subsequent attack-centered implementation, oracle, provenance, and evidence-scope chain. |
| ExploitGym | Agents extend a program input that triggers a vulnerability into a working exploit; 898 real-world instances span userspace, V8, and Linux kernel, with protection variants and containerized environments. | Directly overlaps real exploit construction and environment interaction. ACTS specializes the attack mechanism and oracle to cryptographic implementation failures, secret authority, query/workload, and provenance. |
| ExploitBench | Exploitation is decomposed into 16 verified flags from coverage/crash through primitives, control-flow hijack, and code execution; 41 V8 bugs and model/environment, coaching, and harness arms. | Directly overlaps stage separation, deterministic oracles, and feedback/harness contrasts. ACTS contributes crypto-specific stages and oracle/evidence boundaries, not a generic capability ladder. |
| ABC | Checklist and empirical guidance for task/reward design; reports large relative overestimation reductions when applied to CVE-Bench. | Methodological overlap only. ACTS uses these concerns as safeguards and tests their consequences in crypto attack evidence; it does not present a checklist as the scientific contribution. |
| BenchJack | Automated red-team audit of benchmark hackability, eight flaw classes, and iterative repair over ten benchmarks. | Evaluator-adversary overlap. ACTS studies benchmark truth as a boundary condition while keeping cryptographic exploitation, not reward hacking, as the primary object. |

Safe contribution wording: ACTS-Attack studies an evidence-bound chain from a
cryptographic implementation opportunity through model inference, executable
construction, independent oracle verdict, and provenance/workload scope. It
must not claim to be the first cryptanalysis benchmark, the first agentic
cryptography benchmark, or a universal capability ranking.

Sources: the HTML full texts linked from `NOVELTY_MATRIX.md`.
