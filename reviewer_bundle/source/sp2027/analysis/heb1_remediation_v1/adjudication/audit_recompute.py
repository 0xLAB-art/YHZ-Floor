#!/usr/bin/env python3
"""Read-only integrity and common-contract recomputation helpers.

This module parses preserved artifacts only.  It never invokes a validator,
provider, network, or historical campaign runner.  ``INCONCLUSIVE`` is used
when the available bytes cannot establish a correspondence; it is not a
claim of semantic equivalence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

HONEST_FAMILIES = frozenset({"S1", "S2", "S3", "S13"})
PARTIAL_FAMILIES = frozenset({"S13"})
MALFORMED_FAMILY = "S15"


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _target_fields(target: Mapping[str, Any]) -> dict[str, Any]:
    """Return all target fields, including primitive-specific crypto fields."""
    return dict(target)


def check_target_correspondence(
    public_target: Mapping[str, Any], private_entry: Mapping[str, Any],
    public_artifact_sha256: str | None = None,
) -> dict[str, Any]:
    """Compare public target bytes with private target state and hash metadata."""
    state = private_entry.get("state")
    if not isinstance(state, Mapping):
        return {"status": "INCONCLUSIVE", "reasons": ["private target state missing"]}
    public_fields = _target_fields(public_target)
    private_fields = _target_fields(state)
    reasons: list[str] = []
    if public_fields != private_fields:
        reasons.append("public/private target fields differ, including crypto fields")
    expected_hash = private_entry.get("sha256")
    target_hash = hashlib.sha256(_canonical(public_target)).hexdigest()
    if not isinstance(expected_hash, str):
        reasons.append("private target hash missing")
    elif public_artifact_sha256 is not None and expected_hash != public_artifact_sha256:
        reasons.append("public certificate and private target hashes differ")
    return {"status": "PASS" if not reasons else "FAIL", "reasons": reasons,
            "public_target_sha256": target_hash, "private_target_sha256": expected_hash}


def audit_heb_cases(cases_root: Path, private_root: Path) -> dict[str, Any]:
    """Audit preserved HEB public/private case correspondence without reruns."""
    records: list[dict[str, Any]] = []
    for public_dir in sorted(cases_root.glob("*/*/public")):
        case_id = public_dir.parent.name
        private_dir = private_root / public_dir.parent.parent.name / case_id
        public, public_error = load_json(public_dir / "target.json")
        certificate, certificate_error = load_json(public_dir / "certificate.json")
        private, private_error = load_json(private_dir / "targets.json")
        record: dict[str, Any] = {"case_id": case_id, "status": "INCONCLUSIVE", "reasons": []}
        if (public_error or private_error or certificate_error or
                not isinstance(public, Mapping) or not isinstance(private, Mapping) or
                not isinstance(certificate, Mapping)):
            record["reasons"] = [x for x in (public_error, private_error, certificate_error) if x] or ["malformed target files"]
        else:
            target_id = private.get("cert_target_id")
            entries = private.get("targets", {})
            entry = entries.get(target_id) if isinstance(entries, Mapping) else None
            cert_target_hash = certificate.get("target", {}).get("artifact_sha256")
            record.update(check_target_correspondence(public, entry or {}, cert_target_hash))
        records.append(record)
    failures = [r for r in records if r["status"] == "FAIL"]
    return {"integrity_status": "PASS" if records and not failures else "FAIL" if failures else "INCONCLUSIVE",
            "cases": len(records), "failures": failures, "records": records}


def compare_certificate_pair(public_path: Path, private_path: Path) -> dict[str, Any]:
    """Report byte/JSON differences; do not infer public/private equivalence."""
    public, public_error = load_json(public_path)
    private, private_error = load_json(private_path)
    if public_error or private_error or not isinstance(public, Mapping) or not isinstance(private, Mapping):
        return {"status": "INCONCLUSIVE", "differences": [x for x in (public_error, private_error) if x]}
    differences = sorted(_diff_paths(public, private))
    return {"status": "PASS", "differences": differences,
            "public_sha256": sha256_file(public_path), "private_sha256": sha256_file(private_path)}


def audit_iar_a_certificates(directory: Path) -> dict[str, Any]:
    """Compare every preserved IAR-A public/private certificate pair."""
    pairs = []
    for public_path in sorted(directory.glob("*.public_certificate.json")):
        private_path = public_path.with_name(public_path.name.replace(
            ".public_certificate.json", ".private_certificate.json"))
        comparison = compare_certificate_pair(public_path, private_path)
        pairs.append({"name": public_path.stem.replace(".public_certificate", ""), **comparison})
    failures = [pair for pair in pairs if pair["status"] == "FAIL"]
    inconclusive = [pair for pair in pairs if pair["status"] == "INCONCLUSIVE"]
    status = "PASS" if pairs and not failures and not inconclusive else "FAIL" if failures else "INCONCLUSIVE"
    return {"integrity_status": status, "pairs": len(pairs), "failures": failures,
            "inconclusive": inconclusive, "records": pairs,
            "limitation": "Differences are reported; no public/private semantic equivalence is inferred."}


def _diff_paths(left: Any, right: Any, path: str = "$") -> set[str]:
    if type(left) is not type(right):
        return {path}
    if isinstance(left, Mapping):
        paths: set[str] = set()
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}"
            if key not in left or key not in right:
                paths.add(child)
            else:
                paths.update(_diff_paths(left[key], right[key], child))
        return paths
    if isinstance(left, list):
        return {path} if left != right else set()
    return {path} if left != right else set()


def recompute_common_contract(
    results: Mapping[str, Any],
    honest_families: frozenset[str] = HONEST_FAMILIES,
    partial_families: frozenset[str] = PARTIAL_FAMILIES,
) -> dict[str, Any]:
    """Recompute metrics with explicit malformed/substantive denominators."""
    cases = results.get("per_case")
    if not isinstance(cases, list):
        return {"integrity_status": "INCONCLUSIVE", "errors": ["per_case is not a list"]}
    validation_errors = _validate_rows(cases)
    if validation_errors:
        return {"integrity_status": "INCONCLUSIVE", "errors": validation_errors,
                "limitations": ["no rates are emitted when a retained verdict is missing or malformed"]}
    malformed = [case for case in cases if case.get("adj", {}).get("malformed") is True]
    substantive = [case for case in cases if case.get("adj", {}).get("malformed") is not True]
    attack = [case for case in substantive if case.get("family") not in honest_families]
    honest = [case for case in substantive if case.get("family") in honest_families]
    full_honest = [case for case in honest if case.get("requested") == 6]
    partial = [case for case in honest if case.get("family") in partial_families
               and case.get("requested") <= case.get("adj", {}).get("supported", -1)
               and case.get("requested", 6) < 6]
    systems = sorted({name for case in cases for name in case.get("asserted", {})})
    metrics: dict[str, Any] = {}
    for system in systems:
        metrics[system] = {
            "false_promotion": _rate(attack, lambda c: _false_promotion(c, system)),
            "level6_false_promotion": _rate(attack, lambda c: _level6_promotion(c, system)),
            "overclaim": _rate(substantive, lambda c: _overclaim(c, system)),
            "false_reject_honest": _rate(full_honest, lambda c: not _accepted(c, system)),
            "raw_rejection_coverage": _rate(partial, lambda c: not _accepted(c, system)),
            "partial_acceptance": {"numerator": 0, "denominator": len(partial),
                                   "status": "N/A"} if system == "v2"
                                   else _partial_rate(partial, system),
        }
    expected_cases = results.get("metrics", {}).get("cases")
    errors = [] if expected_cases in (None, len(cases)) else ["reported case count differs from per_case"]
    return {"integrity_status": "PASS" if not errors else "FAIL", "denominators": {
        "all": len(cases), "malformed": len(malformed), "substantive": len(substantive),
        "attack_substantive": len(attack), "honest_substantive": len(honest),
        "partial_claimable": len(partial), "honest_full_claims": len(full_honest)},
        "metrics": metrics, "errors": errors,
        "limitations": ["malformed cases are excluded from substantive rates",
                        "partial_acceptance is N/A when partial_claimable is zero"]}


def _validate_rows(cases: list[Any]) -> list[str]:
    errors: list[str] = []
    cohort_systems: set[str] | None = None
    for index, case in enumerate(cases):
        if not isinstance(case, Mapping):
            errors.append(f"case[{index}] is not an object")
            continue
        required = ("family", "adj", "requested", "systems", "asserted", "system_levels")
        if (any(key not in case for key in required)
                or not isinstance(case["systems"], Mapping)
                or not isinstance(case["asserted"], Mapping)
                or not isinstance(case["adj"], Mapping)
                or not _bounded_int(case["requested"], 1, 6)
                or not isinstance(case["family"], str)
                or not isinstance(case["adj"].get("malformed"), bool)
                or not _bounded_int(case["adj"].get("supported"), 0, 6)
                or not case["systems"]
                or set(case["systems"]) != set(case["asserted"])
                or not isinstance(case["system_levels"], Mapping)):
            errors.append(f"case[{index}] missing retained verdict fields")
            continue
        current_systems = set(case["systems"])
        if cohort_systems is None:
            cohort_systems = current_systems
        elif current_systems != cohort_systems:
            errors.append(f"case[{index}] system cohort differs from other rows")
        for system, decision in case["systems"].items():
            if decision not in {"ACCEPT", "ACCEPTED", "EMIT", "REJECT"}:
                errors.append(f"case[{index}] {system} has missing/invalid decision")
            if system not in case["asserted"]:
                errors.append(f"case[{index}] {system} missing asserted level")
            asserted = case["asserted"][system]
            if asserted is not None and not _bounded_int(asserted, 0, 6):
                errors.append(f"case[{index}] {system} has invalid asserted level")
            if decision in {"ACCEPT", "ACCEPTED", "EMIT"} and asserted is None:
                errors.append(f"case[{index}] {system} accepted without asserted level")
    return errors


def _bounded_int(value: Any, minimum: int, maximum: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum


def _accepted(case: Mapping[str, Any], system: str) -> bool:
    return case["systems"].get(system) in {"ACCEPT", "ACCEPTED", "EMIT"}


def _emitted(case: Mapping[str, Any], system: str) -> int | None:
    if not _accepted(case, system):
        return None
    value = case["asserted"].get(system)
    return value if isinstance(value, int) else None


def _false_promotion(case: Mapping[str, Any], system: str) -> bool:
    emitted = _emitted(case, system)
    supported = case["adj"].get("supported")
    return (emitted is not None and emitted >= case["requested"]
            and isinstance(supported, int) and supported < case["requested"])


def _level6_promotion(case: Mapping[str, Any], system: str) -> bool:
    emitted = _emitted(case, system)
    supported = case["adj"].get("supported")
    return emitted == 6 and isinstance(supported, int) and supported < 6


def _overclaim(case: Mapping[str, Any], system: str) -> bool:
    emitted = _emitted(case, system)
    supported = case["adj"].get("supported")
    return emitted is not None and isinstance(supported, int) and emitted > supported


def _rate(cases: list[Mapping[str, Any]], predicate: Any) -> dict[str, Any]:
    return {"numerator": sum(predicate(case) for case in cases), "denominator": len(cases),
            "status": "N/A" if not cases else "computed"}


def _partial_rate(cases: list[Mapping[str, Any]], system: str) -> dict[str, Any]:
    return _rate(cases, lambda case: _emitted(case, system) == case.get("requested"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    args = parser.parse_args(argv)
    results, error = load_json(args.results)
    if error or not isinstance(results, Mapping):
        print(json.dumps({"integrity_status": "INCONCLUSIVE", "errors": [error or "not an object"]}))
        return 1
    report = recompute_common_contract(results)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("integrity_status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
