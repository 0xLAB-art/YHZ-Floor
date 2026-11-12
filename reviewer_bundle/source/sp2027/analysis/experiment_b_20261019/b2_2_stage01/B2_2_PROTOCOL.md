# B2-2 Protocol — Constructed Untrusted Submission Through Stage01

Status: frozen before execution. This is a new, offline, separately versioned
follow-on. It does not modify the Stage01 components or any archived campaign
artifact.

## Question

Can an externally assembled certificate/evidence submission pass the real
Stage01 validator and reference verifier while the credited execution's
candidate output is not the submitted candidate? If so, does an explicitly
identified external candidate-to-execution binding wrapper reject that same
submission while preserving a matching positive control?

This is a constructed submission-boundary experiment. It is **not** a live
ACTS campaign exploit and must not be reported as one.

## Immutable components

- Validator: `../contract_sound_stage01_validator_v2.py`, SHA-256
  `f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a`.
- Reference verifier: `../contract_sound_stage01_reference_verifier_v2.py`,
  SHA-256 `15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b`.
- Original controls are read from the clean Stage01 source and IAR-A archive;
  source files are copied into this directory's cases and never edited.

## Cases

1. `clean_control`: clean Stage01 certificate/candidate. Expected original
   validator ACCEPT and reference ACCEPTED. The wrapper is `INCONCLUSIVE`
   because the original clean trace has no explicit candidate hash; this is a
   reproducibility control, already established by the clean Stage01 campaign.
2. `a1_reproduction`: archived A1 constructed cross-boundary certificate:
   X execution/trace/authorship evidence, Y candidate/effect. Expected original
   validator ACCEPT and reference ACCEPTED; wrapper outcome is recorded as the
   external comparison. This reproduces the already established IAR-A result.
3. `a1b_reproduction`: archived A1b session mismatch. Expected original
   validator REJECT and reference REJECTED on execution-session-binding; wrapper
   outcome is recorded. This is a negative reproducibility control.
4. `candidate_binding_mismatch`: a new copy of A1 in which the copied trace
   contains `candidate_sha256` equal to X's actual candidate hash, while the
   certificate points to Y's submitted candidate. All outer evidence hashes and
   the certificate trace hash are recomputed. The original components do not
   enforce this added field; that outcome is measured, not assumed.
5. `candidate_binding_match_control`: clean control with a copied trace
   containing `candidate_sha256` equal to the submitted candidate hash. The
   original components should still accept, and the external wrapper should
   ACCEPT. This checks that the wrapper does not reject a matching positive
   case.

The mismatch and match cases deliberately separate semantic mismatch from a
stale/corrupt outer SHA. Every copied evidence file's certificate hash and the
certificate's `execution.trace_hash` are recomputed. A separate stale-hash
negative is not used as the repair result; stale/corrupt-hash behavior is
reported only if encountered.

## Systems compared

- `original-validator`: exact frozen validator, certificate on stdin.
- `original-reference`: exact frozen reference verifier, generated bundle JSON.
- `external-binding-wrapper`: new wrapper only; it first runs the original
  validator and then checks candidate existence/hash plus
  `execution_trace.candidate_sha256 == certificate.agent_artifact.sha256`.
  It does not claim to authenticate unsigned trace metadata; it only enforces
  the explicit semantic link supplied by the submission.
- `v3-full`: comparison is conditional. Stage01 certificates do not satisfy
  the frozen V3-full `heb1-signed/1` contract (Ed25519 sidecars, six evidence
  kinds, request/trust layout). No IAR-B/IAR-C rerun or redesign is allowed.
  Therefore the runner records `NOT_COMPARABLE` rather than silently adapting
  formats or claiming a V3-full result.

## Reachability assessment

The runner performs a read-only source scan of the ACTS Stage01 campaign
runners. It checks whether any runner accepts an externally supplied public
certificate/evidence bundle or certificate-composition input. The expected
determination is `NOT_REACHABLE_IN_CURRENT_PIPELINE`: campaign harnesses create
certificates internally from one case/session; no external certificate
ingestion/composition interface is present. This is a source-reachability
finding, not a dynamic campaign result.

## Evidence and determination

`b2_2_runner.py` preserves:

- exact source paths and component hashes;
- copied case construction and all raw certificates/evidence;
- subprocess argv, return codes, stdout, stderr, parsed verdicts, and hashes;
- wrapper checks and reasons;
- V3-full comparability record;
- read-only reachability evidence and determination;
- protected-file hashes and offline manifest.

The final report must distinguish: reproduction, repair/wrapper validation,
authenticated-baseline comparison, operational exploitability, and reachability.
If the pass only reconfirms IAR-A, it must say so and recommend the next
discriminating end-to-end experiment rather than claim a new vulnerability.
