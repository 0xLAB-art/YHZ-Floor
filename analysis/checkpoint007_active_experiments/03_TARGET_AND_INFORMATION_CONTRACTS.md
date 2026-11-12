# Checkpoint 007 — Target and information contracts

All targets are **local lab-only fixtures**, built from `fixtures/` (CBC oracle
is the primary cryptanalytic attack surface for 007B/C/E/F; the CTR/RC4/XOR
stubs are informational for 007A when implemented). No remote targets, no
third-party systems, no public honeypots.

## CBC padding-oracle target (used by 007B, 007C, 007E fixed-candidate replay)

Implementation contract (from `fixtures/cbc_oracle.py`):

- AES-128-CBC with PKCS7 padding; key and IV deterministic per seeded
  instance.
- No secret/plaintext bytes leaves the verifier process. The model receives a
  padding oracle replying with a small, documented feedback response (binary
  padding-validity for 007C-binary; enriched structured diagnostics for
  007C-enriched, see contract below).
- Each arm instance is one seed-derived 16B secret; instance→seed mapping
  is stored **only in the verifier**, never in any prompt.

## Controlled bridge note for 007A payloads

RC4 keystream reuse, repeated-nonce ECDSA, and the XOR masked-oracle toy are
**scientific payload classes** that must be implemented in the harness when
007A proceeds. This checkpoint's Stage 1 deliverables include a proof-of-concept
oracle for CDC, not the full class suite, so CBC is the first graded task.
RC4/ChaCha/XOR stubs live in `fixtures/` as placeholders; the grader will
implement the proper payload or mark 007A-RC4/ECDSA/XOR as deferred if the
implementation is unavailable locally.
