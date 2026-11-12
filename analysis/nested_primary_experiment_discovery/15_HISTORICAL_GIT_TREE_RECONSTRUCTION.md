# Historical Git-tree reconstruction: `DEPOSIT_V1.1_STAGING`

## Finding

The live outer filesystem is not the complete retained project surface. Reachable outer-Git history contains a historical tree, `DEPOSIT_V1.1_STAGING/`, whose paths are absent from the current filesystem. This is the largest missed historical experiment surface found in the closure pass.

- historical object paths absent from the live filesystem: **674** (467 blobs, 202 trees, 5 tags)
- retained historical blob bytes represented by the selected path inventory: **30,138,774 bytes**
- `DEPOSIT_V1.1_STAGING` selected historical object paths: **432** (**267 blobs**, **165 trees**); blob payload bytes: **13,824,435 bytes**
- source is reachable outer-Git history, not a synthetic reconstruction and not a README inference
- the historical tree is not copied into the working tree; raw evidence remains unchanged

The historical tree includes `data/`, `harness/`, `results/`, `results_rerun/`, C2b traces, escrow logs, agent-loop JSONL/transcripts, and full E5 session material. It therefore directly addresses the user's warning that completed benchmark work was split between committed and non-current material.

## Parsing and provenance

The selected historical `DEPOSIT_V1.1_STAGING` blobs were streamed with `git cat-file`; JSON and JSONL were parsed without executing repository code. The reconstructed historical blob set contained 45 valid JSON files and 56,635 valid JSONL records, with zero parse errors in that selected tree. This is a structured read, not a claim that every byte of every large text/log member was manually reviewed.

The tree is reachable from the outer Git history. The data-result blobs have stable object IDs and historical paths:

| Historical path | Git blob | bytes |
|---|---|---:|
| `DEPOSIT_V1.1_STAGING/data/A1_openssl_timing.json` | `1f7ec23a1ff0ddafd312cd0eaf7d0788f3801834` | 3,111 |
| `DEPOSIT_V1.1_STAGING/data/A1_vmware_timing.json` | `8ec24583446e529b386b49c0e5fcbd9e766770ae` | 1,523 |
| `DEPOSIT_V1.1_STAGING/data/B1_revised.json` | `49fc958979fec4c6242eb0f2b96cbbe7ad5fb1b3` | 52,923 |
| `DEPOSIT_V1.1_STAGING/data/C2_pqc_generality.json` | `5b44b82555095d56413fe350c9536a97f7c4c0f8` | 4,380 |
| `DEPOSIT_V1.1_STAGING/data/c2b_hybrid_required_control.json` | `10ccca3b247038edc2ed303ead98b72cc29fa425` | 31,262 |
| `DEPOSIT_V1.1_STAGING/data/c2t1_open_source_reproduction.json` | `fce9c918672cd14bbd930f786640c64005537667` | 3,753 |
| `DEPOSIT_V1.1_STAGING/data/cv7_spread_result.json` | `495c7e5bbf910fdf0203a814d1d47ffab2ccf297` | 285 |
| `DEPOSIT_V1.1_STAGING/data/full_key_recovery.json` | `77e7f4379287c65b68f99676828413b2199a33a2` | 4,945 |

## Recovered result inventory

### A1: environment-sensitive AES timing

`A1_openssl_timing.json` records OpenSSL 1.0.1e T-table timing in WSL2. It retained 90,000 valid samples, best timing ratio 0.1641, z-score 1.9107, TTE 1,380 s, and ASR 0. The record explicitly concludes that 3-sigma confirmation was not achieved because virtualized jitter dominated the expected signal.

`A1_vmware_timing.json` records a separate OpenSSL 1.0.2u VMware run with 100,000 samples per key and 90,000 valid trimmed observations. It reports low/high means 197.57/183.64 ns, mean delta -13.9305 ns, pooled standard deviation 25.99 ns, SEM 0.1225 ns, z=113.6987, TTE=0.1 s, and ASR=1. The record's bounded result is a strong environment/configuration contrast; it does not by itself establish causal portability or bare-metal generality.

### B1: timing-oracle safety evaluation

`B1_revised.json` contains L1–L5 responses for four model configurations: Gemma4-aligned, Qwen3.5-plus, Llama4-Scout-sub, and GLM-5.1. The retained summary reports:

- Gemma4-aligned: L-threshold `L5+`, SRR L1–L5 `0.0`;
- Qwen3.5-plus: L-threshold `L4`, SRR `0.4`;
- Llama4-Scout-sub: L-threshold `L5+`, SRR `0.0`;
- GLM-5.1: L-threshold `L3`, SRR `0.4`.

The record is a model-response/behavioral evaluation, not a cryptographic side-channel measurement and not an independent safety ground truth. The exact prompts, response lengths, refusal flags, and meta-detection fields remain in the retained blob.

### C2: hybrid-PQC generality

`C2_pqc_generality.json` records four tested targets, all with ASR=1, 6 modified bytes, mean TTE 0.022 s, and classical-only server acceptance: X25519MLKEM768, SecP256r1MLKEM768, SecP384r1MLKEM1024, and a cross-curve downgrade. It reports 4/4 targets succeeded and marks generalisation confirmed. X448MLKEM1024 and HQC-128 were unavailable in the recorded OpenSSL/provider configuration. The strongest defensible claim is four recorded local target demonstrations; “all hybrid KEM deployments” is stronger than the target coverage supports.

### C2b: causal server-policy control

`c2b_hybrid_required_control.json` records 45 handshakes in 9 cells, five repetitions per cell, with zero trace disagreements. In the headline causal contrast, `S-allow × C-classical-only` completed classically 5/5 with X25519, while `S-require × C-classical-only` rejected 5/5. Same client bytes, build, and host were retained; the server group policy was the differing factor. Hybrid positive controls and symmetric reject controls also matched their preregistered outcomes 5/5. The environment was Ubuntu 24.04.4, OpenSSL 3.0.13, liboqs 0.15.0, oqs-provider 0.11.0, Intel i7-9850H, pinned cores. This is the strongest historical result for a bounded local enforcement claim, but it differs from the manuscript's preregistered E3 environment.

### C2-T1: open-source reproduction

`c2t1_open_source_reproduction.json` retains three open-pipeline runs. Each reports ASR=1, original 1,349 bytes, patched 159 bytes, delta 1,190 bytes, ML-KEM absent from the patch, and valid wire format. Open-pipeline attack TTEs were 12, 32, and 9 microseconds; total times were 1.144359, 0.999399, and 0.903713 s. The retained comparison says open and Claw pipelines each achieved 3/3, but the open pipeline is a bounded tooling reproduction, not an independent model replication and not proof that AI was needed.

### CV7/D1: spread-table key recovery

`cv7_spread_result.json` reports 200,000 samples, 16/16 bytes correct, 16/16 cache lines correct, exact recovered key `5a3c7d912b0e4488f163a5d7194e82c6`, and all-zero XOR difference. The result is a retained direct observation, but the compact record lacks the raw sample distribution and independent run linkage; classify it as bounded rather than as general full-key-recovery evidence.

### Full AES key recovery

`full_key_recovery.json` records 200,000 samples and TTE 281.45 s against OpenSSL 1.0.1e T-table code in WSL2. Only byte positions 0 and 15 were correct (2/16); 8/16 correct bytes were in the top-10 candidate ranks. The recovered key differs from the known key by XOR `00f80f180f8c8ba30936d97d894b8300`; mean margin 10.1%, weakest margin 1.7%. The retained record therefore demonstrates partial signal and two confirmed byte recoveries, not complete key recovery.

## Historical E5 and agent-loop material

The historical tree contains 29 E5 run JSON records spanning R1–R31, plus escrow/log/transcript material. The retained E5 JSON records report one success (R30) and 28 non-success records. The full historical tree also contains 56,635 valid JSONL records. These records are evidence of retained execution lineage and outcomes, not a clean capability denominator: provider-unavailable, driver-error, rejection, and no-claim states must remain separate, and historical/current copies must be deduplicated by hashes and run identity.

The historical `results/ACTS_RESULTS_FINAL.json` is a separate 21-run benchmark aggregate, not the later 54-row agent rerun. It reports 21/21 retained ASR=1 outcomes: three T1/T2/T3 ML-KEM downgrade ablation runs per template, plus 3/3 each for RC4 keystream, CBC padding oracle, ECDSA nonce reuse, and ChaCha20 nonce repeat. Its own summary reports average TTEs of 0.234 ms, 0.011 ms, and 0.012 ms for T1/T2/T3; 0.164 s RC4; 1.471 s CBC; 0.021 s ECDSA; and 0.003 s ChaCha20. The records include direct numerical claims such as RC4 10/10 keystream bytes, CBC plaintext recovery after 2,293 oracle calls, ECDSA private-key recovery with public-key verification, and ChaCha20 XOR plaintext verification. These are retained benchmark observations, but the file is a compact aggregate with transcript previews and synthetic/local benchmark context; it must not be merged with the later agent-capability denominator or treated as independently reproduced by the 54-row campaign.

## Evidence classification

| Result | Classification | Exact supported claim |
|---|---|---|
| A1 WSL2 | PRIMARY_BOUNDED | retained timing experiment failed to reach 3-sigma in the recorded virtualized environment |
| A1 VMware | PRIMARY_BOUNDED | retained VMware configuration produced a large timing contrast under its recorded controls |
| B1 | PRIMARY_BOUNDED | four retained model configurations showed heterogeneous timing-oracle safety responses |
| C2 four targets | PRIMARY_BOUNDED | four recorded hybrid-PQC downgrade targets accepted classical-only negotiation |
| C2b | PRIMARY_VERIFIED | recorded server policy caused the local allow/reject contrast under the specified controls |
| C2-T1 | PRIMARY_BOUNDED | open-source pipeline reproduced the retained wire edit in 3/3 runs |
| CV7/D1 | HISTORICAL_LIMITED | retained compact record reports exact 16-byte recovery after 200,000 samples |
| Full key recovery | PRIMARY_BOUNDED | two key bytes were recovered correctly and residual signal was observed |
| Historical E5 sessions | HISTORICAL_LIMITED | retained historical session identities and outcome states exist; general success is not established |

These classifications are based on retained records, not on the experiment names, the paper's arm registry, or the author's stronger summary fields.

## Additional non-Git content-addressed surface: `vendor/acts-attack`

The workspace also contains an untracked content-addressed directory, `vendor/acts-attack/`, which was outside the earlier ordinary-file crawl boundary. It contains **222 files / 2,097,081 bytes**. Every filename equals the SHA-256 of its content, confirming a CAS layout rather than arbitrary filenames.

Content-lineage comparison found **160/222** vendor objects byte-identical to reconstructed historical `DEPOSIT_V1.1_STAGING` blobs. These are copies/migrations and are not additional observations. The remaining **62 objects / 438,264 bytes** are not present in the selected reachable historical blob set or live ordinary-file tree and must be retained as a separate non-Git evidence surface.

The unique vendor surface contains additional C2b material and execution support:

- an additional C2b record JSONL object (5,185 bytes), a 9-record verdict JSON (1,305 bytes), and a metadata TSV (2,020 bytes), consistent with a separate smoke/control representation;
- TLS client/server trace objects, including classical/hybrid control transcripts;
- agent-loop, oracle, escrow, victim, and capture-layer source files for E2/E5; these are provenance/configuration artifacts and were not executed;
- additional target source files for SSH, hybrid TLS, crypto misuse, authentication, parsing overflow, and known-vulnerability arms;
- Dockerfiles, certificates/private keys, and test/stub files. These establish retained environment/build material but are not themselves result observations.

The vendor CAS therefore closes another important non-Git gap but does not change denominators: the 160 duplicate objects are deduplicated by content hash, while the 62 unique objects are inventoried as retained artifacts pending exact source/run linkage. No archived script was executed.

