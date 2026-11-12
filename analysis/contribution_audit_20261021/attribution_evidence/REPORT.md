# Attribution evidence audit — 2026-10-21

The retained counts reproduce. They support a constructed demonstration of complementary authenticity and claim-specific binding checks, not a novel provenance mechanism, independent attack prevalence, or superiority to a configured provenance framework. The current discussion has a material contract-mismatch statement about partial-claim false rejects and compresses distinct corpora enough to obscure their independence limits.

## Executed evidence and boundaries

All new files are confined to this directory. No provider calls, candidate generation, frozen runner invocation, manuscript edits, or original artifact writes were performed. No applicable AGENTS.md was found in the repository/ancestor locations. `omo-agent-toolkit ulw-loop status --json` returned `ULW_LOOP_PLAN_MISSING`; there is no active attempt directory. The caller explicitly assigned this output namespace. Memory keyword search supplied no attribution evidence; conclusions below use current files only.

Commands executed from `/mnt/nvme5/ACTS-Attack`:

```
PYTHONDONTWRITEBYTECODE=1 python3 -B sp2027/analysis/contribution_audit_20261021/attribution_evidence/recompute.py > sp2027/analysis/contribution_audit_20261021/attribution_evidence/recompute.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python3 -B sp2027/analysis/contribution_audit_20261021/attribution_evidence/recompute_stage1.py > sp2027/analysis/contribution_audit_20261021/attribution_evidence/stage1.log 2>&1
python3 -B sp2027/analysis/contribution_audit_20261021/attribution_evidence/census.py > sp2027/analysis/contribution_audit_20261021/attribution_evidence/census.log 2>&1
```

| Success criterion / exact scenario | Binary observable | Captured artifact |
|---|---|---|
| Replay every HEB1 dev/heldout, IAR-B dev/heldout, and IAR-C preserved bundle with original validator and adjudicator scripts; 274 bundles ×4 components | 1,096 subprocesses return parseable output and agree with archived decisions/adjudicator fields; zero disagreements | `raw_invocations.json` records command, return code, stdout, stderr, verdict for every invocation; `archive_disagreements.json`; `recompute.log` |
| Preserve replay inputs/code | All 4,666 inventoried input/code files have identical before/after hashes | `input_hashes_before.json`, `input_hashes_after.json`, `input_integrity.json` (`unchanged: true`) |
| Replay Stage1 existing bundles across five evaluator settings with the declared second-evaluation replay case | 135 decisions match archived values; zero disagreements; all Stage1 source/data bytes unchanged; all traversed frozen path/hash entries match | `stage1_replay.json`, `stage1_integrity.json`, `stage1.log` |
| Reconstruct denominators and claims without pooled populations | Separate case/population rows and numerator/denominator fields | `case_ledger.csv`, `case_ledger.json`, `claim_ledger.csv`, `claim_ledger.json`, `recomputed_summary.json` |
| Verify IAR-C calibration relationship and supplementary counts | Calibration and preserved case IDs and complete per-case result rows are identical; in-toto row counts match; HEB1 current freeze hashes match | `supplementary_census.json`, `census.log` |

Stage1 replay reuses the stored bundle `run` expectations, as the original runner does, and verifies existing signatures/joins. It does not independently re-execute producer programs, create new observer records, or establish that the trusted observer's historical assertions were true. The historical Stage01 pair and upstream in-toto executables were not re-executed here: their retained case outcomes were recounted, explicitly distinguished below. The mutation outputs expose aggregate decision censuses, not a retained per-mutant decision table; their aggregate count can be reconstructed, but this audit does not claim a fresh 11,256-evaluation soundness run.

## Census and exact denominators

| Population | Total bundles | Defect/attack denominator | Join-only false promotions | Signature-only false promotions | Combined false promotions | Honest denominator / combined rejects |
|---|---:|---:|---:|---:|---:|---:|
| HEB1 development | 54 | 32 B1–B4b | V2 0/32 | absent | absent | 12 / V2 0 |
| HEB1 heldout | 64 | 36 B1–B5 | V2 0/36 | absent | absent | 12 / V2 0 |
| IAR-B development | 54 | 40 non-H0/H7 | 16/40 | 24/40 | 0/40 | 14 / 0 |
| IAR-B heldout | 58 | 44 non-H0/H7 | 16/44 | 28/44 | 0/44 | 14 / 0 |
| IAR-C preserved | 44 | 28 S4–S12,S14,S15 | 10/28 | 14/28 | 0/28 | 16 / 0 |

HEB1 V0 schema/declaration and V1 hash baselines promote 32/32 development defects and 36/36 heldout defects. HEB1 does not contain an authenticated baseline. Both baselines and V2 lack signature authentication. For heldout, 36 defects plus 8 B0 coherent and 20 C-family controls make 64. C4 adds four unsupported level-6 emissions outside the 36-defect headline denominator: V0/V1 have 40/64 false level-6 promotions over the entire heldout corpus. HEB1's 36/36 is not the full corpus acceptance rate.

IAR-B's 44 heldout negative-family cases include eight malformed H8 cases. IAR-C's 28 attack cases include eight malformed S15 cases. These are designed bundle cases, often paired over two primitives, not independent empirical attacks. All three systems reject those eight malformed cases in IAR-C. No confidence interval from these curated cases establishes population prevalence.

IAR-C V2 promotions occur in S7,S9,S10,S11,S12 (two each); V3-sig promotions occur in S4,S5,S6,S7,S8,S11,S14 (two each). Thus some failures overlap (S7/S11); this is not a clean factorial intervention in which authentication is the only implementation change. V2 and V3 also differ in their supported claim contracts and individual joins.

The 14/16 V2 rejections are numerically correct but misleading as comparative false rejects: the denominator contains two full-attribution S1 cases and fourteen honest lower-level cases (S2/S3 and ten S13). V2 accepts both S1 and rejects all fourteen lower-level requests because its contract only emits complete attribution. V3-full accepts all sixteen at the supported rung. Report lower-claim support as a functionality difference; compare full-attribution false promotion on a common requested-claim contract.

## Independence, leakage, and post-hoc choices

1. HEB1 heldout generation imports the frozen development constructors. It changes parameters/opaque IDs and adds six B5 split-session cases targeting a join J2 already present in V2. This tests another composition against a frozen validator, not independent task/domain generalization. Labels/private truth are not passed to validators by the replay; public case input and trust anchor arguments are recorded verbatim. This does not establish blindness of the person designing fixtures.
2. IAR-B heldout uses the same generator family and frozen evaluator, with H10 reference-replay cases added. Its 58 bundles and 44 negative-family cases must not be confused with IAR-C's 44 bundles and 28 attacks.
3. IAR-C has separately written generator/adjudicator modules and no imports of IAR-B fixtures or validators; it shares `eb_crypto`, wire format, claim ladder, known scenario dimensions, and same-author construction. More decisively, calibration `iar_c/runs/20261019_121420/results.json` and preserved `121621/results.json` contain exactly the same 44 IDs and identical complete `per_case` rows. The preserved evaluation is not an untouched heldout test. It is a preserved replay following observed calibration. This proves exposure/reuse, not undisclosed retuning or malicious label leakage.
4. Original TOEEA-1 Stage1 is a different 27-bundle experiment. Its protocol illustrative 14/13 crypto-positive/negative split is actually 21/6 in the frozen cases. The preregistered crypto-ground-truth metric yields full strict FA 0/6 and FR 19/21. Those 'FR' entries mostly reject cryptographically true but wrongly attributed bundles. A post-hoc attribution metric (D-06) yields FA 0/25 and FR 0/2. Preserve both and label the attribution metric post-hoc.
5. TOEEA-1 strict vs lenient is a policy choice. Against its own expected lenient decisions, full_lenient gives FA 0/24 and FR 0/3; the historical summary's 1/25 compares lenient outcomes to strict truth. Historical Stage01 has 13 applicable analogues, two true successes and eleven non-successes; its two accepted mismatches are 2/11 applicable non-successes, not the summary's 2/25 denominator containing fourteen N/A cases. These are historical report issues, not claims found in the inspected current manuscript.
6. Stage1 D-07 states that the exploratory raw run/code was overwritten by the confirmatory path; the heading reverses the overwrite direction, while its body explains the current state. The exploratory record is a transcribed table, not reproducible raw execution evidence. Current frozen Stage1 path/hash checks match, which does not reconstruct that lost pre-freeze state.

## Current manuscript wording

Inspected current files: `sp2027/paper/capability_revision_20261020/main_sections/09_audit.tex`, `main_sections/10_discussion.tex`, `supp_sections/S27c_attribution_compact.tex`. No manuscript file was changed.

The HEB1 paragraph in `10_discussion.tex` needs these corrections:

- Replace “composition-blind and authenticity-blind baselines” with the actual HEB1 systems, “schema/declaration and hash-integrity baselines.” The current phrasing suggests that authentication is the controlled contrast in HEB1 when none of its three systems authenticates records.
- Name IAR-C (44 total, 28 attack cases) and IAR-B heldout (58 total, 44 negative-family cases) explicitly. “Preserved set and ... held out” should not imply that one test was split into these denominators or that IAR-C was untouched before preservation.
- Remove comparative “false-rejected 14/16 honest partial claims.” Correct wording: “V2, which emits only full attribution, rejected the fourteen lower-level requests; V3-full supported all sixteen honest requests, including two full-attribution cases.”
- “Adversarial 2×2 comparison” should be qualified as a comparison of implemented authenticity/binding design classes, not an otherwise-identical factorial ablation.

Suggested replacement, retaining only reproduced evidence:

> On 36 constructed HEB1 heldout defect bundles, schema/declaration and hash-integrity baselines emitted unsupported full attribution in all cases; the join validator emitted none. In IAR-C's preserved corpus, join-only, signature-only, and combined checks promoted 10/28, 14/28, and 0/28 attack-family cases. IAR-C used a separately written generator and adjudicator but had already evaluated the same cases during calibration. On the separate IAR-B heldout corpus the corresponding counts were 16/44, 28/44, and 0/44. The combined validator accepted all sixteen honest IAR-C requests at their supported claim level. V2's rejection of fourteen lower-level requests reflects its full-attribution-only contract. These constructed cases demonstrate complementary authenticity and claim-specific consistency requirements under the stated trust model.

`09_audit.tex` and S27c already correctly call 11,256 bounded mechanized evaluations rather than proof, and configured in-toto agreement an implementation/policy result rather than superiority. Retain those limitations. S27c's “fresh aggregator ... check is harder” is narrower than a universal ordering: empty state removes replay rejection, but the per-mutant checker does not test multi-submission durable replay/concurrency behavior. Prefer “each mutant is evaluated with an empty replay ledger; this does not test cross-submission replay-state correctness.” The current 19-operator/1,407-mutant statement was source-inspected and aggregate-recounted, not freshly executed by this audit.

## What the evidence adds, and what remains assumed

Authenticity is required against the tested record rewriting/unauthorized signer cases; signatures alone cannot establish that authentic records concern the claimed candidate, target, condition, or execution. Claim-specific joins are required against the tested authentic splice/replay/overclaim cases. Their combination is sufficient for these curated cases under their adjudicators, not a universal necessity/sufficiency theorem. The partial-claim ladder preserves useful limited claims; V2's design does not provide a fair lower-claim comparator.

The bounded trust assumptions include truthful/non-compromised observers and reference signers, protected trusted anchors and role policy, correct statement semantics, correct independent target predicate, canonical signature verification, and a replay policy appropriate to the consumer. A valid signature authenticates a statement's issuer, not the underlying execution's truth. Original TOEEA-1 further documents a pre/post program-hash TOCTOU window, no namespace isolation, in-memory replay state, and local key custody. These limitations are not inherited blindly by later v2 observers; the populations and implementations are distinct.

The original HEB1/IAR-A operational boundary is synthetic composition; inspected historical runners issue their own certificates internally. A real component accepting assembled evidence is an acceptance-logic counterexample, not demonstrated external attacker ingress into the campaign. Later loopback/own-target experiments are separately scoped constructed reachability evidence, not a reason to retroactively relabel HEB1 or IAR-C as deployed attacks. This audit did not rerun their targets.

Recounted Stage6 upstream rows show default in-toto 16/16 false promotion, stateless independent policy 1/16 and 21/22 agreement, stateful independent policy 0/16 and 22/22 agreement, and no false rejection among six positive cases. The delegated ACTS integration is also 21/22. SLSA rows stop at acquisition (20) or timeout (2); 6/6 arithmetic nonacceptance of positive cases is not a meaningful policy-quality comparison. The inspection source independently implements the same chosen policy and uses a frozen predicate; that demonstrates configurable expressiveness and implementation agreement. It supplies no advantage beyond a properly specified provenance configuration.

The four soundness aggregate files each recount to 2,814 mutant-semantic evaluations (1,407 mutants × two semantics), totaling 11,256. All use seed 20261020, 22 base cases, deterministic operators and shared contract infrastructure. This is neither 11,256 unique independent attacks nor formal proof. The accepted mutation classes are claims-block changes; both evaluator and property checker live in `contract.py` and share signature/policy machinery, so common-mode omissions remain possible. The retained attempt directories disclose correction/selection history; a final zero alone cannot establish an independent oracle or pre-registration of every repaired detail.

Allowed contribution: a reproducible corpus and operational specification of what execution-attribution claims require, with observable counterexamples to under-bound policies and a configured cross-implementation agreement check. Not established: new cryptographic/provenance mechanism, AI-specific attribution failure, transfer to independent benchmarks, prevalence, arbitrary-host soundness, compromised-trust robustness, or superiority over in-toto/SLSA. H1-R3 capability, E5 acquisition, V4 observations, release-audit cells, and these attribution bundles remain separate populations with no pooled numerator or denominator.
