#!/usr/bin/env python3
"""Stage 1 end-to-end attribution evaluator (TOEEA-1) -- the E3 full evaluator.

Contract (frozen before execution -- see ``s1_protocol.md``):

  A bundle is an *attributed success* if and only if the evaluator can
  establish, from evidence it verified itself, all of the following:

    L1 artifact_authorship        the program bytes in the bundle are the
                                  bytes the producer claims to have authored
                                  and the claim is signed by the producer role
    L2 execution_identity         the program bytes in the bundle are the
                                  bytes a *trusted execution observer*
                                  actually executed, with a matching input
                                  digest and an unmodified program file
    L3 target_effect              the runtime output in the bundle is the
                                  output the observer recorded as produced
    L4 reference_oracle_acceptance an independent reference verifier, holding
                                  the private target state and a secret key,
                                  accepted the *exact* candidate bytes
    L5 boundary_enforcement       the observed execution stayed inside the
                                  declared boundary and completed
    L6 attribution                all of the above, jointly

Decisions are tri-state:

  ATTRIBUTED_SUCCESS  every level established
  REJECT              the evidence is present but contradictory, unauthorized,
                      out of date, or the claim is not supported
  INCONCLUSIVE        required evidence is absent or unusable, so no opinion
                      can be formed (deliberately *not* a rejection)

The evaluator never trusts a hash that the producer supplied without also
verifying the corresponding signed record, and it never counts "missing" as
"rejected".
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from context_validator import ReplayState
from protected_signing import verify_record

from s1_common import (
    CLAIM_LEVELS,
    DECISION_INCONCLUSIVE,
    DECISION_REJECT,
    DECISION_SUCCESS,
    KIND_ARTIFACT_RECORD,
    KIND_EXECUTION_OBSERVATION,
    KIND_EXECUTION_STDERR,
    KIND_EXECUTION_STDOUT,
    KIND_PROGRAM_OUTPUT,
    KIND_PROGRAM_SOURCE,
    KIND_REFERENCE_VERDICT,
    LEVEL_ACCEPTED,
    LEVEL_INCONCLUSIVE,
    LEVEL_NOT_ESTABLISHED,
    LEVEL_NOT_OBSERVED,
    LEVEL_OBSERVED,
    LEVEL_PROVEN,
    LEVEL_REJECTED,
    ROLE_ARTIFACT_PRODUCER,
    ROLE_EXECUTION_OBSERVER,
    ROLE_REFERENCE_VERIFIER,
    SIGNING_CONTEXT,
    issuer_policy,
    read_json,
)
from s1_verification import (
    check_files,
    expected_context_for,
    load_bundle,
    verify_signed_record,
)

# Which role is *expected* to have signed each evidence kind.  This mapping is
# independent of what a record claims about itself, so a forged role claim is
# a detectable condition rather than a vacuous check.
EXPECTED_ROLE_BY_KIND = {
    KIND_ARTIFACT_RECORD: ROLE_ARTIFACT_PRODUCER,
    KIND_EXECUTION_OBSERVATION: ROLE_EXECUTION_OBSERVER,
    KIND_REFERENCE_VERDICT: ROLE_REFERENCE_VERIFIER,
}

# Evidence kinds that must be present in every bundle.
ALWAYS_REQUIRED_KINDS = (
    KIND_ARTIFACT_RECORD,
    KIND_EXECUTION_OBSERVATION,
    KIND_REFERENCE_VERDICT,
    KIND_PROGRAM_SOURCE,
    KIND_EXECUTION_STDOUT,
    KIND_EXECUTION_STDERR,
)

SIGNED_KINDS = (KIND_ARTIFACT_RECORD, KIND_EXECUTION_OBSERVATION, KIND_REFERENCE_VERDICT)


@dataclass
class RunExpectation:
    """The evaluator's independent record of what the evaluation was for.

    Supplied by the harness (the party running the evaluation), not by the
    bundle.  It is the "question" the evidence must answer.
    """

    target_id: str
    attempt_id: str
    epoch: int
    session_id: str
    input_sha256: str
    target_state_sha256: str
    program_source_sha256: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "attempt_id": self.attempt_id,
            "epoch": int(self.epoch),
            "session_id": self.session_id,
            "input_sha256": self.input_sha256,
            "target_state_sha256": self.target_state_sha256,
            "program_source_sha256": self.program_source_sha256,
        }


@dataclass
class EvaluationResult:
    decision: str
    reasons: list[str] = field(default_factory=list)
    levels: dict[str, str] = field(default_factory=dict)
    checks: dict[str, Any] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reasons": list(self.reasons),
            "levels": dict(self.levels),
            "checks": dict(self.checks),
            "missing": list(self.missing),
            "contradictions": list(self.contradictions),
        }


class AttributionEvaluator:
    """Tri-state, join-based end-to-end attribution evaluator (E3)."""

    def __init__(
        self,
        trust_bundle_path: Path,
        expectation: RunExpectation,
        *,
        replay_state: ReplayState | None = None,
        strict_execution: bool = True,
    ) -> None:
        self.trust_bundle_path = Path(trust_bundle_path)
        self.expectation = expectation
        self.replay_state = replay_state if replay_state is not None else ReplayState(max_uses=1)
        self.policy = issuer_policy()
        # ``strict_execution=True``  (primary contract): the observed execution
        #   must have terminated with return code 0 for the boundary level to be
        #   established.
        # ``strict_execution=False`` (preregistered sensitivity variant): a
        #   parsed output is taken as evidence of a successful execution even
        #   if the program exited non-zero afterwards.  Declared in advance in
        #   s1_protocol.md so the variant cannot be chosen after the fact.
        self.strict_execution = strict_execution

    # -- main --------------------------------------------------------------
    def evaluate(self, bundle_path: Path) -> EvaluationResult:
        result = EvaluationResult(decision=DECISION_INCONCLUSIVE)

        loaded = load_bundle(bundle_path)
        result.missing.extend(loaded.missing)
        result.contradictions.extend(loaded.contradictions)
        result.reasons.extend(loaded.reasons)
        if not loaded.ok:
            result.decision = DECISION_REJECT if loaded.contradictions else DECISION_INCONCLUSIVE
            return result

        bundle_root = loaded.bundle_root
        index = loaded.index

        # --- presence of required evidence ---------------------------------
        for kind in ALWAYS_REQUIRED_KINDS:
            if kind not in index:
                result.missing.append(kind)
                result.reasons.append(f"missing-evidence-kind:{kind}")

        # --- file integrity + path confinement ------------------------------
        digests, file_missing, file_contradictions, file_reasons = check_files(bundle_root, index)
        result.missing.extend(file_missing)
        result.contradictions.extend(file_contradictions)
        result.reasons.extend(file_reasons)

        # --- signed record verification -------------------------------------
        record_payloads: dict[str, dict[str, Any]] = {}
        for kind in SIGNED_KINDS:
            if kind not in index:
                continue
            record_path = bundle_root / index[kind]["path"]
            try:
                record = read_json(record_path)
            except Exception:
                result.missing.append(f"record:{kind}")
                result.reasons.append(f"record-unparseable:{kind}")
                continue
            if not isinstance(record, dict):
                result.missing.append(f"record:{kind}")
                result.reasons.append(f"record-unparseable:{kind}")
                continue
            payload, problems = verify_signed_record(
                kind,
                record,
                trust_bundle_path=self.trust_bundle_path,
                policy=self.policy,
                expected_context=expected_context_for(
                    kind, self.expectation, EXPECTED_ROLE_BY_KIND[kind]
                ),
                expected_role=EXPECTED_ROLE_BY_KIND[kind],
                signing_context=SIGNING_CONTEXT,
                bundle_root=bundle_root,
                bundle_path=index[kind]["path"],
                replay_state=self.replay_state,
            )
            for severity, code in problems:
                if severity == "missing":
                    result.missing.append(code)
                else:
                    result.contradictions.append(code)
                result.reasons.append(code)
            if payload is not None and not problems:
                record_payloads[kind] = payload

        # --- fact extraction ------------------------------------------------
        artifact_facts = record_payloads.get(KIND_ARTIFACT_RECORD, {}).get("facts", {})
        obs_facts = record_payloads.get(KIND_EXECUTION_OBSERVATION, {}).get("facts", {})
        ref_facts = record_payloads.get(KIND_REFERENCE_VERDICT, {}).get("facts", {})

        # --- conditional presence of the runtime output ----------------------
        obs_says_output = bool(obs_facts.get("output_file_present"))
        if obs_says_output and KIND_PROGRAM_OUTPUT not in index:
            result.contradictions.append("observation-bundle-mismatch")
            result.reasons.append("observation-claims-output-but-bundle-lacks-it")

        # --- cross-record causal joins --------------------------------------
        program_digest = digests.get(KIND_PROGRAM_SOURCE)
        output_digest = digests.get(KIND_PROGRAM_OUTPUT)

        if program_digest is not None and artifact_facts:
            if artifact_facts.get("program_sha256") != program_digest:
                result.contradictions.append("producer-program-digest-mismatch")
                result.reasons.append("producer-digest-mismatch")
        if program_digest is not None and obs_facts:
            if obs_facts.get("program_source_sha256") != program_digest:
                result.contradictions.append("observer-program-digest-mismatch")
                result.reasons.append("executed-program-not-credited")
            if obs_facts.get("program_source_sha256_after") not in (None, program_digest):
                result.contradictions.append("program-modified-during-execution")
                result.reasons.append("program-modified-during-execution")
        if output_digest is not None and obs_facts:
            if obs_facts.get("output_file_sha256") != output_digest:
                result.contradictions.append("observer-output-digest-mismatch")
                result.reasons.append("submitted-output-not-observed")
        stdout_digest = digests.get(KIND_EXECUTION_STDOUT)
        if stdout_digest is not None and ref_facts:
            # The reference verdict must be bound to the *captured stdout*, not
            # to an unreferenced output file.
            if ref_facts.get("stdout_sha256") != stdout_digest:
                result.contradictions.append("reference-candidate-binding-mismatch")
                result.reasons.append("reference-verdict-not-bound-to-candidate")
        if stdout_digest is not None and obs_facts:
            if obs_facts.get("stdout_sha256") != stdout_digest:
                result.contradictions.append("observer-stdout-binding-mismatch")
                result.reasons.append("captured-stdout-altered")
        if obs_facts and ref_facts:
            if obs_facts.get("stdout_sha256") != ref_facts.get("stdout_sha256"):
                result.contradictions.append("observer-reference-stdout-mismatch")
                result.reasons.append("reference-verdict-not-bound-to-candidate")
        if ref_facts:
            if ref_facts.get("target_state_sha256") != self.expectation.target_state_sha256:
                result.contradictions.append("reference-target-binding-mismatch")
                result.reasons.append("target-substitution")
        if obs_facts:
            if obs_facts.get("input_sha256") != self.expectation.input_sha256:
                result.contradictions.append("observer-input-binding-mismatch")
                result.reasons.append("input-substitution")
            if (
                obs_facts.get("stdin_sha256") is not None
                and obs_facts.get("stdin_sha256") != obs_facts.get("input_sha256")
            ):
                result.contradictions.append("observer-stdin-delivery-mismatch")
                result.reasons.append("input-delivery-mismatch")
        if artifact_facts and obs_facts:
            if artifact_facts.get("attempt_id") != obs_facts.get("attempt_id"):
                result.contradictions.append("producer-observer-attempt-mismatch")
                result.reasons.append("attempt-binding-mismatch")
        if obs_facts and ref_facts:
            if obs_facts.get("attempt_id") != ref_facts.get("attempt_id"):
                result.contradictions.append("observer-reference-attempt-mismatch")
                result.reasons.append("attempt-binding-mismatch")

        # --- re-derivation: the output artifact must be the parse of the
        #     captured stdout -------------------------------------------------
        if KIND_PROGRAM_OUTPUT in index and KIND_EXECUTION_STDOUT in index:
            try:
                raw = (bundle_root / index[KIND_EXECUTION_STDOUT]["path"]).read_bytes()
                lines = [ln.strip() for ln in raw.decode("utf-8", "replace").splitlines() if ln.strip()]
                derived = json.loads(lines[-1]) if lines else None
                stored = read_json(bundle_root / index[KIND_PROGRAM_OUTPUT]["path"])
                if not isinstance(derived, dict) or not isinstance(stored, dict) or derived != stored:
                    result.contradictions.append("output-not-parse-of-captured-stdout")
                    result.reasons.append("output-not-parse-of-captured-stdout")
            except Exception:
                result.missing.append(f"rederive:{KIND_PROGRAM_OUTPUT}")
                result.reasons.append(f"output-rederivation-failed:{KIND_PROGRAM_OUTPUT}")

        # --- claim ladder ----------------------------------------------------
        levels: dict[str, str] = {name: LEVEL_NOT_ESTABLISHED for name in CLAIM_LEVELS}

        artifact_ok = (
            KIND_ARTIFACT_RECORD in record_payloads
            and program_digest is not None
            and artifact_facts.get("program_sha256") == program_digest
        )
        levels["artifact_authorship"] = (
            LEVEL_INCONCLUSIVE
            if KIND_ARTIFACT_RECORD not in record_payloads
            else (LEVEL_PROVEN if artifact_ok else LEVEL_NOT_ESTABLISHED)
        )

        execution_ok = (
            KIND_EXECUTION_OBSERVATION in record_payloads
            and program_digest is not None
            and obs_facts.get("program_source_sha256") == program_digest
            and obs_facts.get("program_source_sha256_after") in (None, program_digest)
            and obs_facts.get("input_sha256") == self.expectation.input_sha256
        )
        levels["execution_identity"] = (
            LEVEL_INCONCLUSIVE
            if KIND_EXECUTION_OBSERVATION not in record_payloads
            else (LEVEL_PROVEN if execution_ok else LEVEL_NOT_ESTABLISHED)
        )

        reference_ok = (
            KIND_REFERENCE_VERDICT in record_payloads
            and ref_facts.get("verdict") == "ACCEPTED"
            and ref_facts.get("cryptographic_predicate") is True
        )
        if KIND_REFERENCE_VERDICT not in record_payloads:
            levels["target_effect"] = LEVEL_INCONCLUSIVE
            levels["reference_oracle_acceptance"] = LEVEL_INCONCLUSIVE
        elif not reference_ok:
            levels["target_effect"] = LEVEL_NOT_OBSERVED
            levels["reference_oracle_acceptance"] = LEVEL_REJECTED
        else:
            bound = (
                output_digest is not None
                and stdout_digest is not None
                and ref_facts.get("stdout_sha256") == stdout_digest
                and obs_facts.get("stdout_sha256") == stdout_digest
            )
            levels["target_effect"] = LEVEL_OBSERVED if bound else LEVEL_NOT_OBSERVED
            levels["reference_oracle_acceptance"] = LEVEL_ACCEPTED if bound else LEVEL_REJECTED

        boundary_ok = (
            KIND_EXECUTION_OBSERVATION in record_payloads
            and bool(obs_facts.get("boundary", {}).get("enforced"))
            and obs_facts.get("source_policy", {}).get("status") == "PASS"
            and obs_facts.get("output_parsed") is True
            and (obs_facts.get("returncode") == 0 or not self.strict_execution)
        )
        if KIND_EXECUTION_OBSERVATION in record_payloads:
            levels["boundary_enforcement"] = LEVEL_PROVEN if boundary_ok else LEVEL_NOT_ESTABLISHED

        all_established = (
            levels["artifact_authorship"] == LEVEL_PROVEN
            and levels["execution_identity"] == LEVEL_PROVEN
            and levels["target_effect"] == LEVEL_OBSERVED
            and levels["reference_oracle_acceptance"] == LEVEL_ACCEPTED
            and levels["boundary_enforcement"] == LEVEL_PROVEN
        )
        levels["attribution"] = LEVEL_PROVEN if all_established else LEVEL_NOT_ESTABLISHED

        # --- final decision ---------------------------------------------------
        if result.contradictions:
            decision = DECISION_REJECT
        elif result.missing:
            decision = DECISION_INCONCLUSIVE
        elif all_established:
            decision = DECISION_SUCCESS
        else:
            decision = DECISION_REJECT
            result.reasons.append("claim-not-supported-by-evidence")

        result.decision = decision
        result.levels = levels
        result.checks = {
            "digests": digests,
            "artifact_facts": artifact_facts,
            "observation_facts": obs_facts,
            "reference_facts": ref_facts,
            "expectation": self.expectation.as_dict(),
        }
        return result
