# Checkpoint 007 — Pilot #1 CBC pilot notes (non-confirmatory)

CBC pilot arm P001_CBC_PNAS completed.

Local observations:
- public_obs: {'obs':'P1 cbc prefix','P2':'P2','task':'cbc_padding_oracle'}
  reduced to prompt '{"obs":"P1 cbc prefix","P2":"P2","task":"cbc_padding_oracle"}' with no
  secret, digest, oracle endpoint, or verifier truth. Truth-exclusion gate passed.
- The model interpreted the input as a CBC padding oracle task but asked for clarification
  rather than assuming an implementation. That is a valid pilot outcome (instrument
  confirms the task is recognizable, but the prompt needs a clearer solve directive to
  exercise the construct we care about: code construction + oracle probing).

Next pilot design decision (before any confirmatory arm):
- Add an explicit solve directive (e.g., "write Python to recover the plaintext from a
  padding oracle in <max turns> using <oracle budget> queries") AND a concrete,
  purely numerical toy instance in the public prompt so the model can demonstrate solution
  behavior without any secret leaving the verifier process.
- The toy instance's reserved secret and plaintext are generated only in the verifier;
  the prompt includes only the ciphertext and the description of the oracle feedback.
- This keeps the instrument faithful to the construct (authoring + probing) and testable
  against the success predicate (final candidate == reserved secret).

Pilot result used only to tune instrument wording, not counted as evidence.
