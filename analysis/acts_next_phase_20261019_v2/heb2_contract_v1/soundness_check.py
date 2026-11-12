#!/usr/bin/env python3
"""Mechanized soundness check for Contract V2 (preregistration §4).

A seeded mutation corpus is generated from the genuine per-case certificates.
Every mutant is evaluated under both preregistered semantics.  For every mutant
that the contract attributes, the soundness property S1 is re-verified
directly against that mutant's own contents; a violation is a hard failure.

Each mutant is evaluated with a **fresh** aggregator, so the replay ledger is
empty for that evaluation.  This removes a protective mechanism and therefore
makes the check strictly harder on the contract than a normal evaluation.
"""
from __future__ import annotations

import copy
import json
import random
import sys
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
STAGE1_ROOT = HERE.parents[0] / "stage1_e2a"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(STAGE1_ROOT))

from contract import (  # noqa: E402
    SEMANTIC_COMPLETION,
    SEMANTIC_OUTPUT,
    ContractV2,
    soundness_violations,
)

SEED = 20261020
RANDOM_MUTANTS = 200


def _flip_hex(value: str, rng: random.Random) -> str:
    if not value:
        return value
    index = rng.randrange(len(value))
    replacement = rng.choice("0123456789abcdef" + "0123456789abcdef")
    if replacement == value[index]:
        replacement = "0" if value[index] != "0" else "1"
    return value[:index] + replacement + value[index + 1:]


def _observation(bundle: dict[str, Any]) -> dict[str, Any]:
    return bundle["certificate"]["evidence"]["observation"]


def _reference(bundle: dict[str, Any]) -> dict[str, Any]:
    return bundle["certificate"]["evidence"]["reference"]


def mutate_signature_observation(bundle, rng):
    record = _observation(bundle)["record"]
    record["signature_hex"] = _flip_hex(record["signature_hex"], rng)
    return "signature_observation"


def mutate_signature_reference(bundle, rng):
    record = _reference(bundle)["record"]
    record["signature_hex"] = _flip_hex(record["signature_hex"], rng)
    return "signature_reference"


def mutate_key_id(bundle, rng):
    record = _observation(bundle)["record"]
    record["key_id"] = "ed25519-" + "".join(rng.choice("0123456789abcdef") for _ in range(24))
    return "key_id"


def mutate_observation_payload(bundle, rng):
    payload = _observation(bundle)["record"]["payload"]
    payload["parse"]["parsed_candidate_sha256"] = _flip_hex(
        payload["parse"]["parsed_candidate_sha256"] or "0" * 64, rng)
    return "observation_payload"


def mutate_reference_payload(bundle, rng):
    payload = _reference(bundle)["record"]["payload"]
    payload["stdout_sha256"] = _flip_hex(payload["stdout_sha256"] or "0" * 64, rng)
    return "reference_payload"


def mutate_reference_crypto(bundle, rng):
    payload = _reference(bundle)["record"]["payload"]
    payload["crypto_ok"] = False
    payload["verdict"] = "REJECTED"
    return "reference_crypto_flag"


def mutate_certificate_target(bundle, rng):
    bundle["certificate"]["target_id"] = bundle["certificate"]["target_id"] + "-other"
    return "certificate_target_id"


def mutate_certificate_attempt(bundle, rng):
    bundle["certificate"]["attempt_id"] = bundle["certificate"]["attempt_id"] + "-B"
    return "certificate_attempt_id"


def mutate_certificate_epoch(bundle, rng):
    bundle["certificate"]["epoch"] = bundle["certificate"]["epoch"] + 1
    return "certificate_epoch"


def mutate_certificate_artifact(bundle, rng):
    bundle["certificate"]["agent_artifact"]["sha256"] = _flip_hex(
        bundle["certificate"]["agent_artifact"]["sha256"], rng)
    return "certificate_artifact_digest"


def mutate_certificate_candidate(bundle, rng):
    bundle["certificate"]["candidate_output"]["sha256"] = _flip_hex(
        bundle["certificate"]["candidate_output"]["sha256"], rng)
    return "certificate_candidate_digest"


def mutate_delete_observation(bundle, rng):
    bundle["certificate"]["evidence"].pop("observation", None)
    return "delete_observation"


def mutate_delete_reference(bundle, rng):
    bundle["certificate"]["evidence"].pop("reference", None)
    return "delete_reference"


def mutate_claims_proven(bundle, rng):
    bundle["certificate"]["claims"]["attribution"] = "PROVEN"
    return "claims_attribution_proven"


def mutate_claims_not_established(bundle, rng):
    bundle["certificate"]["claims"]["attribution"] = "NOT_ESTABLISHED"
    return "claims_attribution_not_established"


def mutate_swap_evidence(bundle, rng):
    evidence = bundle["certificate"]["evidence"]
    evidence["observation"], evidence["reference"] = evidence["reference"], evidence["observation"]
    return "swap_evidence"


def mutate_drop_context(bundle, rng):
    _observation(bundle).pop("context", None)
    return "drop_observation_context"


def mutate_splice_observation(bundle, rng, donor):
    bundle["certificate"]["evidence"]["observation"] = copy.deepcopy(
        donor["certificate"]["evidence"]["observation"])
    return "splice_observation_from_other_case"


def mutate_splice_reference(bundle, rng, donor):
    bundle["certificate"]["evidence"]["reference"] = copy.deepcopy(
        donor["certificate"]["evidence"]["reference"])
    return "splice_reference_from_other_case"


SINGLE_CASE_OPERATORS: list[tuple[str, Callable[[dict, random.Random], str]]] = [
    ("signature_observation", mutate_signature_observation),
    ("signature_reference", mutate_signature_reference),
    ("key_id", mutate_key_id),
    ("observation_payload", mutate_observation_payload),
    ("reference_payload", mutate_reference_payload),
    ("reference_crypto_flag", mutate_reference_crypto),
    ("certificate_target_id", mutate_certificate_target),
    ("certificate_attempt_id", mutate_certificate_attempt),
    ("certificate_epoch", mutate_certificate_epoch),
    ("certificate_artifact_digest", mutate_certificate_artifact),
    ("certificate_candidate_digest", mutate_certificate_candidate),
    ("delete_observation", mutate_delete_observation),
    ("delete_reference", mutate_delete_reference),
    ("claims_attribution_proven", mutate_claims_proven),
    ("claims_attribution_not_established", mutate_claims_not_established),
    ("swap_evidence", mutate_swap_evidence),
    ("drop_observation_context", mutate_drop_context),
]


def build_corpus(genuine: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build the seeded mutant corpus from the genuine bundles."""
    rng = random.Random(SEED)
    corpus: list[dict[str, Any]] = []
    for index, bundle in enumerate(genuine):
        for name, operator in SINGLE_CASE_OPERATORS:
            mutant = copy.deepcopy(bundle)
            operator(mutant, rng)
            corpus.append({"origin": bundle["case_id"], "operator": name, "bundle": mutant})
        donor = genuine[(index + 1) % len(genuine)]
        for name, operator in (("splice_observation_from_other_case", mutate_splice_observation),
                               ("splice_reference_from_other_case", mutate_splice_reference)):
            mutant = copy.deepcopy(bundle)
            operator(mutant, rng, donor)
            corpus.append({"origin": bundle["case_id"], "operator": name, "bundle": mutant})
    for _ in range(RANDOM_MUTANTS):
        bundle = copy.deepcopy(genuine[rng.randrange(len(genuine))])
        operator = SINGLE_CASE_OPERATORS[rng.randrange(len(SINGLE_CASE_OPERATORS))][1]
        operator(bundle, rng)
        corpus.append({"origin": "random", "operator": "random", "bundle": bundle})
    return corpus


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: soundness_check.py <run_dir> <trust_dir> <out.json>")
    run_dir = Path(sys.argv[1])
    trust_dir = Path(sys.argv[2])
    out_path = Path(sys.argv[3])
    bundle_path = trust_dir / "issuers_public.json"
    policy_path = trust_dir / "trust_policy.json"

    genuine = []
    for case_dir in sorted((run_dir / "cases").iterdir()):
        certificate_path = case_dir / "certificate.e2a.json"
        if not certificate_path.is_file():
            continue
        certificate = json.loads(certificate_path.read_text())
        genuine.append({"case_id": certificate["case_id"], "certificate": certificate})
    if not genuine:
        raise SystemExit(f"no certificates found under {run_dir / 'cases'}")

    genuine_bundles = [{"case_id": item["case_id"], "certificate": item["certificate"]}
                       for item in genuine]

    baseline = []
    for bundle in genuine_bundles:
        for semantic in (SEMANTIC_OUTPUT, SEMANTIC_COMPLETION):
            contract = ContractV2(bundle_path, policy_path, None, semantic)
            decision = contract.evaluate(bundle)
            violations = soundness_violations(bundle, semantic, bundle_path, policy_path)
            baseline.append({
                "case_id": bundle["case_id"], "semantic": semantic,
                "decision": decision["decision"], "reason": decision["reason"],
                "soundness_violations": violations,
            })

    corpus = build_corpus(genuine_bundles)
    accepted = 0
    violations_found = []
    decisions: dict[str, int] = {}
    for mutant in corpus:
        for semantic in (SEMANTIC_OUTPUT, SEMANTIC_COMPLETION):
            contract = ContractV2(bundle_path, policy_path, None, semantic)
            decision = contract.evaluate(mutant["bundle"])
            key = f"{semantic}:{decision['decision']}"
            decisions[key] = decisions.get(key, 0) + 1
            if decision["decision"] != "ATTRIBUTED_SUCCESS":
                continue
            accepted += 1
            violations = soundness_violations(mutant["bundle"], semantic, bundle_path, policy_path)
            if violations:
                violations_found.append({
                    "origin": mutant["origin"], "operator": mutant["operator"],
                    "semantic": semantic, "violations": violations,
                })

    report = {
        "schema": "acts-heb2-soundness/1",
        "seed": SEED,
        "random_mutants": RANDOM_MUTANTS,
        "genuine_cases": len(genuine_bundles),
        "corpus_size": len(corpus),
        "evaluations": len(corpus) * 2,
        "accepted_mutants": accepted,
        "soundness_violations": violations_found,
        "decision_census": dict(sorted(decisions.items())),
        "genuine_baseline": baseline,
        "genuine_violations": [row for row in baseline if row["soundness_violations"]],
    }
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "corpus_size": len(corpus),
        "evaluations": len(corpus) * 2,
        "accepted_mutants": accepted,
        "soundness_violations": len(violations_found),
        "genuine_violations": len(report["genuine_violations"]),
        "decision_census": report["decision_census"],
    }, indent=2, sort_keys=True))
    return 0 if not violations_found and not report["genuine_violations"] else 1


if __name__ == "__main__":
    raise SystemExit(main())