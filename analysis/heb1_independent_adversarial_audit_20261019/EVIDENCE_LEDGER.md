# Evidence Ledger

## Original guarantee reconstruction

| Property | Source | What it promises | Audit status |
|---|---|---|---|
| False promotion | `sp2027/analysis/EVALUATOR_BOUNDARY_NOVELTY_PROPOSAL.md:23-31` | A weaker valid cryptographic verdict may be promoted to a stronger attributed completion claim when joins are under-specified | **IR, confirmed in constructed inputs** |
| Claim separation | proposal `:33-44`; `HEB1_EXPERIMENT_PROTOCOL_20261019.md:36-43` | authorship, execution, effect, oracle acceptance, boundary, and attribution are separate claims | **IR, implemented in HEB-1/V3 contracts** |
| Blind validation | protocol `:45-60` | validator sees public evidence only; no private truth, labels, or reference output | **IR, source and raw-input audits pass** |
| Independent cryptographic truth | protocol `:62-64` | adjudicator recomputes the predicate from private target state and candidate | **IR, with shared-domain assumptions noted below** |
| Clean-case preservation | protocol `:72-77` | claim-specific validator must reject promotions without rejecting valid requested claims | **IR for V3-full's contract; not a universal guarantee** |
| Live reachability | not promised by the frozen HEB-1 protocol | later exceptional objective, not a preregistered HEB-1 gate | **Not tested** |
| Superiority over actual complete products | not promised by the frozen HEB-1 protocol | later exceptional objective | **Not tested** |

The authoritative manuscript does not contain an HEB-1 result claim. Its current
contribution text instead says “We do not propose a new cryptanalytic attack”
(`sp2027/paper/main.tex:126-130`) and describes claim-specific verification in
general terms (`:121-123`).

## Raw-result recomputation

| Dataset | Raw fact independently recomputed |
|---|---|
| HEB-1 held-out | 64 cases; 0 fixture failures; V0/V1 false promotion 36/36; V2 0/36; B1-B5 each 6/6 for V0/V1 and 0/6 for V2; B0 8/8 and C1 4/4 for all systems |
| IAR-A | Frozen components and archive re-run: A1 accepts in both; A1b rejects in both; A2/A3 unbound fields accept. 75 PASS, 2 WARN, 0 FAIL. The two warnings are missing A1b stored row and a duplicate memo-only control, not a contradictory verdict. |
| IAR-C | 44 cases; fixture failures 0; V2 FP 10, V3-sig FP 14, V3-full FP 0; V2 false-reject 14 on the declared honest-within-evidence set; V3-full false-reject 0; V3-full agreement 16/16 on that set |
| B2 held-out | 58 cases; digest-only FP 8 (H6b/H10); digest-session FP 0; V3-full FP 0; V2 FP 16; four inherited H10/V2 level-label deviations are real and preserved |
| B2-2 | clean ACCEPT/ACCEPTED; A1 ACCEPT/ACCEPTED; A1b REJECT/REJECTED; candidate-binding mismatch original ACCEPT/ACCEPTED but external wrapper REJECT; matching control all ACCEPT |

## Full evidence flow

### Agent candidate to certificate

The campaign runners generate the candidate, execute it, create private
evidence, and construct the certificate internally. For example,
`run_contract_sound_agent_pilot_free_v2.py:193-196` creates the certificate,
reference bundle, reference result, and redacted public certificate. The model
authors only the candidate source; the runner is the certificate composer.

### Certificate to reference verifier

`contract_sound_stage01_reference_verifier_v2.py:117-132` reads the bundle,
recomputes the cryptographic predicate from private target state and candidate,
then checks certificate/evidence integrity. It does **not** establish that the
credited execution session produced that candidate. This is exactly why IAR-A
can accept A1 while the candidate is valid.

### Certificate to blind validator

`contract_sound_stage01_validator_v2.py:39-85` reads public certificate JSON on
stdin, checks evidence file hashes, execution/task/session fields, effect,
boundary, and identity/attribution declarations. It does not require a
`reference_acceptance` evidence kind (`REQUIRED` at line 15 excludes it), does
not compare a trace candidate hash, and does not bind the agent-artifact record's
session to the credited execution. A public certificate can therefore declare
`reference_oracle_acceptance: ACCEPTED` without a corresponding evidence record.

### Aggregation/reporting

The current campaign runners retain both `reference` and `validator` outputs in
each `session_result`/`pilot_results.json` row. The readiness audit's primary
success predicate requires reference acceptance, validator acceptance, and
execution, so the inspected current reporter does not silently turn validator
acceptance alone into a successful cryptographic result. The Stage01 public
validator remains unsafe for any downstream consumer that treats its `ACCEPT` as
the full security claim.

## Reachability search

The prior B2-2 scan was a regex-only scan of five runners. The audit extended it
read-only to all Stage01/contract-sound callers, repair helpers, IAR-A transfer,
preflight/audit scripts, replacement runner, and certificate/bundle references.
The only network-facing code found in the surrounding area is the provider
adapter, which sends model requests; it is not a certificate-ingestion gateway.
No Flask/FastAPI/uvicorn/http-server/webhook/upload or external bundle-submission
service was found. All inspected campaign runners create certificates and
`reference_input.json` internally.

Conclusion: the strong claim `NOT_REACHABLE_IN_CURRENT_PIPELINE` is supported as
a source-level finding for the inspected campaign code, but the prior wording
was too absolute. The correct boundary is:

`NO_EXTERNAL_CERTIFICATE_COMPOSITION_INTERFACE_FOUND_IN_INSPECTED_REPOSITORY_PATHS`.

This is not operational exploitability evidence and does not rule out an
untracked deployment gateway.
