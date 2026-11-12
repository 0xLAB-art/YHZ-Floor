#!/usr/bin/env python3
"""Stage 1 baseline evaluators E0-E2 (ablation ladder).

These are *design classes*, not products.  They exist to isolate which
verification layer contributes what, under one identical bundle set and one
identical decision vocabulary.  They are labelled ``digest_only``,
``signed_digest_only`` and ``signed_context_only`` everywhere so they are
never confused with in-toto, SLSA or any other real provenance product.

  E0  digest_only          file digests only.  This is the "equal hashes in
                            attacker-editable records" design that the
                            independent scientific-controls review identified
                            as insufficient.
  E1  signed_digest_only   E0 + Ed25519 record signatures and role/kind
                            authorization (per-record authenticity, but no
                            binding between records).
  E2  signed_context_only  E1 + signed target/attempt/epoch/role context and
                            the replay ledger (per-record freshness and
                            authorization, but still no cross-record causal
                            join).

  E3  (full)              E2 + the cross-record causal joins, implemented in
                            ``s1_attribution_evaluator.AttributionEvaluator``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from context_validator import ReplayState
from protected_signing import verify_record

from s1_attribution_evaluator import (
    ALWAYS_REQUIRED_KINDS,
    EXPECTED_ROLE_BY_KIND,
    SIGNED_KINDS,
    EvaluationResult,
    RunExpectation,
)
from s1_common import (
    DECISION_INCONCLUSIVE,
    DECISION_REJECT,
    DECISION_SUCCESS,
    KIND_REFERENCE_VERDICT,
    SIGNING_CONTEXT,
    issuer_policy,
    read_json,
)
from s1_verification import check_files, expected_context_for, load_bundle, verify_signed_record


class _LayeredEvaluator:
    """Common machinery: same loading, same presence policy, same vocabulary."""

    use_signatures = False
    use_context = False
    use_joins = False
    name = "base"

    def __init__(self, trust_bundle_path: Path, expectation: RunExpectation,
                 *, replay_state: ReplayState | None = None) -> None:
        self.trust_bundle_path = Path(trust_bundle_path)
        self.expectation = expectation
        self.replay_state = replay_state if replay_state is not None else ReplayState(max_uses=1)
        self.policy = issuer_policy()

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

        for kind in ALWAYS_REQUIRED_KINDS:
            if kind not in index:
                result.missing.append(kind)
                result.reasons.append(f"missing-evidence-kind:{kind}")

        digests, file_missing, file_contradictions, file_reasons = check_files(bundle_root, index)
        result.missing.extend(file_missing)
        result.contradictions.extend(file_contradictions)
        result.reasons.extend(file_reasons)

        payloads: dict[str, dict[str, Any]] = {}
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
            if not self.use_signatures:
                # E0 does not authenticate records at all; it reads whatever
                # the bundle claims.
                payloads[kind] = record.get("payload", {}) if isinstance(record.get("payload"), dict) else {}
                continue
            if not self.use_context:
                try:
                    payload = verify_record(record, self.trust_bundle_path, self.policy)
                except Exception as exc:
                    result.contradictions.append(f"record-verification-failed:{kind}")
                    result.reasons.append(f"record-verification-failed:{kind}:{type(exc).__name__}")
                    continue
                if record.get("kind") != kind:
                    result.contradictions.append(f"record-kind-mismatch:{kind}")
                    result.reasons.append(f"record-kind-mismatch:{kind}")
                    continue
                if record.get("issuer_role") != EXPECTED_ROLE_BY_KIND[kind]:
                    result.contradictions.append(f"record-role-mismatch:{kind}")
                    result.reasons.append(f"record-role-mismatch:{kind}")
                    continue
                if record.get("context") != SIGNING_CONTEXT:
                    result.contradictions.append(f"record-domain-mismatch:{kind}")
                    result.reasons.append(f"record-domain-mismatch:{kind}")
                    continue
                payloads[kind] = payload
                continue
            # E2: full signed-context verification.
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
                payloads[kind] = payload

        ref_facts = payloads.get(KIND_REFERENCE_VERDICT, {}).get("facts", {})
        verdict = ref_facts.get("verdict")

        result.checks = {
            "digests": digests,
            "reference_verdict": verdict,
            "expectation": self.expectation.as_dict(),
        }

        if result.contradictions:
            result.decision = DECISION_REJECT
        elif result.missing:
            result.decision = DECISION_INCONCLUSIVE
        elif verdict != "ACCEPTED":
            result.decision = DECISION_REJECT
            result.reasons.append("reference-verdict-not-accepted")
        else:
            result.decision = DECISION_SUCCESS
        return result


class DigestOnlyEvaluator(_LayeredEvaluator):
    """E0: file digests only."""

    use_signatures = False
    use_context = False
    use_joins = False
    name = "digest_only"


class SignedDigestOnlyEvaluator(_LayeredEvaluator):
    """E1: digests + per-record signatures and role authorization."""

    use_signatures = True
    use_context = False
    use_joins = False
    name = "signed_digest_only"


class SignedContextOnlyEvaluator(_LayeredEvaluator):
    """E2: digests + signatures + signed context binding and replay ledger."""

    use_signatures = True
    use_context = True
    use_joins = False
    name = "signed_context_only"


BASELINE_EVALUATORS = {
    "digest_only": DigestOnlyEvaluator,
    "signed_digest_only": SignedDigestOnlyEvaluator,
    "signed_context_only": SignedContextOnlyEvaluator,
}
