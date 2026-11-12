# Reproducibility Package — ACTS-Attack — 2026-10-18

**Deliverable #5 of the ACTS-Attack completion program.**
**Purpose:** everything a third party needs to (a) verify the integrity of every cited artifact, (b) re-derive every reported number from retained records without provider calls, and (c) re-execute the provider-route experiments where a route is available — with explicit statements of what cannot be reproduced and why.

---

## 1. Verify first (no provider calls needed)

Run these five checks in order; they require only the repository and Python 3.

```bash
# 1. Protected artifacts (must match exactly; any drift invalidates this package)
sha256sum sp2027/analysis/RESULTS_LOCK.json          # 4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39
sha256sum sp2027/analysis/RESULTS_LOCK_H1PC.json     # 8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103
sha256sum sp2027/paper/main.tex                      # 51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461
sha256sum sp2027/paper/main.pdf                      # fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a

# 2. New 2x2 lane: manifest + final freeze
cd sp2027/research_execution/info_contract_2x2_20261018
sha256sum -c hashes/all_artifacts.sha256             # 152/152 OK
sha256sum hashes/all_artifacts.sha256                # 7c9cf717769674c73462e0caedd41e25bfa8351551da5985ca03dfc81350dc76
# FINAL_FREEZE.json records the manifest hash, the earlier 150-entry snapshot
# (68945c20f4f98e590acf2db88c3726f1e8edcd44d945ba9925f2f7db0e10f0c5) and the coverage rule.

# 3. Candidate-identity resolution (surrogate attempt 3)
cd sp2027/analysis/postfreeze_integrity_resolution_20261018
sha256sum -c SHA256SUMS
python3 evidence/extract_candidate.py <attempt3>/surrogate/direct_generator_transcript.jsonl   # prints a5e8ed51...
python3 evidence/replay_candidate.py                 # full_match TRUE; claim sha 919ca521... == run_result.json candidate_sha256

# 4. Corpus-wide integrity sweep v2
cd sp2027/analysis/postfreeze_integrity_resolution_20261018/evidence
python3 integrity_sweep_v2.py                        # regenerates integrity_sweep_v2.json (~733 entries, 69 manifests)

# 5. 2x2 leak scan re-derivation (reads retained artifacts only)
cd sp2027/research_execution
python3 leakscan_info_contract_2x2.py                # rewrites LEAK_SCAN.json / STATUS; re-run inside a copy if the frozen tree must stay byte-frozen
```

## 2. Re-deriving reported numbers without provider calls

| Result | Re-derivation source |
|---|---|
| V4 8/12 and per-family split; 31 programs | `sp2027/agent-eval/R1_CLEAN_COHORT_V4_RESULTS.md`, `R1_CLEAN_COHORT_V4_ROW_LEDGER.csv`, `R1_CLEAN_COHORT_V4_MANIFEST.json` |
| Explicit-observation 18/18 and 52 physical run IDs | `sp2027/analysis/canonical_run_audit_20261018.json` (event-file hashes + run-ID extraction) |
| H1 V2 51/60 / 0/35 / 0/20 / 30/30 | `sp2027/research_execution/H1_V2_FAILURE_STAGE_SUMMARY.json` + `H1_V2_FAILURE_STAGE_MATRIX.csv` |
| XOR defect 10/10 + 10/10, retrospective 0/20 | XOR control records (postfreeze root) + coverage audit row B2 |
| Adaptive 8 and 39 queries, failed replicate | `adaptive_discovery_20261017_attempt6/`, `attempt7/` run records |
| Held-out attempt4 4/4 + leak audit | `heldout_generalization_20261017_attempt4/{records.json, VRE.json, leak_audit.json, manifest.json}` |
| Composition 1/1, oracle_queries=1 | `compositional_20261017_attempt2/` records |
| Surrogate 9,640 vs 20,480 | dossier replay (§1.3) + effort3 records |
| E5 1/14 / R30 / 8,714 calls | `sp2027/agent-eval/runs_e5` escrow + relay ledgers |
| C2b 45/45; C2-T1 3/3 wire-only; D1 2/16 vs 16/16 | C2/C2b/C2-T1/D1 records (coverage audit §D) |
| E3 −1.695593 ms, CI, p≈8.9e-34; E1 0/54, kappa 0.784; E4 10/47 vs 10/19; E6 0.594/0.418 | `sp2027/analysis/e3_*`, E1/E4/E6 records |
| 2×2 all numbers (cells, marginals, Fisher, submissions, failure stages, falsifiers) | `info_contract_2x2_20261018/{ANALYSIS.json, results.jsonl, events.jsonl, summary.json}`; `python3 ../analysis_info_contract_2x2.py` re-derives ANALYSIS.json |
| Population/denominator rules | `sp2027/analysis/CANONICAL_RUN_AUDIT_20261018.md`; `EVIDENCE_CHAIN_COVERAGE_MAP_20261018.md` |

## 3. Re-executing the provider-route experiments

**Environment:** Python 3.12.3 (stdlib only for the runners; no third-party crypto imports — fixtures build bytes with `hashlib`-adjacent helpers and deterministic keystreams). Provider adapter: `sp2027/analysis/checkpoint007_active_experiments/runs_009/provider_adapter.py` (`ClaudeProvider`), POST `{endpoint}/v1/messages`, headers `x-api-key` + `Authorization: Bearer`, `anthropic-version: 2023-06-01`, no temperature in payload (provider default); errors classed TIMEOUT / PROVIDER_UNAVAILABLE / MALFORMED_PROVIDER_JSON / HTTP_ERROR / EMPTY_RESPONSE / INCOMPLETE_RESPONSE.

**Routes:** the 2×2 lane used `https://api.apmix.ai/v1/messages` with model label `claude-sonnet-4-6-free` and the key at `~/.config/acts007/apmix.key` (never logged; `--` do not paste the key into any artifact). The 2×2 cost $0 (free model tier); no paid fallback is authorized anywhere in this program ($50 alert / $200 hard stop). Historical logged spend before this lane: $0.357648 estimated (synthesis §8).

### 3.1 The 2×2 lane (full pipeline)

```bash
cd sp2027/research_execution
python3 preflight_info_contract_2x2.py     # local solver, oracle accept/reject, cell-text audit, wire probe, attest
ACTS_SEEDS=41,42,43,44 python3 run_info_contract_2x2_chacha20.py   # 16 sessions, <=32 calls, cost $0
python3 analysis_info_contract_2x2.py      # -> ANALYSIS.json
python3 leakscan_info_contract_2x2.py      # -> LEAK_SCAN.json, STATUS_INFO_CONTRACT.json, hashes/all_artifacts.sha256
```

**Warning:** the runner writes into the fixed `info_contract_2x2_20261018/` directory. To re-execute without touching the frozen record, copy the runner to a scratch directory and change `OUT`, or copy the whole experiment directory first. A rerun produces a **new** observation set, which must be versioned separately and must not be pooled with the frozen one.

Expected: C1 4/4 (4 submissions), C2 4/4 (6), C3 4/4 (4), C4 0/4 (8); 0 provider failures. Per-cell n=4 means only large effects are recoverable; exact statistics recompute deterministically via `analysis_info_contract_2x2.py` (Fisher one-sided 0.03846, two-sided 0.07692 on R+/R−; naming marginal 1.0).

### 3.2 Fixture and oracle reuse (verbatim lineage)

- Fixture/oracle/feedback/policy: `run_code_feedback_chacha20.py` (`instance()`, `oracle()`) — the P009 protocol, reused verbatim; C1's prompt reproduced the historical default byte-for-byte (verified in `preflight/cell_text_audit.json`).
- Action extraction + policy: `run_code_feedback_exploration.py` (`extract_action`, `policy_check`).
- Oracle predicate: candidate JSON at `plaintext2_hex` must equal hex(P1) exactly. Oracle never inspects the candidate by name; acceptance is exact-match only.

### 3.3 Held-out fixture re-execution (attempt 4 pattern)

`heldout_generalization_20261017_attempt4/src/run_experiment.py` regenerates the two secrets into `truth_material/`, runs the four cells, and `src/independent_oracle.py` adjudicates; the integrity gate is the leak audit (`leak_audit.json`, pre/post-send checks) plus the secret-hash conventions in §4. Re-execution must generate **fresh** secrets and will not replicate the frozen values (only the procedure reproduces).

### 3.4 Surrogate arm

`surrogate_conversion_20261017_attempt3/surrogate/run_surrogate.py` executes a candidate against the local oracle; the hash conventions for `candidate_sha256` (claim-object hash) are documented in the dossier Part 1. For verification use only `evidence/executed_candidate_reconstructed.py`; the archived on-disk `generated_agent.py` is not the executed program.

## 4. Hash conventions and manifest rules (critical for verification)

1. **Byte-hash vs value-hash:** attempt4 secret manifests record `sha256(value.strip())` over the 8-char value (9-byte file with trailing newline). Raw file-byte hashes differ (`bc68bb03…` / `b1fcbbd5…`). The oracle compares stripped values and its `expected_value_hash` uses the value-hash convention.
2. **Claim-object hash:** `run_result.json:candidate_sha256` in the surrogate arm is `sha256(json.dumps(claim, sort_keys=True))`, **not** the candidate source hash. The source hash of the executed candidate is `a5e8ed51…` via `extract_candidate.py` (fenced body, `CODE_BEGIN/CODE_END`, fences stripped).
3. **Manifest base:** an entry resolves relative to the parent of the manifest's `hashes/` directory, else the manifest's own directory; absolute entries as-is; hardlink duplicates deduped.
4. **Snapshot ordering:** manifests may predate finalizer appends (attempt4 `manifest.json` `ba52ba8c…` → `1f1f811a…` by removing three finalizer fields) and self-hash lines may go stale on regeneration (retry1, compositional). These are documented, not defects.
5. **Coverage rule (2×2):** `hashes/all_artifacts.sha256` covers every regular file except `hashes/` and `FINAL_FREEZE.json` (self-referential metadata).

## 5. Protected artifacts

| Artifact | SHA-256 | Rule |
|---|---|---|
| `sp2027/analysis/RESULTS_LOCK.json` | `4b152f18…9e39` | never modify |
| `sp2027/analysis/RESULTS_LOCK_H1PC.json` | `8221cb86…5103` | never modify |
| `sp2027/paper/main.tex` | `51f97748…e461` | never modify |
| `sp2027/paper/main.pdf` | `fd9a5889…887a` | never modify |

All four verified intact at the end of this program (`AGENT_PILOT_PREFLIGHT_AUDIT.json` records the same expected digests).

## 6. Known non-reproducible items (stated, not repaired)

| Item | Why not reproducible |
|---|---|
| Hosted model weights identity | Provider-attested labels only; no immutable image digest for hosted arms |
| V4 raw timing endpoint pairs (0/8) | Monotonic endpoint pairs were not retained; elapsed durations are recorded evidence only |
| WebSP paper-result joins | External source records absent at paper time; absence reported, not inferred |
| Cybench output-payload / producing-run linkage | Same class: externally limited |
| E5 enforced acquisition | Requires authenticated, role-separated interfaces + launch-policy evidence; current records are host-executed with unauthenticated handlers |
| W3/W4 populations | Identity defects / identity-invalid corpus (excluded by rule) |
| Frozen truth values in held-out fixtures | Fresh secrets are generated per execution by design; only the procedure reproduces |
| Provider transport behavior (latencies, exact wire bytes) | Provider-side; raw bodies retained per response where captured |

## 7. Budget and route accounting

- Authorized route only: free `claude-sonnet-4-6-free` via `https://api.apmix.ai/v1/`; the 2×2 lane added **$0** marginal spend. No paid fallback was used at any point in this program.
- Historical logged program spend before this lane: **$0.357648** estimated (synthesis §8; `BUDGET_LEDGER.jsonl`). This program added no billable calls.
- Guardrails that were in force: $50 alert, $200 hard stop.

## 8. Package quick index

| Section of record | Primary location |
|---|---|
| Deliverables #1–#6 | `sp2027/analysis/COMPLETE_EXPERIMENT_COVERAGE_AUDIT_20261018.md` + `sp2027/analysis/final_deliverables_20261018/` |
| Canonical populations & admissibility rules | `sp2027/analysis/CANONICAL_RUN_AUDIT_20261018.md` |
| Evidence-chain matrix EC-01…EC-11 | `sp2027/analysis/EVIDENCE_CHAIN_COVERAGE_MAP_20261018.md` |
| Integrity dossier + sweep v2 + candidate resolution | `sp2027/analysis/postfreeze_integrity_resolution_20261018/` |
| New 2×2 lane (frozen) | `sp2027/research_execution/info_contract_2x2_20261018/` |
| Synthesis (RQs, §11 decisions, §12 gaps) | `sp2027/research_execution/ACTS_ATTACK_FINAL_SCIENTIFIC_SYNTHESIS.md` |
| Postfreeze corpus roots | `/tmp/opencode/novelty_program/` (repo mirror under `sp2027/paper/capability_merge_20261016/artifact_documentation/novelty_program_20261017/`) |

**Bottom line:** every reported number re-derives from retained artifacts without provider calls; the single new provider lane (2×2) is preregistered, leak-scanned, hash-frozen, and re-executable at $0 on the authorized free route; and every irreproducible element is named with its reason instead of being papered over.
