# Contract-Sound Exploitation — Prior-Art Differentiation Matrix v1

This matrix records the checked scope boundary for the proposed contribution. It is not a claim that the papers are identical; it identifies what ACTS-Attack must not present as novel by itself.

| Work | Established contribution | Overlap risk | ACTS-Attack differentiation requirement |
|---|---|---|---|
| ExploitGym, arXiv:2605.11086 | Large realistic exploitation benchmark with 898 vulnerability instances, executable environments, and defense/configuration variation. | Working agent-authored exploits and scale are not sufficient novelty. | Focus on cryptographic observation-contract equivalence and attribution boundaries, not benchmark size or generic exploit success. |
| ExploitBench, arXiv:2605.14153 | Capability ladder with 16 measurable flags, deterministic challenge-response oracles, differential execution, and environment/harness ablations. | Capability decomposition and deterministic oracle use are already established. | Demonstrate a cryptographic-specific representation intervention where semantically equivalent sufficient evidence changes agent completion, plus held-out evaluator-fault detection. |
| CryptanalysisBench, arXiv:2607.18538 v2 | 191 cryptanalysis tasks across six primitive families, independently verifiable attacks, and reported novel cryptanalysis. | Cryptographic task coverage or more known primitive attacks is insufficient. | Study how equivalent information contracts and evaluator boundaries affect attributable exploit construction; do not compete on task count. |
| ReproBench, arXiv:2609.34450 | Six evidence-backed stages for reproducing real firmware vulnerabilities from CVE identifiers, with artifact-grounded phase outcomes. | Staged artifacts and evidence-grounded reproduction are not novel alone. | Define cryptographic-specific sufficiency witnesses, ambiguity counterexamples, and claim-separated certificates for agent exploit attribution. |
| When Agent Evaluation Becomes Unreliable, arXiv:2610.16067 | Oracle-integrity auditing, replay/ablation analysis, fault catalogue, and configuration-dependent measurement effects. | Generic evaluator defects, replay checks, and saying scores can be wrong are already covered. | Use real ACTS defects plus held-out cryptographic variants, blind validator decisions, and a primary C1/C2 semantics-preserving representation contrast. |

## Contribution boundary

The proposed result is publishable as a distinct contribution only if it demonstrates all of the following:

1. C1 and C2 are proven equivalent and sufficient over the complete agent-accessible interface;
2. the agent outcome differs reproducibly under the representation intervention, or the validator discovers a cryptographic-specific held-out failure mechanism not captured by the baselines;
3. the effect is not a prompt, parser, transport, oracle, environment, or budget confound;
4. the result has independently replayable artifacts and explicit claim boundaries;
5. negative and inconclusive outcomes are retained.

A certificate format, a larger task list, an additional metric, or a generic warning about oracle integrity is not sufficient on its own.

## Sources checked

- https://arxiv.org/abs/2605.11086 (submitted 2026-05-11)
- https://arxiv.org/abs/2605.14153 (submitted 2026-05-13)
- https://arxiv.org/abs/2607.18538 (v2, revised 2026-07-29)
- https://arxiv.org/abs/2609.34450 (submitted 2026-09-28)
- https://arxiv.org/abs/2610.16067 (submitted 2026-10-12)