#!/usr/bin/env python3
"""Standalone post-call verifier for one H1-R3 session.

Reads the pre-existing per-session artifacts in CASE_DIR and computes the
independent cryptographic verdict and the certificate/blind checks.

Entry point used after each provider call:
    python3 h1r3_verify_one.py CASE_DIR
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_json(p: Path) -> dict:
    return json.loads(p.read_text())


def reference_verdict(case_dir: Path) -> dict:
    bundle = load_json(case_dir / "reference_bundle.json")
    # Import the existing verifier machinery from the H1-R3 harness.
    sys.path.insert(0, str(HERE))
    import h1r3_reference as ref
    return ref.main_from_bundle(bundle)


def certificate_checks(case_dir: Path) -> dict:
    cert = load_json(case_dir / "certificate.private.json")
    return {
        "schema": cert.get("schema"),
        "attempt_id": cert.get("attempt_id"),
        "task": cert.get("task"),
        "contract_sufficiency_status": cert.get("contract", {}).get("sufficiency_status"),
        "claims_target_effect": cert.get("claims", {}).get("target_effect"),
        "claims_reference_oracle_acceptance": cert.get("claims", {}).get("reference_oracle_acceptance"),
    }


def blind_checks(case_dir: Path) -> dict:
    blind_payload_path = case_dir / "blind_payload.json"
    if not blind_payload_path.is_file():
        return {"status": "NOT_RUN", "reason": "blind_payload.json missing"}
    payload = load_json(blind_payload_path)
    import h1r3_blind_validator as blind
    return blind.main_from_payload(payload)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 h1r3_verify_one.py CASE_DIR")
    case_dir = Path(sys.argv[1])
    if not case_dir.is_dir():
        raise SystemExit(f"case directory not found: {case_dir}")

    reference = reference_verdict(case_dir)
    cert = certificate_checks(case_dir)
    blind = blind_checks(case_dir)

    report = {
        "case_dir": str(case_dir),
        "reference": reference,
        "certificate": cert,
        "blind": blind,
    }
    out = case_dir / "verify_one_report.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"case_dir": str(case_dir), "report_path": str(out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
