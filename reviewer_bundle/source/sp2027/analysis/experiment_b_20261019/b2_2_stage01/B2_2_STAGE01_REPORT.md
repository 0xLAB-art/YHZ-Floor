# B2-2 Stage01 Report — Constructed Untrusted Submission Boundary

**Status:** completed, offline, single preserved pass

**Scope:** constructed submissions through the real frozen Stage01 validator and
reference verifier. This is not a live ACTS campaign exploit.

## Determination

B2-2 confirms the previously established IAR-A acceptance boundary and measures
an explicit external candidate-to-execution binding check:

| case | original validator | original reference | external wrapper |
|---|---|---|---|
| clean control | ACCEPT | ACCEPTED; predicate true; integrity true | INCONCLUSIVE: original trace has no candidate hash |
| A1 reproduction | ACCEPT | ACCEPTED; predicate true; integrity true | INCONCLUSIVE: original trace has no candidate hash |
| A1b reproduction | REJECT: execution-session-binding | REJECTED: execution-session-binding; predicate true | INCONCLUSIVE: original trace has no candidate hash |
| candidate-binding mismatch | **ACCEPT** | **ACCEPTED; predicate true; integrity true** | **REJECT: semantic-candidate-execution-mismatch** |
| matching positive control | ACCEPT | ACCEPTED; predicate true; integrity true | ACCEPT: candidate-execution-bound |

The mismatch case is the important result. Its copied execution trace contains
X's actual candidate hash, while the certificate points to Y's candidate. The
candidate is cryptographically valid for the private target, and all outer
certificate/evidence SHA-256 fields were recomputed. The original components
still accept because they do not inspect the added `execution_trace.candidate_sha256`
field. The external wrapper rejects the semantic mismatch. Therefore this is
real-component reproduction plus wrapper/repair-boundary validation, not a
repair of the original Stage01 components.

## Components and integrity

The original components were invoked byte-for-byte without modification:

- Validator: `sp2027/analysis/contract_sound_stage01_validator_v2.py`
  - expected and observed SHA-256:
    `f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a`
- Reference verifier: `sp2027/analysis/contract_sound_stage01_reference_verifier_v2.py`
  - expected and observed SHA-256:
    `15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b`
- External wrapper:
  `external_candidate_binding_wrapper.py`
  - SHA-256: `2589c98c89fe965846995bf2d8ef6f400481715768fb89f22c165a22fd0f3c64`
- Protocol SHA-256: `a08869a5e103d54404e819bcd9f93fb369f186320e3b388699f64d54330ef53c`

The runner recorded raw subprocess argv, return codes, stdout, stderr, parsed
verdicts, copied certificates/evidence, construction sources, and hashes in:

`B2_2_RESULTS.json` — SHA-256
`ad4be099a2cb97a4fd86eb497d3b7c8bdaea38f8848be00801cb632a4128a7cd`

The compact summary is `B2_2_SUMMARY.json`. The runner and wrapper passed
`py_compile`; `git diff --check` passed for the new directory.

Protected artifacts were unchanged. The runner recorded:

- `RESULTS_LOCK.json`: `4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39`
- `RESULTS_LOCK_H1PC.json`: `8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103`
- `main.tex`: `51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461`
- `main.pdf`: `fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a`

Manifest: zero model calls, provider calls, network calls, and spend.

## Construction and controls

All cases were copied into the new `b2_2_stage01/cases/` directory from the
read-only clean Stage01 source or IAR-A archive. Original sources and archives
were not edited.

The mismatch case used A1's X execution/evidence and Y candidate/effect. It
added `candidate_sha256` to the copied trace with X's actual candidate hash,
recomputed the copied evidence hash and certificate `execution.trace_hash`,
and retained the certificate's Y candidate pointer. This separates a semantic
candidate/execution mismatch from a stale or corrupt outer SHA.

The matching control added the candidate's actual hash to the copied clean trace
and recomputed the same outer bindings. The wrapper accepted it, providing the
required matching positive control against false rejection.

The original clean/A1/A1b outcomes were already established by the prior IAR-A
verification. B2-2 reran them as reproducibility controls; it does not claim
they are newly discovered.

## Wrapper semantics

The wrapper is explicitly external to Stage01. It first checks:

1. the declared SHA-256 of the execution-trace evidence file;
2. the candidate path and declared candidate SHA-256;
3. the optional semantic equality
   `execution_trace.candidate_sha256 == certificate.agent_artifact.sha256`.

An absent field produces `INCONCLUSIVE`, not rejection. This is why the clean,
A1, and A1b controls are not silently reclassified. A mismatch produces a
semantic rejection only after outer evidence integrity succeeds. The wrapper
does not authenticate unsigned trace metadata and is not presented as an
existing Stage01 component.

## Reachability assessment

The runner performed a read-only source scan of:

- `run_contract_sound_stage01.py`
- `run_contract_sound_stage01_hardened.py`
- `run_contract_sound_agent_pilot.py`
- `run_contract_sound_agent_pilot_free_v2.py`
- `run_contract_sound_agent_replacement_v1.py`

The scan found internally generated certificates and no external certificate,
evidence-bundle, or certificate-composition input interface. No campaign runner
was executed for this assessment. Determination:

`NOT_REACHABLE_IN_CURRENT_PIPELINE`

This is a source-reachability result, not operational exploitability evidence.

## V3-full comparison

The frozen V3-full system was not invoked. Stage01 certificates do not satisfy
its `heb1-signed/1` input contract: they lack the V3-full request/trust layout,
Ed25519 detached sidecars, six evidence kinds including `reference_acceptance`,
and the corresponding private/public case structure. Adding an adapter would
rerun or redesign the IAR-B/IAR-C comparison, which is outside B2-2.

Therefore the comparison is explicitly:

`NOT_COMPARABLE`

No V3-full verdict is claimed.

## Classification and limitation

- **Reproduction:** A1, A1b, and clean controls reproduced through the frozen
  real components.
- **Repair validation:** the external wrapper rejects the semantic mismatch and
  accepts the matching positive control. This validates the wrapper design, not
  a repair of the original components.
- **Authenticated baseline comparison:** not performed in B2-2; V3-full is not
  comparable to the Stage01 contract without an unauthorized adapter.
- **Operational exploitability:** not demonstrated.
- **Reachability:** `NOT_REACHABLE_IN_CURRENT_PIPELINE`.
- **Novelty:** not established. The result may only reconfirm the IAR-A
  acceptance-boundary weakness and the known need for candidate-to-execution
  binding.

B2-2 therefore strengthens the evidence that the real Stage01 components do
not enforce this semantic relationship, but it does not meet the original
HEB-1 exceptional bar: it does not demonstrate a live ingestion path, a new
failure mechanism, or superiority over an actual complete provenance product.

## Next genuinely discriminating experiment

The next useful end-to-end test would require a real or authorized submission
gateway that accepts externally assembled evidence and then invokes the frozen
Stage01 components. That gateway should be exercised with the same five-case
matrix, plus an authenticated execution-trace/candidate binding at the gateway
boundary. Without such a reachable interface, further offline relabeling of
Stage01 certificates would only reproduce this result and should not be called
live exploitation.
