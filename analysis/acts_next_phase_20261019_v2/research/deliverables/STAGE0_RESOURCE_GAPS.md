# Stage 0 — Resource and Permission Gaps

**Project:** ACTS-Attack  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/research/`  
**Date:** 2026-10-20  
**Status:** COMPLETE

## 1. Resources Requiring User Authorization

The following resources were identified as blockers; statuses below reflect subsequent user authorization and execution:

| # | Resource | Why Blocking | Authorization Needed | Status |
|---|----------|--------------|----------------------|--------|
| 1 | **heb1_remediation_v1 test suite re-run** | Independently reproduce prior 55-PASS claim | Read-only execution (no external deps) | **RESOLVED — 55 passed in 3.36s** |
| 2 | **in-toto / SLSA Verifier / Sigstore-Cosign installation** | Execute a bounded comparison against genuine upstream implementations | Install only in isolated environment | **RESOLVED — authorized, installed, Stage 2 executed** |
| 3 | **Stage 4 model route (`claude-sonnet-4-6-free` via https://api.apmix.ai)** | Confirm route and analyze bounded AI-agent evidence | Provider authorization + model access confirmation | **RESOLVED — HTTP 200 exact-route attestation; 72-session evidence analyzed** |
| 4 | **Authorized reachable ingress for Stage 3** | Stage 3 needed an ingress through which untrusted evidence could reach the evaluation path | Authorization to construct and exercise a controlled local ingress | **RESOLVED — loopback ingress constructed and exercised; 0 unauthorized attributions** |
| 5 | **Live target for the campaign** | Stage 5 needed the project's own containerised target with a reserved secret adjudicated by a separate process | Authorization to start the target locally on loopback | **RESOLVED — the project image was started, exploited and attributed; the model agent's failure is reported** |

## 2. Resources NOT Requiring Authorization (Can Proceed)

| # | Resource | Basis |
|---|----------|-------|
| 1 | Stage 1 e2a documentation (RESULTS.md, PROTOCOL.md) | Based entirely on local executed run results |
| 2 | Stage 12 prior art matrix | Read-only analysis of existing documents + prior art knowledge |
| 3 | Stage 13 scientific validity audit | Read-only analysis of denominators, freezes, claims, limitations |
| 4 | MASTER_PROGRESS_REPORT.md | Compilation of completed work |
| 5 | REPOSITORY_AND_TRUST_BOUNDARY_MAP.md | Source-level dataflow mapping |
| 6 | MANIFEST.sha256 | Hash computation on local generated files |

## 3. Notes

- No money will be spent, no services deployed, no external targets attacked, no provider restrictions bypassed.
- Local offline work proceeded by default; network/install actions occurred only after explicit user authorization.
- If any authorization is denied, the corresponding stage is documented as BLOCKED_BY_RESOURCE_OR_AUTHORIZATION rather than fabricated.