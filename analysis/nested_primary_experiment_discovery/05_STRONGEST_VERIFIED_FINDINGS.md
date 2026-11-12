# Strongest findings

## 1. Local hybrid-policy enforcement is directly verified

The strongest result is C2b. In the retained 3x3 matrix, a server configured to allow classical fallback completed the classical-only client condition in 5/5 handshakes, while a server configured to require the hybrid group rejected the same classical-only client in 5/5 with alert 40 and no Finished. Hybrid-capable controls completed 5/5, and classical servers rejected hybrid-only clients 5/5. All 45 verdicts are trace-backed with zero endpoint disagreements.

Supported inference: the recorded server group policy is the enforcement point for this local client/server/build configuration.

Unproven: a general TLS vulnerability, an ML-KEM break, deployment prevalence, or behavior on other versions/builds.

Evidence: `ACTS-ATTACK/data/c2b_hybrid_required_control.json`, `ACTS-ATTACK/harness/results_c2b_pq/`, grade `PRIMARY_VERIFIED`.

## 2. Fixed cryptographic operation paths are independently oracle-checked

The fixed-operation rerun reaches accepted outputs in all 12 retained operations: RC4, CBC padding oracle, ECDSA nonce reuse, and ChaCha20 nonce reuse each succeed 3/3. The oracle owns reserved ground truth, secrets are fresh per replicate, retries are disabled, and paired executor/oracle monotonic spans are retained.

Supported inference: these four local operation implementations and verifier paths were exercised successfully under the recorded Linux/OpenSSL environment.

Unproven: any agent capability, an agent-time estimate, or a causal comparison to the historical agent loop.

## 3. The repository contains a real environment-sensitive timing contrast

The WSL2 record fails its 3-sigma threshold (z=1.9107; ASR=0), whereas the VMware record reports 90,000 valid trimmed samples, z=113.6987, and ASR=1.

Supported inference: the two recorded configurations produced materially different observed timing separability.

Unproven: causality of the environment change, generality beyond the recorded builds/hosts, and portable side-channel strength.

## 4. C2-T1 is reproducible as a bounded wire edit

Three open-pipeline records report 3/3 ASR and 3/3 wire-format validity, with attack times of 9e-6 to 3.2e-5 s and total times of 0.903713 to 1.144359 s. The record itself limits binary verification (`r2_verified=false`).

Supported inference: the retained open pipeline can perform the specified wire-format edit on the tested input class.

Unproven: AI necessity, toolchain generality, or parity with proprietary binary-analysis capabilities.

## 5. D1 contains a striking but bounded key-recovery observation

The Spread-Table result reports 16/16 bytes and cache lines correct with XOR difference `00000000000000000000000000000000` after 200,000 samples. The sibling Bernstein record reports only 2/16 correct bytes and a nonzero XOR difference.

Supported inference: the retained Spread-Table record is consistent with exact recovery of the declared known key for the recorded implementation/configuration.

Unproven: independent reproduction, raw-sample auditability, portability, and general AES key recovery.

Evidence: `data/cv7_spread_result.json`, `data/full_key_recovery.json`, grade `PRIMARY_BOUNDED`.
