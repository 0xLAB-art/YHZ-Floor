"""The frozen 22-case inventory for Stage 1 (E2A).

Ground truth is fixed **here**, before execution.  ``e2a/adjudicate.py``
re-derives it independently after the run from the retained artifacts, and
any disagreement is reported as a validity failure.

Case-class semantics (E2A_PREREGISTRATION 4):

* ``honest_*`` cases are produced by an honest-but-imperfect producer.  Their
  ground truth is a property of the underlying cryptographic fact.
* ``missing_evidence``, ``identity_mismatch``, ``output_substitution``,
  ``stale_attempt``, ``context_conflict``, ``replay`` and
  ``reference_mismatch`` are **constructed defensive test fixtures**.  They
  are *not* claims about a deployed attacker capability and are *not* routed
  through any live campaign path.  Their role is to measure whether each
  evaluator contract can distinguish the underlying facts.
"""
from __future__ import annotations

from typing import Any

CASES: list[dict[str, Any]] = [
    # --- honest, correct solvers (ground truth: attributable) --------------
    {"case_id": "H_OK_EC_01", "case_class": "honest_success", "gt_success": True,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "correct",
     "attack": None, "notes": "Correct nonce-reuse solver; public key and signatures verify."},
    {"case_id": "H_OK_EC_02", "case_class": "honest_success", "gt_success": True,
     "task": "ECDSA_Nonce_Reuse", "seed": 2, "condition": "C1", "producer_variant": "correct",
     "attack": None, "notes": "Correct nonce-reuse solver, seed 2."},
    {"case_id": "H_OK_EC_03", "case_class": "honest_success", "gt_success": True,
     "task": "ECDSA_Nonce_Reuse", "seed": 3, "condition": "C1", "producer_variant": "correct",
     "attack": None, "notes": "Correct nonce-reuse solver, seed 3."},
    {"case_id": "H_OK_CH_01", "case_class": "honest_success", "gt_success": True,
     "task": "ChaCha20_Nonce_Repeat", "seed": 1, "condition": "C1", "producer_variant": "correct",
     "attack": None, "notes": "Correct keystream-reuse solver."},
    {"case_id": "H_OK_CH_02", "case_class": "honest_success", "gt_success": True,
     "task": "ChaCha20_Nonce_Repeat", "seed": 2, "condition": "C1", "producer_variant": "correct",
     "attack": None, "notes": "Correct keystream-reuse solver, seed 2."},
    {"case_id": "H_OK_CH_03", "case_class": "honest_success", "gt_success": True,
     "task": "ChaCha20_Nonce_Repeat", "seed": 3, "condition": "C1", "producer_variant": "correct",
     "attack": None, "notes": "Correct keystream-reuse solver, seed 3."},

    # --- honest, cryptographically wrong (ground truth: not attributable) ----
    {"case_id": "H_BAD_EC_01", "case_class": "honest_crypto_failure", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "wrong",
     "attack": None, "notes": "Well-formed output, wrong private key (off by one)."},
    {"case_id": "H_BAD_EC_02", "case_class": "honest_crypto_failure", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 2, "condition": "C1", "producer_variant": "wrong",
     "attack": None, "notes": "Well-formed output, wrong private key, seed 2."},
    {"case_id": "H_BAD_CH_01", "case_class": "honest_crypto_failure", "gt_success": False,
     "task": "ChaCha20_Nonce_Repeat", "seed": 1, "condition": "C1", "producer_variant": "wrong",
     "attack": None, "notes": "Well-formed output, wrong recovered plaintext."},
    {"case_id": "H_BAD_CH_02", "case_class": "honest_crypto_failure", "gt_success": False,
     "task": "ChaCha20_Nonce_Repeat", "seed": 2, "condition": "C1", "producer_variant": "wrong",
     "attack": None, "notes": "Well-formed output, wrong recovered plaintext, seed 2."},

    # --- honest execution failure ------------------------------------------
    {"case_id": "H_FAIL_EC_01", "case_class": "honest_execution_failure", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "fail",
     "attack": None, "notes": "Program exits with status 3 before producing output."},
    {"case_id": "H_FAIL_CH_01", "case_class": "honest_execution_failure", "gt_success": False,
     "task": "ChaCha20_Nonce_Repeat", "seed": 1, "condition": "C1", "producer_variant": "fail",
     "attack": None, "notes": "Program exits with status 3 before producing output."},

    # --- honest malformed output -------------------------------------------
    {"case_id": "H_MALFORMED_EC_01", "case_class": "honest_malformed_output", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "malformed",
     "attack": None, "notes": "Program exits 0 but prints a non-JSON line."},

    # --- honest underdetermined target --------------------------------------
    {"case_id": "H_UNDET_EC_01", "case_class": "honest_underdetermined", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C0", "producer_variant": "underdetermined",
     "attack": None, "notes": "C0 instance omits the second signature; target is provably ambiguous."},

    # --- missing evidence ---------------------------------------------------
    {"case_id": "M_MISSING_OBS", "case_class": "missing_evidence", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "correct",
     "attack": "omit_observation", "notes": "Observation record removed before aggregation."},
    {"case_id": "M_MISSING_REF", "case_class": "missing_evidence", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "correct",
     "attack": "omit_reference", "notes": "Reference record removed before aggregation."},

    # --- constructed defensive fixtures ------------------------------------
    {"case_id": "X_IDENTITY", "case_class": "identity_mismatch", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "correct",
     "attack": "identity_swap",
     "notes": "Certificate names a different program than the one executed; digests internally consistent."},
    {"case_id": "X_OUTPUT_SWAP", "case_class": "output_substitution", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "wrong",
     "attack": "output_swap",
     "notes": "Candidate output consumed by the reference comes from a different run; digests updated."},
    {"case_id": "X_STALE_ATTEMPT", "case_class": "stale_attempt", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "correct",
     "attack": "stale_attempt",
     "notes": "Evidence from attempt A presented under attempt B; attempt fields made internally consistent."},
    {"case_id": "X_CONTEXT_CONFLICT", "case_class": "context_conflict", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "correct",
     "attack": "context_conflict",
     "notes": "Observer record signed for a different (target, attempt, epoch) than the claim."},
    {"case_id": "X_REPLAY", "case_class": "replay", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "correct",
     "attack": "replay",
     "notes": "A previously consumed observation record is replayed under a new claim."},
    {"case_id": "X_REF_MISMATCH", "case_class": "reference_mismatch", "gt_success": False,
     "task": "ECDSA_Nonce_Reuse", "seed": 1, "condition": "C1", "producer_variant": "correct",
     "attack": "reference_mismatch",
     "notes": "Reference record reports the predicate true but pins a different stdout digest."},
]

CASE_CLASSES = [
    "honest_success", "honest_crypto_failure", "honest_execution_failure",
    "honest_malformed_output", "honest_underdetermined", "missing_evidence",
    "identity_mismatch", "output_substitution", "stale_attempt",
    "context_conflict", "replay", "reference_mismatch",
]

N_SUCCESS = sum(1 for case in CASES if case["gt_success"])
N_NON_SUCCESS = sum(1 for case in CASES if not case["gt_success"])


def label_table() -> dict[str, Any]:
    """The frozen ground-truth label table (labels for the adjudicator)."""
    return {
        "schema": "e2a-labels/1",
        "case_count": len(CASES),
        "n_success": N_SUCCESS,
        "n_non_success": N_NON_SUCCESS,
        "class_count": len(CASE_CLASSES),
        "classes": list(CASE_CLASSES),
        "labels": [
            {
                "case_id": case["case_id"],
                "case_class": case["case_class"],
                "gt_success": case["gt_success"],
                "task": case["task"],
                "seed": case["seed"],
                "condition": case["condition"],
                "producer_variant": case["producer_variant"],
                "attack": case["attack"],
            }
            for case in CASES
        ],
    }
