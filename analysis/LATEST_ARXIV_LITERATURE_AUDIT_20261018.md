# Recent arXiv literature audit — 2026-10-18

## Search scope
Direct arXiv API searches were run on 2026-10-18 for `cybersecurity` + `LLM agent`, `penetration testing` + `language model`, `cryptographic` + `agent`, and cybersecurity evidence/provenance/trace terms. DuckDuckGo search was unavailable because of an anti-bot challenge; no result was treated as verified from search snippets alone.

## Included primary sources

| Key | Source | Why it supports ACTS-Attack | Boundary / non-overlap |
|---|---|---|---|
| `reprobench` | Liang He, Sheng Wu, Haomiao Hao, Hongduo Zhao, Jia Yan, Purui Su, “ReproBench: Benchmarking LLM Agents on Reproducing Vulnerability From Scratch,” arXiv:2609.34450 (2026) | Decomposes vulnerability reproduction into six executable phases and evaluates downloaded artifacts, unpacked binaries, analysis logs, and validated crashes. Supports the manuscript’s staged evidence-chain and the distinction between post-environment success and from-scratch construction. | IoT vulnerability reproduction, not cryptographic exploitation; no ACTS denominator or record is reused. Verified via `https://export.arxiv.org/api/query?id_list=2609.34450`. |
| `heldt2026` | Tobias Heldt, Matt Turk, Christoph Landolt, Mario Fritz, “Does AI Help Cyber Attackers or Defenders? Evidence from Nonpublic Vulnerabilities and Subsequent Attacks,” arXiv:2610.06584 (2026) | Uses researcher-developed deterministic graders, includes cryptographic challenges, separates attack/repair outcomes, and tests subsequent non-independent resistance intervals. Supports task-specific oracle authority, non-independence cautions, and the need to avoid interpreting one accepted test as durable security. | Different benchmark and nonpublic software environments; cited as adjacent evidence, not pooled with ACTS. Verified via `https://export.arxiv.org/api/query?id_list=2610.06584`. |
| `assurancepentest` | Joas Antonio dos Santos Barbosa, “From Capability to Assurance in Autonomous Penetration-Testing Harnesses: A Framework and Reference Implementation,” arXiv:2609.22664 (2026) | Separates capability from evidence grounding, authorization, and tamper-evident accountability, and reports executable acceptance tests and an enforcement gap. Supports ACTS’s outcome-versus-attribution distinction and V/R/E tiering. | Penetration-testing harness assurance, not an empirical cryptographic capability comparison; no shared runs. Verified via `https://export.arxiv.org/api/query?id_list=2609.22664`. |
| `evoprobe` | Qianhong Guo, Wei Xie, Xiaofang Cai, Shuoyoucheng Ma, Chengxin Hu, Baosheng Wang, “EvoProbe: Evaluation-Driven Benchmark Evolution for LLM Agents,” arXiv:2610.19433 (2026) | Uses verifiable subtask outcomes and evidence-supported trajectory evaluation to expose phase-level bottlenecks beyond aggregate success. Supports the manuscript’s choice to report construction, execution, verification, and terminal failures separately. | Cybersecurity benchmark evolution, not a cryptographic attack study; cited for evaluation design only. Verified via `https://export.arxiv.org/api/query?id_list=2610.19433`. |

## Excluded or held out

- CyberArena and other dynamic attack/defense competitions: useful context, but they do not materially support the cryptographic evidence-boundary claim and would consume space without a direct manuscript dependency.
- CyberClear: relevant to APT provenance, but overlaps with existing PROV-AGENT/CTF-ABACUS/ORTHRUS coverage and is less direct for executed cryptographic exploitation.
- Unverified search-result titles and papers with unclear venue or metadata were not added.

## Integration decision
Add the four included sources to the related-work discussion and bibliography. Do not import their numerical outcomes into ACTS populations, denominators, or causal comparisons. Preserve the paper’s central claim: independently verified model-authored cryptographic exploit realization is contract-bounded, and accepted outcomes do not by themselves prove acquisition path, isolation, or immutable model identity.