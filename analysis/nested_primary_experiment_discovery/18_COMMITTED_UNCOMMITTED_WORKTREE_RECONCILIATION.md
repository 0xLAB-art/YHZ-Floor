# Committed, uncommitted, and ignored worktree reconciliation

Audit date: 2026-10-15. This is a read-only reconciliation of the live nested checkout. No worktree state was restored, deleted, staged, or executed.

## Nested Git state

The nested checkout is `/mnt/nvme5/ACTS-Attack/ACTS-ATTACK`. Its live status contains 232 tracked paths with status changes, 99 nonignored untracked paths, and 133 ignored paths. The 232 tracked changes were checked against the nested `HEAD` using Git blob hashes:

| category | paths | interpretation |
|---|---:|---|
| tracked paths with status changes | 232 | includes mode changes and one content change |
| content-identical to `HEAD` | 231 | mode-only `100644` to `100755` changes; scientific bytes unchanged |
| content-different from `HEAD` | 1 | `README.md` only |
| nonignored untracked | 99 | includes the V3 sessions, V4 wrappers, and one untracked data result |
| ignored | 133 | includes the V2 session copies, campaign logs, caches, and ignored target/cache material |

`README.md` is a documentation revision, not an experimental observation. Its current text changes the displayed ASR, scope, target count, and experiment count; those claims were not used as measurements. The tracked data/results/harness bytes are Git-content-identical to `HEAD` despite the mode-only status changes.

## V2/V3 session population

The ignored `harness/v2/results/e2/_loop_out/` and nonignored `harness/v3/results/e2/_loop_out/` directories each contain exactly 74 JSONL session files. Every same-named V2/V3 pair has the same SHA-256. Across one deduplicated population:

- 341 JSONL event records;
- 42 session-end records with `verdict=success` and `match=true`;
- 2 terminal errors;
- 12 `no CLAIM` outcomes;
- 3 unresolved terminal records;
- 15 provider/gateway-unavailable outcomes.

The 42 accepted results span RC4 keystream, ChaCha20 nonce repeat, crypto misuse, and parsing-overflow conditions. The retained successful rows include, for example, 10/10 Qwen RC4 sessions, 7/10 NVIDIA Nemotron-3.5 RC4 sessions, 4/5 Qwen ChaCha20 sessions, 4/4 NVIDIA Nemotron-3-super parsing-overflow sessions, and 3/3 NVIDIA Nemotron-3-super crypto-misuse sessions. These are session-level observations with an oracle-owned `match=true` field; they are not independent V2/V3 replications and are not a clean model capability denominator because failures include provider, parser, and no-claim states.

Representative raw paths:

- `harness/v2/results/e2/_loop_out/agent_session_qwen_qwen3.8-27b:free_RC4_Keystream_rep1.jsonl` (ignored copy);
- `harness/v3/results/e2/_loop_out/agent_session_qwen_qwen3.8-27b:free_RC4_Keystream_rep1.jsonl` (untracked copy);
- `harness/v3/results/e2/_loop_out/agent_session_nvidia_nemotron-3-super-120b-a12b:free_PARSING_OVERFLOW_rep1.jsonl`;
- `harness/v3/results/e2/_loop_out/agent_session_nvidia_nemotron-3.5-lightning:free_RC4_Keystream_rep1.jsonl`.

The event records expose more than final labels: attempt number, raw action/run events, claim payloads, reserved expected SHA-256, oracle operation span, container image digest, timestamps, and provider errors. They therefore support bounded verification of the retained session claims, but not independent source-to-run reconstruction for every session.

## V4 and other untracked surfaces

`harness/v4/` is nonignored and contains only three wrapper/source files totaling 1,353 bytes:

- `harness/v4/acts_audit_v4.py`;
- `harness/v4/record_builder.py`;
- `harness/v4/run_agent_operations_v4.py`.

It contains no retained result/session files. It changes the audit tolerance/wrapper lineage and delegates to V3 code; it is a configuration/provenance surface, not a completed experimental family.

`data/c2t1_toolchain_diversity_repro.json` is nonignored and untracked. Its content hash is identical to the retained historical C2-T1 record, so it is a current-worktree duplicate, not an independent repetition.

## Ignored campaign logs

The ignored files `harness/rerun/agent_campaign.log`, `agent_campaign_free*.log`, and `agent_campaign_v5_*.log` are human-readable campaign summaries. They contain additional model/condition status lines, including the historical `agent_campaign.log` summary of 8/18 RC4 successes across the listed model rows and 2/15 ChaCha successes in the mixed summary. They do not contain complete per-session oracle records and conflict in scope/denominator with the V2/V3 JSONL population. They are therefore classified as `HISTORICAL_LIMITED` summary evidence, not merged into the 74-session population.

## Scientific conclusion

This reconciliation closes the specific blind spot around committed, uncommitted, and ignored nested files. The important result missed by a tracked-only crawl is the 74-session V2/V3 population and its exact 42 accepted oracle-backed session claims. The correct deduplicated conclusion is **74 retained sessions, 42 accepted session verdicts, and 32 non-accepted/uncertain terminal states**, with V2/V3 as byte-identical copies. V4 adds no completed result. The current nested checkout is fully file-inventoried, but the project-wide evidence status remains `PARTIAL DISCOVERY — NAMED EVIDENCE GAPS` because outer historical trees, sealed payloads, and archive/source-linkage limitations remain.
