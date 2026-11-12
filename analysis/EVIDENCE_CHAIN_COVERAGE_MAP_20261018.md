# Evidence-chain coverage map and canonical claim matrix — 2026-10-18

The unit of analysis is an evidence-supported stage of a specified attack claim. Rows are intentionally not composable into one synthetic end-to-end run unless the same run ID and contract provide every stage.

| Claim ID | Stage / claim | Canonical run IDs or records | Verification authority | Tier | What is established | What remains unproven / forbidden inference |
|---|---|---|---|---|---|---|
| EC-01 | Opportunity specified | EXP-034 task cards; explicit-observation public-input manifests; E5 card | frozen task/card manifests | R/V by family | weakness, input contract, and success predicate were stated for each fixture | does not prove exploitability or agent understanding |
| EC-02 | Agent constructs executable artifact | EXP-034 12 session records; 18 explicit-observation event namespaces; adaptive attempt 6/7 successful run records | retained generated programs and run/event identity | V for named runs | model-authored code reached target invocation in the cited runs | hosted weights, complete acquisition path, and transfer beyond contract are not proven |
| EC-03 | Target predicate executes | V4 task-specific invocations; explicit-code candidates; adaptive separate-process targets; held-out attempt 4 cells | target process plus run-local oracle | V | candidate was submitted to the declared target/oracle | syntax-only or wire-only records (e.g. C2-T1) do not satisfy this stage |
| EC-04 | Independent acceptance | V4 8 accepted sessions; explicit 18 accepted events; adaptive 8/39 query successes; held-out 4/4 attempt 4; composition 1/1 | independent task/capability oracle | V | declared predicate accepted the candidate under the local fixture | acceptance does not prove acquisition, deployment risk, or model identity |
| EC-05 | Revisions / effort | V4 31 submitted programs, CBC query counts, adaptive 8/39 queries, E5 8,714 relays | retained event/request/escrow ledgers where available | R/V | the cited workload or revisions were recorded for the cited run | not a comparable cross-family effort ranking; bounded tails are not total work |
| EC-06 | Failure localization | V4 4 oracle failures; initial ECDSA schema-defect runs; adaptive failed replicate; provider-unavailable and blocked attempts | terminal records and failure-stage artifacts | V/R | failures can be separated into oracle, interface, provider, timeout, and integrity classes | failure class is not automatically cryptanalytic incapacity |
| EC-07 | Task-specific target mechanism | fixed executor 12/12; C2b 45 handshakes; C2-T1 3 wire-valid edits; A1/D1/E3 local targets | local target/oracle or measurement controls | V/R | specified local relations/policies/measurements were reproduced at their stated scope | no primitive break, on-path downgrade, stock-AES generalization, or cross-host law |
| EC-08 | Information contract boundary | H1 V2 0/35 candidate-bearing recovery, 0/20 XOR masks, 30/30 instructed abstentions; reduced arm RC4/ECDSA 2/2, ChaCha20 0/2 | scorer controls and retained response records | R/V | output/interface/knowledge conditions change the admissible interpretation | unmatched information, parser, feedback, and model conditions do not identify a causal effect |
| EC-09 | Attribution/provenance | E1 0/54 strict H1; EXP-034 0/12 immutable environment; E5 verifier hash mismatch and host execution; V4 0/8 recomputable timing endpoints | provenance matrices, source hashes, escrow logs, clock ledger | R/V* | accepted outcomes can coexist with incomplete provenance and measurement reconstruction | no claim of false candidate, secret isolation, immutable model identity, or independent timing recomputation |
| EC-10 | Replication / transfer | explicit 6/6 per family and 18/18 total; held-out attempt 4 2/2 dev + 2/2 held-out | distinct namespace/run IDs, integrity manifest | V (bounded) | family-specific reproducibility and held-out fixture success | not V4 replication, pooled capability rate, feedback causality, or cross-family generalization |
| EC-11 | Cross-family synthesis | selected evidence rows EC-01–EC-10 | analytical framework only | R | stages can be compared by claim type and boundary, not merged by denominator | no synthetic causal chain or universal attack-success law |

## Canonical stage transitions

1. **Specified opportunity → constructed artifact:** supported for V4 and explicit code lanes when generated artifacts and run IDs are retained.
2. **Constructed artifact → target execution:** supported only where a target invocation and target-specific oracle record exist; C2-T1 remains a partial wire-edit stage.
3. **Target execution → accepted outcome:** supported by the V4 8/12 cohort, explicit 18/18 lanes, adaptive accepted runs, attempt-4 held-out cells, and composition 1/1 under their own contracts.
4. **Accepted outcome → effort characterization:** supported only by the retained interval/request/event fields for the cited run; not by cross-family comparisons.
5. **Accepted outcome → agent attribution:** blocked where immutable model identity, host isolation, or complete provenance is absent; E5 and V4 timing illustrate this boundary.
6. **Separate families → scientific synthesis:** permitted as a claim-relative comparison of evidence stages and limitations, not as an exchangeable pooled population.

## Overlap and duplicate policy

- V2/V3 copies and migrated historical records are one physical observation unless a separate execution record exists.
- The 31 V4 programs are submissions nested in 12 sessions, not 31 sessions.
- The 18 explicit-observation successes are 18 physical run IDs in three six-run family namespaces; they are not duplicates of V4.
- Attempt-3 held-out records are retained for integrity analysis but excluded from the clean 4/4 claim.
- Adaptive attempt-6 and attempt-7 records are retained separately; the paper reports accepted run outcomes and the failed replicate, not a probability estimate.
- Beyond Attack Success contributes verification/provenance analysis only; it does not add an independent attack numerator.