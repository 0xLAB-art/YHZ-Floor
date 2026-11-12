# Resource and Permission Requests

**Project:** ACTS-Attack  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/`  
**Date:** 2026-10-20  
**Status:** RESOLVED — all four requests closed

---

## 1. Purpose

This document records authorization decisions and outcomes. All four requests have been resolved.

---

## 2. Requests Requiring Authorization

### Request 2.1 — heb1_remediation_v1 Test Suite Re-Run

**Resource:** Read-only execution of the heb1_remediation_v1 test suite (55 PASS claimed by prior team)  
**Purpose:** Independently reproduce prior results in this environment before trusting them as a baseline  
**Dependencies:** None external (no network, no installs)  
**Risk:** Low — read-only, no modifications  
**Authorization needed:** User confirmation to run the test suite  
**Status:** APPROVED AND COMPLETED — 55 passed in 3.36s

### Request 2.2 — in-toto / SLSA Verifier / Sigstore-Cosign Installation

**Resource:** Installation of provenance verification tools in an isolated environment  
**Purpose:** Stage 2 requires a fair comparison against genuine upstream provenance implementations  
**Dependencies:** Network fetch / pip install of official binaries or packages  
**Risk:** Medium — modifies the environment; must not alter main project dependencies  
**Authorization needed:** User approval to install new dependencies in isolation  
**Status:** APPROVED AND COMPLETED — isolated tools installed; Stage 2 executed

### Request 2.3 — Stage 4 Model Route Access

**Resource:** `claude-sonnet-4-6-free` via https://api.apmix.ai  
**Purpose:** Stage 4 AI-agent vs scripted producer study (matched arms under the same contract)  
**Dependencies:** Provider authorization, model access confirmation  
**Risk:** Medium — provider calls, potential spending  
**Authorization needed:** Provider authorization + model access confirmation, confirmed free/approved spending limit, max call count, no paid fallback, sampling controls, retention policy  
**Status:** APPROVED AND EXECUTED — fresh HTTP 200 route attestation; existing frozen 72-session evidence analyzed; no fallback

### Request 2.4 — Authorized Reachable Ingress for Stage 3

**Resource:** Confirmation of an existing authorized gateway with a real accepted input format and documented attacker-controlled fields  
**Purpose:** Stage 3 is conditional on identifying an authorized reachable ingress  
**Dependencies:** None (information only)  
**Risk:** Low  
**Authorization needed:** Confirmation of `NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED`, or provision of an authorized gateway  
**Status:** RESOLVED — no external gateway exists; a controlled loopback ingress was constructed in `stage3_boundary/` and exercised (12 submissions, 0 unauthorized attributions)

---

## 3. Constraints Honored

| Constraint | How honored |
|------------|-------------|
| No money spent | No paid services, no paid fallback |
| No services deployed | No external deployment |
| No external targets attacked | No third-party targets |
| No provider restrictions bypassed | All provider calls require explicit authorization |
| No model calls without authorization | Fresh model call occurred only after explicit authorization; exact route matched |
| No network/installs without approval | Stage 2 installation and Stage 4 call occurred only after explicit approval |
| Report negative results | No native provenance interoperability, no large representation effect, and no external gateway are documented |
| Do not claim novelty without evidence | Stage 4 null/inconclusive effect incorporated; strong novelty claim rejected |

---

## 4. Consequences of Denial

Requests 2.1–2.4 are closed. No further authorization is required for the completed scope.

| Request | Final status |
|---------|--------------|
| 2.1 | COMPLETED — 55/55 tests passed |
| 2.2 | COMPLETED — isolated tools and bounded Stage 2 comparison |
| 2.3 | COMPLETED — route attested and bounded Stage 4 evidence analyzed |
| 2.4 | COMPLETED — controlled loopback ingress constructed and exercised; no external gateway exists |

---

## 5. What Can Proceed Without Authorization

All four requests are closed and every deliverable in the completed scope is produced.

---

## 6. Requested User Action

No further action is required. If an externally reachable gateway is provisioned later, it would extend Stage 3 beyond the loopback scope and would need its own preregistration.