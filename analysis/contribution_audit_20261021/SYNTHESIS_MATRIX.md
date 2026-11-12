# Consolidated claim / evidence / closest-prior-work matrix

Derived from `abc_prior/claim_comparison.json`,
`agentsuite_prior/claim_comparison.json` and the three wave-1 analyses.
Every wave-1 number was independently reproduced by `root_verify.py`.
The manuscript was not modified by this audit.

## C1 — measurement technique

**Claim.** A controlled separation of attack correctness, source admission and execution attribution as an evaluation procedure.

**Verdict.** Supported as a controlled evaluation procedure, not as a new general principle. Both comparators own the decomposition template: ABC separates true task success from the automatic score (App. A, p. 17), AgentSuite decomposes measurement invalidity by benchmark component (Table 2, p. 3). Our increment is the unit of analysis (the submitted program and its execution evidence) and the intervention (byte-identical re-admission).

**Our evidence.**
- Zero of 852 frozen sources were rejected for imports under the v3 policy; the three pre-output failures are one syntax error and two runtime errors.
- The narrower legacy policy is a counterfactual policy, not the task contract: all 205 of its import rejects concern modules the frozen prompt explicitly permitted. Calling them task-contract violations would be incorrect.
- Conservative removal of eligible whole unused import statements, applied to 128 derivatives, left every observed output identical; 104 derivatives then qualified under the legacy policy and 98 of those are cryptographically correct.
- Runtime tracing observed a real load of the imported object in 100 of the 101 sources with static legacy-disallowed references.

*Implication.* The policy-sensitivity finding survives the strongest available deflation, but it is evaluator-policy dependence under a changed rule, not evidence that the evaluator erred against the task contract.

**ABC.** ABC's taxonomy is two-layer and has no source-admission layer: keyword sweep finds 'admission', 'source admission', 'import' (as policy) and 'predicate' have 0 occurrences. ABC's method is a static, human-scored checklist audit (1 point per satisfied item, p. 4) plus per-issue designed experiments (Sec 5.2, p. 9); it never re-admits byte-identical artifacts under a changed rule, and it never decomposes a single reported result into three separately measured causes. ABC quantifies flaw-induced score distortion (KernelBench 31% absolute, p. 9; CVE-Bench time-based SQLi 32.5%, p. 10); our procedure quantifies the share of outcomes that flip under a different admission rule applied to unchanged programs (46/256, 16/256, 122/256; 6.2%-47.7% per arms, manuscript Sec 4/Fig policy-effect). This is a difference in kind of evidence (intervention vs audit), not only in domain.

**AgentSuite.** {'level': 'kind_on_one_axis', 'anchors': ["App. B.1, p.13: annotation guideline requires 'clear, observable evidence of a benchmark-intrinsic validity issue' - the agent's own output is not the judged object", 'Fig. 1, p.2: Ground Truth is a design-time reference trajectory, not runtime evidence about a specific run', 'Sec. 3.2-3.3, p.4: no execution stage in the pipeline'], 'description': "Object of separation differs: COBA separates which BENCHMARK COMPONENT is broken (design-time artifact); we separate which STAGE OF THE RUN produced the failure (artifact correctness -> source qualification -> execution evidence) for agent-produced programs in a security setting. The 'execution attribution' class has no counterpart among the four components - it is a fifth, runtime-evidence axis.", 'is_domain_only': False}

**Strongest support.** The three-way decomposition is executed over 852 sessions with an independent cryptographic predicate and a stage-resolved denominator, and the middle axis is measured, not asserted.

**What would change the verdict.** Applying the decomposition to a second, non-cryptographic benchmark's retained programs. Until then it is a local technique with a domain application.

## C2 — measurement technique

**Claim.** Paired representation contrasts under a common executor, followed by a changed admission rule applied to unchanged programs, estimating evaluator-policy dependence under the tested contract (not model rankings, not a general causal capability effect).

**Verdict.** Supported as a measurement instrument, and this is the strongest candidate. ABC already varies the evaluation rule on fixed artifacts (App. G p. 32; Sec. 5.3/Fig. 6 pp. 9-10) and AgentSuite already shows evaluation-side changes move reported capability with a null baseline (p. 8). Our increment is narrower and different in kind: the program bytes are fixed between the two evaluations, the contrast is paired at the instance level, and the estimator is policy dependence rather than a leaderboard.

**Our evidence.**
- L3 R2-R0 under the current contract: 125/128 versus 124/128, a -0.78 pp contrast.
- The same 128 matched instances under legacy admission: 100/128 versus 58/128, a -32.81 pp contrast; the policy change is -32.03 pp with 50 negative and 9 positive per-instance shifts and 69 unchanged.
- The preregistered L3 verdict reproduces exactly: intervals [-2.34375, 3.90625] and [-4.6875, 3.125] pp, Holm-adjusted p = 1.000, both EQUIVALENT_WITHIN_MARGIN.
- The interaction is not uniform: at L1/L2 it is confined to ECDSA, and the L3 R2 shift runs from -21.88 pp (XOR only) to -42.19 pp (ECDSA only).

*Implication.* A changed admission rule moves the apparent representation contrast by up to 32 pp while program bytes and historical cryptographic outcomes are held fixed. This is an artifact-level counterfactual, not a model comparison and not a fresh policy deployment.

**ABC.** ABC's contrasts are not paired at the instance level: no matched instance units, no paired test, no equivalence margin, no preregistration; ABC's own statistics are descriptive percentages, and its Appendix H intervals are a normality-based interval for ground-truth noise (Eq. 3, p. 34), a different quantity. The NeurIPS checklist answer to Q7 (p. 38) states all reported numbers are deterministic and carry no error bars - incompatible with paired inference. ABC never varies a source-admission rule (0 occurrences of 'admission'), never manipulates representation as an independent variable, and never frames an estimand of evaluator-policy dependence. ABC's varied dimension is outcome grading (state/substring/whole-string matching, judge configuration), not program admission. App. G varies a judge over text answers; C2 varies an admission gate over generated source programs.

**AgentSuite.** {'level': 'kind_in_the_estimator', 'anchors': ['Sec. 4.6, p.8: AgentSuite varies the TASK SET and re-runs models - a between-set comparison whose unit is (model, task) and whose output is a leaderboard', 'Sec. 3.1-3.3, pp.4-5: no execution and no per-artifact rule re-application, so an artifact-level counterfactual is not producible', 'Sec. 4.1-4.2, pp.5-6: unit of analysis is the task, not a submitted program'], 'description': "Ours holds the generated program bytes fixed and varies only the admission rule, paired at the instance level, with a preregistered +/-10pp equivalence margin for the representation contrasts and a 6.2%-47.7% rejection rate across arms. Program bytes are fixed between policy evaluations, not across representation arms. This is a within-artifact counterfactual, a genuinely different estimator - but a narrower claim than AgentSuite's (we claim nothing about model rankings).", 'is_domain_only': False}

**Strongest support.** The -32.03 pp L3 R2-R0 shift is reproduced from 128 matched instances, survives conservative unused-import removal, and the preregistered L3 verdict is unchanged. The legacy policy was legitimate under its own prompt, so the finding is evaluator-policy dependence, not evaluator error.

**What would change the verdict.** Re-grading a second benchmark's retained programs under two admission rules with byte-identical artifacts and paired contrasts. If the shift does not reproduce there, this is a property of our harness's legacy policy.

## C3 — domain application

**Claim.** Independent cryptographic predicates and full fresh program replay against retained public inputs.

**Verdict.** Supported as a domain application with a rigour increment. Independent predicates are already ABC's vocabulary (T.7, T.9, O.d.1, pp. 5-6). AgentSuite explicitly places execution-based matching in related work and does not generalise it (App. A, p. 12), so the fresh-replay discipline has no counterpart there.

**Our evidence.**
- 851 syntax-valid originals plus 128 derivatives were freshly executed; all fresh cryptographic outcomes match the retained predicates, with 738/768 primary, 63/64 noise and 20/20 abstention controls.
- Source and prompt hashes match all retained records and the input hashes are unchanged.

*Implication.* The replay is a re-execution of retained programs against retained public inputs. It is not fresh model generation.

**ABC.** 'Cryptographic predicate' is a domain instantiation: 'cryptograph*' has 0 occurrences in the 41-page text and no assessed benchmark (Table 1 p. 8, Table 3 p. 19) contains a cryptographic task; the closest cyber items are answer-matching on Cybench (Table 8, p. 23) and CVE-Bench state matching (Sec 5.3). 'Full fresh program replay against retained public inputs' is a re-execution discipline with no counterpart in ABC: 'replay' has 0 occurrences; ABC's KernelBench re-scoring applies NEW tests to OLD outputs, which is not replay of old programs against old retained inputs.

**AgentSuite.** {'level': 'kind', 'anchors': ['Sec. 3.1-3.3, pp.4-5: pipeline operates on static task artifacts with LLM judging; no execution module at any stage', 'App. A, p.12: execution-based validation treated as out-of-scope narrow-domain work'], 'description': 'Ours introduces executable ground truth where the artifact is a program and the ground truth is a cryptographic relation, and replays admitted programs against retained public inputs (852/852 reference-replay agreement; staged full candidate re-executing 851 admitted programs), explicitly not fresh model generation.', 'is_domain_only': False}

**Strongest support.** 852/852 reference-replay agreement with an independent cryptographic predicate, and 851 admitted programs re-executed in the staged candidate.

**What would change the verdict.** Nothing in the comparators; the limit is that the replay is of retained programs, so it cannot support a claim about fresh generation.

## C4 — domain application

**Claim.** Complementarity of authenticated evidence and claim-specific joins in bounded adversarial attribution tests, using existing provenance mechanisms.

**Verdict.** The only candidate with no overlap at either comparator: 'provenance', 'attribution', 'signature' and 'admission' occur zero times across the 41 ABC pages and the 20 AgentSuite pages. But the right comparators are provenance-aware works (in-toto, SLSA, CTF-ABACUS, ORTHRUS), not these two, and the manuscript already concedes that configured provenance mechanisms implement the tested policy.

**Our evidence.**
- 1,096 validator/adjudicator invocations across 274 bundles agree with the archived decisions; zero disagreements.
- Across the five populations, join-only and signature-only checks each promote attack-family cases that the combined check rejects (IAR-C 10/28 and 14/28, combined 0/28; IAR-B heldout 16/44 and 28/44, combined 0/44).
- The four soundness corpora recount to 11,256 evaluations of 1,407 mutants with no observed soundness violation.
- The 14/16 rejection figure reflects a full-attribution-only validator rejecting fourteen lower-level requests; it is a functionality difference, not a fair comparative false-reject rate.
- IAR-C had already evaluated the same 44 case IDs during calibration, so the preserved corpus is a preserved replay, not an untouched held-out test.

*Implication.* Authenticity and claim-specific binding are jointly required against the tested record-rewriting and splice cases. This is a domain application of existing provenance mechanisms, not a new mechanism, and not a prevalence estimate.

**ABC.** ABC supplies no attribution machinery, no trust model, no signed-record design, no claim scoping, and no mutation-based testing of an evaluation decision; its unit of analysis is the benchmark, not a claim about one execution. Our design deliberately reuses existing provenance mechanisms (in-toto inspection, SLSA arm, shared replay ledger) and tests a fixed decision policy over 11,256 mutation evaluations with no observed soundness violation, plus live-target and loopback-ingress exercises against fabricated claims; the manuscript concedes this is 'its measured application to cryptographic attack claims rather than a new signing, logging or isolation primitive'.

**AgentSuite.** {'level': 'kind', 'anchors': ['Sec. 3.1, p.4: the four-component model contains no runtime-evidence component', 'App. A, p.12: related work covers benchmark validity, agent benchmark validation, but not evidence binding for observed executions'], 'description': "Our artifact is a claim-specific attribution policy (observer-signed record over exact executed bytes and captured stdout; reference-signed recomputation of the task predicate from private target state; role authorization; digest agreement; replay policy; the claimant's own claims block excluded from the decision), validated by bounded mechanized testing (1407 mutants x 2 readings = 11256 evaluations, no observed soundness violation), live-target and loopback-ingress exercises against fabricated claims, and an in-toto inspection reproducing 21/22 decisions (22/22 with a shared replay ledger).", 'is_domain_only': False}

**Strongest support.** Joint necessity of authenticity and claim-specific binding across 274 bundles with zero disagreements, plus 11,256 bounded mechanized evaluations with no observed soundness violation, and a configured in-toto inspection reproducing 21/22 then 22/22 decisions.

**What would change the verdict.** A provenance-aware comparator, not ABC or AgentSuite. The release-evidence audit is documentary, not executable validation, and must not be presented as such.

## C5 — domain application

**Claim.** An integrated security-specific empirical method, rather than generic discovery that benchmark flaws distort performance.

**Verdict.** Not supported as phrased. The contrastive framing 'rather than generic discovery that benchmark flaws distort performance' is contradicted: ABC is the generic discovery work (abstract p. 1; Sec. 5.2 p. 9) and already owns a security-domain case study in CVE-Bench with a 33% absolute overestimation reduction; AgentSuite's headline is the same generic finding at larger scale (5,086 tasks, 18/30 rank shifts).

**Our evidence.**
- The measurable consequence is confined to the admission axis: 6.2%-47.7% of unchanged correct programs are rejected by a legacy import policy, moving the L3 R2-R0 contrast from -0.78 pp to -32.03 pp.
- The attribution axis contributes a specified evidence contract and a bounded mutation test regime, not a prevalence or capability estimate.

*Implication.* The security-specific instantiation is real, but the generic 'flaws distort performance' half is prior work.

**ABC.** The only defensible differences are: (i) our case study is cryptographic and constructive (agent-written attack programs against a declared task contract) rather than web-exploitation state matching; (ii) it integrates a paired contrast and a policy-sensitivity contrast absent from ABC's single-case CVE-Bench narrative; (iii) it adds an attribution layer (E5) with no ABC analogue. All three are incremental and domain-level. A defensible narrowing: 'an integrated cryptographic case study that adds a policy-sensitivity contrast and an attribution layer to the ABC-style audit.'

**AgentSuite.** {'level': 'domain', 'anchors': ["Full text pp.1-20: 'security' 0 hits, 'attack' 0 hits, 'cryptograph' 0 hits", 'Sec. 2.1, p.2: audited benchmarks are tool-calling, conversational and function-calling agent benchmarks (BFCL V3, ACEBench, DrafterBench, tau-bench, tau^2-bench, CFB) - not attack programs', 'Sec. 3.1-3.3, pp.4-5: no execution, no evidence-binding (see C3, C4)'], 'description': 'The security-attack instantiation (cryptographic attack programs, three-way stage separation, provenance-based attribution, six-release documentary audit) is not covered by AgentSuite. The increment for C5 is the integration in this domain, not the discovery that benchmark flaws matter.', 'is_domain_only': True}

**Strongest support.** A cryptographic instantiation that adds an admission-policy axis and an attribution layer to the audit style, measured rather than asserted.

**What would change the verdict.** Drop the contrastive framing. The defensible narrowing is 'a cryptographic case study that adds a policy-sensitivity contrast and an attribution layer to the ABC-style audit'.

