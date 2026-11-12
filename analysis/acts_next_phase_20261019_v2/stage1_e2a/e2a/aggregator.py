"""TRUSTED final claim adjudicator (aggregator).

The aggregator is the only component that issues a security claim.  It never
reads the claimant's ``claims`` block when deciding: the decision is derived
from the signed evidence chain and the cryptographic predicate.  That is the
property the Stage 01 validator does not have.

Checks are applied in a **fixed order** (E2A_PREREGISTRATION 12, amendment 2):

  1. presence of the certificate and of both signed records
  2. authenticity of both records (audited ``protected_signing``)
  3. record kind / issuer role
  4. replay of a previously consumed record  -> REJECT
  5. six-field context binding (audited ``context_validator``) -> INCONCLUSIVE
  6. cross-record digest consistency -> REJECT
  7. certificate-claim consistency -> REJECT
  8. reference adjudicator status -> INCONCLUSIVE
  9. cryptographic predicate -> ATTRIBUTED_SUCCESS / REJECT

REJECT means the retained evidence *contradicts* the claim.  INCONCLUSIVE means
required evidence is *absent or unverifiable*.  Missing evidence is never
recorded as a zero-failure; it is INCONCLUSIVE.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import canonical, remediation

CHECK_ORDER = (
    "presence", "record_signature", "kind_role", "replay", "context_binding",
    "cross_record_consistency", "certificate_claim_consistency",
    "reference_status", "predicate",
)

DECISION_SUCCESS = canonical.DECISION_SUCCESS
DECISION_REJECT = canonical.DECISION_REJECT
DECISION_INCONCLUSIVE = canonical.DECISION_INCONCLUSIVE


class Aggregator:
    """Stateful aggregator: holds the explicit replay ledger and trust bundle."""

    def __init__(self, bundle_path: Path, policy_path: Path, ledger_path: Path | None = None):
        self.bundle_path = Path(bundle_path)
        self.policy_path = Path(policy_path)
        self.signing = remediation.protected_signing()
        self.context_module = remediation.context_validator()
        self.policy, self.policy_document = remediation.load_policy(self.policy_path)
        self.replay = self.context_module.ReplayState(max_uses=1)
        self.ledger_path = Path(ledger_path) if ledger_path else None
        self.ledger: list[dict[str, Any]] = []
        if self.ledger_path and self.ledger_path.exists():
            for line in self.ledger_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self.ledger.append(json.loads(line))

    # -- helpers ------------------------------------------------------------

    def clone_for_sensitivity_check(self) -> "Aggregator":
        """Return an aggregator with an identical replay-ledger state.

        Used for the secondary metric S1 (declaration sensitivity).  The two
        S1 evaluations must start from exactly the same ledger state as the
        primary evaluation, otherwise a change in verdict could be caused by
        ledger state rather than by the claimant's assertion.  The replay
        state of the audited ``ReplayState`` dataclass is copied through its
        documented ``_uses`` mapping; the ledger audit trail is not copied
        because the clone never writes to it.
        """
        clone = Aggregator(self.bundle_path, self.policy_path, None)
        clone.replay._uses.update(self.replay._uses)
        return clone

    def _public_key(self, role: str):
        return remediation.public_key_for_role(self.bundle_path, role)

    def _ledger_append(self, context: dict[str, Any], outcome: str) -> None:
        entry = {"context": context, "outcome": outcome}
        self.ledger.append(entry)
        if self.ledger_path:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with self.ledger_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")

    @staticmethod
    def _expected_context(certificate: dict, kind: str, role: str) -> dict[str, Any]:
        return {
            "kind": kind,
            "domain": canonical.DOMAIN,
            "target_id": certificate["target_id"],
            "attempt_id": certificate["attempt_id"],
            "epoch": certificate["epoch"],
            "role": role,
        }

    # -- decision ------------------------------------------------------------

    def evaluate(self, bundle: dict[str, Any]) -> dict[str, Any]:
        """Evaluate one presented certificate bundle and return the decision."""
        certificate = bundle.get("certificate")
        if not isinstance(certificate, dict):
            return self._result(DECISION_INCONCLUSIVE, "certificate-missing", [])
        for field in ("target_id", "attempt_id", "epoch"):
            if field not in certificate:
                return self._result(DECISION_INCONCLUSIVE, f"certificate-{field}-missing", [])

        evidence = certificate.get("evidence")
        if not isinstance(evidence, dict):
            return self._result(DECISION_INCONCLUSIVE, "evidence-missing", [])
        observation = evidence.get("observation")
        reference = evidence.get("reference")
        if not isinstance(observation, dict) or not isinstance(reference, dict):
            return self._result(DECISION_INCONCLUSIVE, "evidence-record-missing", [])

        # 2. authenticity
        for envelope, label in ((observation, "observation"), (reference, "reference")):
            try:
                self.signing.verify_record(envelope["record"], self.bundle_path, self.policy)
            except Exception:
                return self._result(DECISION_INCONCLUSIVE, f"{label}-signature-invalid", [])
            if canonical.sha_object(envelope["record"]["payload"]) is None:  # pragma: no cover
                return self._result(DECISION_INCONCLUSIVE, f"{label}-payload-invalid", [])

        # 3. kind and role
        if observation.get("kind") != canonical.OBSERVATION_KIND or observation.get("issuer_role") != remediation.ROLE_OBSERVER:
            return self._result(DECISION_INCONCLUSIVE, "observation-kind-or-role", [])
        if reference.get("kind") != canonical.REFERENCE_KIND or reference.get("issuer_role") != remediation.ROLE_REFERENCE:
            return self._result(DECISION_INCONCLUSIVE, "reference-kind-or-role", [])

        observation_payload = observation["record"]["payload"]
        reference_payload = reference["record"]["payload"]

        # 4. replay (checked on the record's own signed context)
        for envelope, label in ((observation, "observation"), (reference, "reference")):
            context = envelope.get("context")
            if not isinstance(context, dict):
                return self._result(DECISION_INCONCLUSIVE, f"{label}-context-missing", [])
            if self.replay.uses(context) >= self.replay.max_uses:
                return self._result(DECISION_REJECT, f"{label}-replayed", [])

        # 5. six-field context binding
        for envelope, label, kind, role in (
            (observation, "observation", canonical.OBSERVATION_KIND, remediation.ROLE_OBSERVER),
            (reference, "reference", canonical.REFERENCE_KIND, remediation.ROLE_REFERENCE),
        ):
            context = envelope["context"]
            if envelope["record"]["payload"].get("context") != context:
                return self._result(DECISION_REJECT, f"{label}-payload-context-mismatch", [])
            expected = self._expected_context(certificate, kind, role)
            try:
                self.context_module.validate_signed_context(
                    context, envelope["context_signature_hex"], self._public_key(role),
                    expected, replay_state=self.replay)
            except Exception as exc:
                message = str(exc)
                if "replay" in message:
                    return self._result(DECISION_REJECT, f"{label}-replayed", [])
                return self._result(DECISION_INCONCLUSIVE, f"{label}-context-binding", [])

        # 6. cross-record consistency
        if reference_payload.get("observation_record_sha256") != canonical.sha_object(observation):
            return self._result(DECISION_REJECT, "reference-does-not-adjudicate-this-observation", [])
        if reference_payload.get("stdout_sha256") != observation_payload.get("stdout_sha256"):
            return self._result(DECISION_REJECT, "reference-stdout-pin-mismatch", [])
        # The observer nests the parsed candidate digest under payload["parse"].
        observation_digest = observation_payload.get("parse", {}).get("parsed_candidate_sha256")
        if reference_payload.get("candidate_digest") != observation_digest:
            return self._result(DECISION_REJECT, "reference-candidate-digest-mismatch", [])
        if reference_payload.get("public_target_digest") != observation_payload.get("public_target_digest"):
            return self._result(DECISION_REJECT, "target-digest-mismatch", [])
        if reference_payload.get("target_id") != observation_payload.get("target_id"):
            return self._result(DECISION_REJECT, "target-id-mismatch", [])

        # 7. certificate-claim consistency
        agent_artifact = certificate.get("agent_artifact")
        if not isinstance(agent_artifact, dict) or "sha256" not in agent_artifact:
            return self._result(DECISION_INCONCLUSIVE, "agent-artifact-declaration-missing", [])
        if agent_artifact["sha256"] != observation_payload.get("program_source_sha256"):
            return self._result(DECISION_REJECT, "executed-program-identity-mismatch", [])
        candidate_output = certificate.get("candidate_output")
        if not isinstance(candidate_output, dict) or "sha256" not in candidate_output:
            return self._result(DECISION_INCONCLUSIVE, "candidate-output-declaration-missing", [])
        if candidate_output["sha256"] != observation_digest:
            return self._result(DECISION_REJECT, "candidate-output-substitution", [])

        # 8. reference adjudicator status
        if reference_payload.get("status") != "ADJUDICATED":
            return self._result(DECISION_INCONCLUSIVE, f"reference-status-{reference_payload.get('status')}", [])

        # 9. the cryptographic predicate
        if reference_payload.get("crypto_ok") is True and reference_payload.get("verdict") == "ACCEPTED":
            return self._result(DECISION_SUCCESS, "predicate-true-and-chain-complete", [])

        # The reference could not adjudicate (e.g. stdout pin mismatch) - the
        # evidence is unverifiable rather than contradictory.
        if reference_payload.get("status") != "ADJUDICATED":
            return self._result(DECISION_INCONCLUSIVE, "reference-inconclusive", [])
        return self._result(DECISION_REJECT, "cryptographic-predicate-false", [])

    # -- output --------------------------------------------------------------

    def _result(self, decision: str, reason: str, chain: list[str]) -> dict[str, Any]:
        return {
            "decision": decision,
            "reason": reason,
            "reason_family": self._family(decision, reason),
            "check_order": list(CHECK_ORDER),
            "chain": chain,
        }

    @staticmethod
    def _family(decision: str, reason: str) -> str:
        if decision == DECISION_INCONCLUSIVE:
            return "absent_or_unverifiable"
        if decision == DECISION_SUCCESS:
            return "attributed"
        if "replayed" in reason:
            return "stale_evidence"
        return "contradicted_by_evidence"

    def sign_claim(self, certificate: dict[str, Any], decision: dict[str, Any],
                   keys_dir: Path) -> dict[str, Any]:
        """Emit the signed final attribution claim (required objects 14 and 15)."""
        context = {
            "kind": canonical.CLAIM_KIND,
            "domain": canonical.DOMAIN,
            "target_id": certificate["target_id"],
            "attempt_id": certificate["attempt_id"],
            "epoch": certificate["epoch"],
            "role": remediation.ROLE_AGGREGATOR,
        }
        key_path = _key_path_for_role(keys_dir, remediation.ROLE_AGGREGATOR)
        _key_id, role, private_key = self.signing.load_private_key(key_path)
        context_signature = private_key.sign(self.context_module.canonical_context(context)).hex()
        payload = {
            "case_id": certificate.get("case_id"),
            "target_id": certificate["target_id"],
            "attempt_id": certificate["attempt_id"],
            "epoch": certificate["epoch"],
            "decision": decision["decision"],
            "reason": decision["reason"],
            "reason_family": decision["reason_family"],
            "attributed_success": decision["decision"] == DECISION_SUCCESS,
            "context": context,
        }
        record = self.signing.sign_record(
            key_path,
            self.signing.SignRequest(kind=canonical.CLAIM_KIND, context=canonical.POLICY_CONTEXT,
                                     payload=payload),
            self.policy,
        )
        return {
            "schema": "e2a-signed-record/1",
            "kind": canonical.CLAIM_KIND,
            "issuer_role": role,
            "record": record,
            "context": context,
            "context_signature_hex": context_signature,
        }


def _key_path_for_role(keys_dir: Path, role: str) -> Path:
    for candidate in sorted(Path(keys_dir).glob("*.json")):
        record = json.loads(candidate.read_text(encoding="utf-8"))
        if record.get("role") == role:
            return candidate
    raise KeyError(f"no private key for role {role!r} in {keys_dir}")
