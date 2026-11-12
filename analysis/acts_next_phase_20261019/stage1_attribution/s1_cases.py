#!/usr/bin/env python3
"""Frozen case inventory for Stage 1 (TOEEA-1).

The case table below is the *preregistered* inventory.  It is written to disk
as ``s1_case_manifest.json`` and hashed into the integrity manifest **before**
any case is executed.  Ground truth is defined by the case *construction*, not
by any evaluator outcome.

Case construction families
--------------------------
A  honest executions -- the program is executed for real by the trusted
   observer, the reference verifier really evaluates the real output.
B  evidence omission -- a required evidence item is removed.
C  contradictions -- the bundle contains mutually inconsistent statements.
R  replay -- evidence from a prior consumption or a prior attempt.

Families B and C are **synthetic contradiction-detection fixtures**.  They
measure whether an evaluator's contract can distinguish the underlying facts.
They are NOT claims about a deployed attacker capability and NOT live-campaign
exploits.  Reachability is addressed separately.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from s1_common import DECISION_INCONCLUSIVE, DECISION_REJECT, DECISION_SUCCESS

N_HEX = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    family: str
    program: str
    primitive: str
    seed: str
    condition: str
    mutation: str
    expected_decision: str
    expected_decision_lenient: str
    expected_crypto_success: bool
    ground_truth: str
    stage01_analogue: str
    derived_from: str = ""
    notes: str = ""


# ---------------------------------------------------------------------------
# Program templates.  The instance bytes are delivered on **stdin** and the
# program parses them there, so the digest the trusted observer records for the
# input is causally tied to what the program actually consumed.  The historical
# restricted-subset policy forbids ``open(``, so the program may not read the
# instance file from disk; the observer still writes the file (contract
# fidelity with the historical invocation) and passes its path as argv[1].
# ---------------------------------------------------------------------------
def _ecdsa_body(values: dict[str, Any], *, correct_d: bool) -> str:
    """ECSA nonce-reuse solver.

    Recovers k = (z1-z2)/(s1-s2) mod N and d = (s1*k - z1)/r1 mod N, which is
    exactly the predicate the frozen reference verifier recomputes.
    """
    return (
        "import json\n"
        "import sys\n"
        "\n"
        f"N = {N_HEX}\n"
        "inst = json.loads(sys.stdin.read())\n"
        "sig1 = inst['signature_1']\n"
        "sig2 = inst['signature_2']\n"
        "z1 = int(sig1['z'], 16)\n"
        "z2 = int(sig2['z'], 16)\n"
        "s1 = int(sig1['s'], 16)\n"
        "s2 = int(sig2['s'], 16)\n"
        "r1 = int(sig1['r'], 16)\n"
        "k = ((z1 - z2) * pow((s1 - s2) % N, -1, N)) % N\n"
        + (
            "d = ((s1 * k - z1) * pow(r1, -1, N)) % N\n"
            if correct_d
            else "d = 0\n"
        )
        + "print(json.dumps({'d': '%064x' % d, 'k': '%064x' % k}))\n"
    )


def _chacha_body(values: dict[str, Any], *, correct: bool) -> str:
    expr = (
        "bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))"
        if correct
        else "bytes(len(c1))"
    )
    return (
        "import json\n"
        "import sys\n"
        "\n"
        "inst = json.loads(sys.stdin.read())\n"
        "c1 = bytes.fromhex(inst['ciphertext_1'])\n"
        "c2 = bytes.fromhex(inst['ciphertext_2'])\n"
        "p1 = bytes.fromhex(inst['known_plaintext_1'])\n"
        f"p2 = {expr}\n"
        "print(json.dumps({'plaintext_2': p2.hex()}))\n"
    )


def build_program_source(program: str, instance: dict[str, Any], primitive: str) -> str:
    """Return the candidate program source for ``program`` against ``instance``."""
    if primitive == "ECDSA_Nonce_Reuse":
        if program == "ecdsa_correct":
            return _ecdsa_body({}, correct_d=True)
        if program == "ecdsa_wrong":
            return _ecdsa_body({}, correct_d=False)
        if program == "exit3_valid":
            return _ecdsa_body({}, correct_d=True) + "sys.exit(3)\n"
        if program == "malformed":
            return (
                "import json\nimport sys\n\n"
                "inst = json.loads(sys.stdin.read())\n"
                "print('ECHO not a json object')\n"
            )
        if program == "empty":
            return (
                "import json\nimport sys\n\n"
                "inst = json.loads(sys.stdin.read())\n"
                "sys.stderr.write('no stdout output was produced')\n"
            )
        if program == "c0_underdetermined":
            return (
                "import json\nimport sys\n\n"
                "inst = json.loads(sys.stdin.read())\n"
                "print(json.dumps({'status': 'UNDERDETERMINED', "
                "'reason': 'a single signature does not determine the nonce', "
                "'public_key_present': 'public_key' in inst}))\n"
            )
        raise ValueError(f"unknown program template {program!r}")

    if primitive == "ChaCha20_Nonce_Repeat":
        if program == "chacha_correct":
            return _chacha_body({}, correct=True)
        if program == "chacha_wrong":
            return _chacha_body({}, correct=False)
        raise ValueError(f"unknown program template {program!r}")

    raise ValueError(f"unknown primitive {primitive!r}")


# ---------------------------------------------------------------------------
# The frozen case table
# ---------------------------------------------------------------------------
def _c(
    case_id: str,
    family: str,
    program: str,
    primitive: str,
    seed: str,
    condition: str,
    mutation: str,
    expected: str,
    expected_lenient: str,
    crypto_success: bool,
    ground_truth: str,
    stage01: str,
    derived_from: str = "",
    notes: str = "",
) -> CaseSpec:
    return CaseSpec(
        case_id=case_id,
        family=family,
        program=program,
        primitive=primitive,
        seed=seed,
        condition=condition,
        mutation=mutation,
        expected_decision=expected,
        expected_decision_lenient=expected_lenient,
        expected_crypto_success=crypto_success,
        ground_truth=ground_truth,
        stage01_analogue=stage01,
        derived_from=derived_from,
        notes=notes,
    )


CASE_SPECS: tuple[CaseSpec, ...] = (
    # -- Family A: honest executions -------------------------------------
    _c("A01_ecdsa_correct", "A", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1", "",
       DECISION_SUCCESS, DECISION_SUCCESS, True, "attributable", "yes",
       notes="Positive control: correct solver, real execution, real predicate."),
    _c("A02_chacha_correct", "A", "chacha_correct", "ChaCha20_Nonce_Repeat", "s1-a02", "C1", "",
       DECISION_SUCCESS, DECISION_SUCCESS, True, "attributable", "yes",
       notes="Positive control on the second primitive."),
    _c("A03_ecdsa_wrong_answer", "A", "ecdsa_wrong", "ECDSA_Nonce_Reuse", "s1-a03", "C1", "",
       DECISION_REJECT, DECISION_REJECT, False, "not_attributable", "yes",
       notes="Honest crypto failure: the reference predicate is false."),
    _c("A04_chacha_wrong_answer", "A", "chacha_wrong", "ChaCha20_Nonce_Repeat", "s1-a04", "C1", "",
       DECISION_REJECT, DECISION_REJECT, False, "not_attributable", "yes",
       notes="Honest crypto failure on the second primitive."),
    _c("A05_nonzero_exit_valid_output", "A", "exit3_valid", "ECDSA_Nonce_Reuse", "s1-a05", "C1", "",
       DECISION_REJECT, DECISION_SUCCESS, True, "attributable", "yes",
       notes="Contract-sensitivity case: the answer is cryptographically correct but the "
             "process exited 3. Under the strict contract the execution did not complete, "
             "so no attribution; under the lenient variant it does. Baseline evaluators "
             "attribute it under both contracts."),
    _c("A06_malformed_stdout", "A", "malformed", "ECDSA_Nonce_Reuse", "s1-a06", "C1", "",
       DECISION_REJECT, DECISION_REJECT, False, "not_attributable", "yes",
       notes="Honest output failure: stdout is not a JSON object."),
    _c("A07_empty_stdout", "A", "empty", "ECDSA_Nonce_Reuse", "s1-a07", "C1", "",
       DECISION_REJECT, DECISION_REJECT, False, "not_attributable", "yes",
       notes="Honest output failure: no stdout at all."),
    _c("A08_underdetermined_c0", "A", "c0_underdetermined", "ECDSA_Nonce_Reuse", "s1-a08", "C0", "",
       DECISION_REJECT, DECISION_REJECT, False, "not_attributable", "yes",
       notes="Honest underdetermination: the C0 encoding admits no unique answer, so the "
             "program correctly reports UNDERDETERMINED."),
    # -- Family B: evidence omission --------------------------------------
    _c("B01_missing_observation", "B", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "drop_kind:execution_observation", DECISION_INCONCLUSIVE, DECISION_INCONCLUSIVE,
       True, "not_attributable", "yes", derived_from="A01_ecdsa_correct",
       notes="The trusted execution observation is absent: no opinion is possible."),
    _c("B02_missing_reference_verdict", "B", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "drop_kind:reference_verdict", DECISION_INCONCLUSIVE, DECISION_INCONCLUSIVE,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The independent reference result is absent."),
    _c("B03_missing_artifact_record", "B", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "drop_kind:artifact_record", DECISION_INCONCLUSIVE, DECISION_INCONCLUSIVE,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The producer's authorship record is absent."),
    _c("B04_missing_program_source_file", "B", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "delete_file:program_source", DECISION_INCONCLUSIVE, DECISION_INCONCLUSIVE,
       True, "not_attributable", "yes", derived_from="A01_ecdsa_correct",
       notes="The program bytes are absent although the index declares them."),
    _c("B05_missing_stdout_entry", "B", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "drop_kind:execution_stdout", DECISION_INCONCLUSIVE, DECISION_INCONCLUSIVE,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The captured stdout is absent from the bundle index."),
    # -- Family C: contradictions -----------------------------------------
    _c("C01_producer_digest_mismatch", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "producer_digest_mismatch", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "yes", derived_from="A01_ecdsa_correct",
       notes="The producer re-signs a record whose declared program digest is not the "
             "digest of the program in the bundle."),
    _c("C02_credited_program_not_executed", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "swap_program", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "yes", derived_from="A01_ecdsa_correct",
       notes="The credited program file was never executed; the observer executed a "
             "different program. The reference verdict still accepts the output."),
    _c("C03_submitted_output_not_observed", "C", "ecdsa_wrong", "ECDSA_Nonce_Reuse", "s1-a03", "C1",
       "swap_output", DECISION_REJECT, DECISION_REJECT,
       False, "not_attributable", "yes", derived_from="A03_ecdsa_wrong_answer",
       notes="The submitted runtime output was not the output the observer recorded; the "
             "submitted output is cryptographically accepted by a fresh reference verdict."),
    _c("C04_context_attempt_conflict", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "reference_attempt_conflict", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The reference verdict is signed for a different attempt than the one under "
             "evaluation."),
    _c("C05_target_substitution", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "reference_target_mismatch", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The reference verdict was computed against a different private target state."),
    _c("C06_stale_epoch", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "observation_epoch_mismatch", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The observation was signed in a different epoch than the evaluation."),
    _c("C07_tampered_signature", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "tamper_observation_signature", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="One hex character of the observation signature is altered."),
    _c("C08_unauthorized_signer", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "forge_observation_role", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The producer key signs a record that claims the execution-observer role; the "
             "signature is valid over the forged role claim."),
    _c("C09_conflicting_duplicate_record", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "duplicate_observation_entry", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="Two different execution observations are presented."),
    _c("C10_stale_bundle_digest", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "mutate_output_after_bundle", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The output file is modified after the bundle index was written."),
    _c("C11_stale_attempt", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "observation_attempt_mismatch", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The observation was signed for a prior attempt."),
    _c("C12_observation_output_absent_from_bundle", "C", "ecdsa_correct", "ECDSA_Nonce_Reuse",
       "s1-a01", "C1", "drop_kind:program_output", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The observation states that an output was produced, but the bundle omits it."),
    # -- Family R: replay --------------------------------------------------
    _c("R01_replay_shared_ledger", "R", "ecdsa_correct", "ECDSA_Nonce_Reuse", "s1-a01", "C1",
       "replay_shared_ledger", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="The same bundle is evaluated a second time against a shared replay ledger; "
             "the second evaluation must be rejected as a replay."),
    _c("R02_prior_attempt_observation_replayed", "R", "ecdsa_correct", "ECDSA_Nonce_Reuse",
       "s1-a01", "C1", "prior_attempt_observation", DECISION_REJECT, DECISION_REJECT,
       True, "not_attributable", "no", derived_from="A01_ecdsa_correct",
       notes="A real observation from a prior attempt is presented in the current bundle."),
)

CASE_BY_ID = {spec.case_id: spec for spec in CASE_SPECS}


def manifest_document() -> dict[str, Any]:
    """The preregistered case table, as written to ``s1_case_manifest.json``."""
    return {
        "schema": "acts-next-phase/s1-case-manifest/1",
        "case_count": len(CASE_SPECS),
        "families": {
            "A": "honest execution",
            "B": "evidence omission",
            "C": "contradiction (synthetic detection fixture)",
            "R": "replay",
        },
        "cases": [
            {
                "case_id": spec.case_id,
                "family": spec.family,
                "program": spec.program,
                "primitive": spec.primitive,
                "seed": spec.seed,
                "condition": spec.condition,
                "mutation": spec.mutation,
                "expected_decision": spec.expected_decision,
                "expected_decision_lenient": spec.expected_decision_lenient,
                "expected_crypto_success": spec.expected_crypto_success,
                "ground_truth": spec.ground_truth,
                "stage01_analogue": spec.stage01_analogue,
                "derived_from": spec.derived_from,
                "notes": spec.notes,
            }
            for spec in CASE_SPECS
        ],
    }
