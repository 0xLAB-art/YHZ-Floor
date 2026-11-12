#!/usr/bin/env python3
"""Construct and execute the B2-2 Stage01 submission-boundary experiment.

All cases are built in this new directory from read-only archived/source
inputs. The frozen Stage01 validator and reference verifier are invoked as
subprocesses without modification. The external candidate-binding wrapper is
also a subprocess and is not presented as an existing Stage01 component.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ANA = ROOT / "sp2027" / "analysis"
VALIDATOR = ANA / "contract_sound_stage01_validator_v2.py"
REFERENCE = ANA / "contract_sound_stage01_reference_verifier_v2.py"
WRAPPER = HERE / "external_candidate_binding_wrapper.py"
CLEAN = ANA / "contract_sound_stage01_hardened_v2_20261018" / "stage1" / "clean" / "clean_01"
IAR = ANA / "heb1_crossboundary_20261019" / "iar" / "iar_a_20261019"

PROTECTED = {
    ANA / "RESULTS_LOCK.json": "4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39",
    ANA / "RESULTS_LOCK_H1PC.json": "8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103",
    ROOT / "sp2027" / "paper" / "main.tex": "51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461",
    ROOT / "sp2027" / "paper" / "main.pdf": "fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_sha(value) -> str:
    return hashlib.sha256(json.dumps(value, indent=2, sort_keys=True).encode() + b"\n").hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def parse_last_json(stdout: str):
    for line in reversed(stdout.splitlines()):
        if line.strip().startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                return None
    return None


def run(cmd, stdin_path: Path | None = None):
    with stdin_path.open("rb") if stdin_path else open("/dev/null", "rb") as stdin:
        proc = subprocess.run(cmd, stdin=stdin if stdin_path else subprocess.DEVNULL,
                              capture_output=True, text=True, cwd=str(HERE))
    return {
        "argv": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "verdict": parse_last_json(proc.stdout),
    }


def copy_case(name: str, public_src: Path, private_src: Path,
              target_src: Path, candidate_src: Path,
              add_trace_candidate: str | None = None) -> dict:
    case = HERE / "cases" / name
    if case.exists():
        shutil.rmtree(case)
    (case / "evidence").mkdir(parents=True)
    source_public = json.loads(public_src.read_text())
    source_private = json.loads(private_src.read_text())
    write_json(case / "source_public_certificate.json", source_public)
    write_json(case / "source_private_certificate.json", source_private)
    shutil.copy2(target_src, case / "target_state.private.json")
    shutil.copy2(candidate_src, case / "candidate.json")

    def materialize(cert: dict) -> dict:
        cert = json.loads(json.dumps(cert))
        cert["agent_artifact"]["path"] = str(case / "candidate.json")
        for item in cert.get("evidence", []):
            source = Path(item["path"])
            dest = case / "evidence" / f"{item['kind']}.json"
            shutil.copy2(source, dest)
            item["path"] = str(dest)
            item["sha256"] = sha(dest)
        return cert

    public = materialize(source_public)
    private = materialize(source_private)
    if add_trace_candidate is not None:
        for cert in (public, private):
            by_kind = {item["kind"]: item for item in cert["evidence"]}
            trace_path = Path(by_kind["execution_trace"]["path"])
            trace = json.loads(trace_path.read_text())
            trace["candidate_sha256"] = add_trace_candidate
            write_json(trace_path, trace)
            by_kind["execution_trace"]["sha256"] = sha(trace_path)
            cert["execution"]["trace_hash"] = sha(trace_path)
    public_path = case / "public_certificate.json"
    private_path = case / "private_certificate.json"
    write_json(public_path, public)
    write_json(private_path, private)
    bundle = {
        "case_id": name,
        "target_state_path": str(case / "target_state.private.json"),
        "candidate_path": str(case / "candidate.json"),
        "certificate_path": str(private_path),
    }
    bundle_path = case / "reference_input.json"
    write_json(bundle_path, bundle)
    return {
        "name": name,
        "case_dir": str(case),
        "public_certificate": str(public_path),
        "private_certificate": str(private_path),
        "reference_input": str(bundle_path),
        "candidate_sha256": sha(case / "candidate.json"),
        "public_certificate_sha256": sha(public_path),
        "private_certificate_sha256": sha(private_path),
        "construction": {
            "public_source": str(public_src),
            "private_source": str(private_src),
            "target_source": str(target_src),
            "candidate_source": str(candidate_src),
            "added_trace_candidate_sha256": add_trace_candidate,
        },
    }


def build_cases() -> list[dict]:
    x_candidate_sha = sha(IAR / "x_candidate.json")
    y_candidate_sha = sha(IAR / "y_candidate.json")
    clean_candidate_sha = sha(CLEAN / "candidate.json")
    return [
        copy_case("clean_control", CLEAN / "public_certificate.json",
                  CLEAN / "certificate.private.json",
                  CLEAN / "target_state.private.json", CLEAN / "candidate.json"),
        copy_case("a1_reproduction", IAR / "A1_trace_candidate_splice.public_certificate.json",
                  IAR / "A1_trace_candidate_splice.private_certificate.json",
                  IAR / "y_target_state.private.json", IAR / "y_candidate.json"),
        copy_case("a1b_reproduction", IAR / "A1b_session_binding.public_certificate.json",
                  IAR / "A1b_session_binding.private_certificate.json",
                  IAR / "y_target_state.private.json", IAR / "y_candidate.json"),
        copy_case("candidate_binding_mismatch", IAR / "A1_trace_candidate_splice.public_certificate.json",
                  IAR / "A1_trace_candidate_splice.private_certificate.json",
                  IAR / "y_target_state.private.json", IAR / "y_candidate.json",
                  add_trace_candidate=x_candidate_sha),
        copy_case("candidate_binding_match_control", CLEAN / "public_certificate.json",
                  CLEAN / "certificate.private.json",
                  CLEAN / "target_state.private.json", CLEAN / "candidate.json",
                  add_trace_candidate=clean_candidate_sha),
    ]


def reachability_scan() -> dict:
    runners = [
        ANA / "run_contract_sound_stage01.py",
        ANA / "run_contract_sound_stage01_hardened.py",
        ANA / "run_contract_sound_agent_pilot.py",
        ANA / "run_contract_sound_agent_pilot_free_v2.py",
        ANA / "run_contract_sound_agent_replacement_v1.py",
    ]
    rows = []
    external_patterns = re.compile(r"json\.load\(sys\.stdin\)|argparse|--(?:certificate|bundle|evidence)")
    internal_patterns = re.compile(r"(?:make_certificate|base_certificate|cert\s*=|write_json\(.*certificate)")
    for path in runners:
        text = path.read_text()
        ext = [(i, line.strip()) for i, line in enumerate(text.splitlines(), 1)
               if external_patterns.search(line)]
        internal = [(i, line.strip()) for i, line in enumerate(text.splitlines(), 1)
                    if internal_patterns.search(line)]
        rows.append({"path": str(path), "external_input_matches": ext,
                     "internal_certificate_matches": internal[:20]})
    no_external = all(not row["external_input_matches"] for row in rows)
    return {
        "determination": "NOT_REACHABLE_IN_CURRENT_PIPELINE" if no_external else "REQUIRES_REVIEW",
        "basis": "read-only source scan; no campaign runner was executed",
        "runners": rows,
    }


def v3_full_comparability() -> dict:
    return {
        "status": "NOT_COMPARABLE",
        "system": str(ANA / "experiment_b_20261019" / "eb_v3_full.py"),
        "reason": "Stage01 format cannot satisfy frozen V3-full input contract without adding a separate authenticated HEB1-signed adapter; B2-2 does not rerun or redesign IAR-B/IAR-C.",
        "missing_contract_elements": [
            "heb1-signed/1 certificate schema and request.json",
            "Ed25519 detached signatures and external trust anchor",
            "six evidence kinds including reference_acceptance",
            "V3-full private/public case layout",
        ],
        "action": "not invoked; no V3-full verdict is claimed",
    }


def run_case(case: dict) -> dict:
    pub = Path(case["public_certificate"])
    private = Path(case["private_certificate"])
    bundle = Path(case["reference_input"])
    original_val = run([sys.executable, str(VALIDATOR)], stdin_path=pub)
    original_ref = run([sys.executable, str(REFERENCE), str(bundle)])
    wrapper = run([sys.executable, str(WRAPPER), str(pub)])
    return {
        "case": case,
        "original_validator": original_val,
        "original_reference": original_ref,
        "external_binding_wrapper": wrapper,
    }


def main() -> int:
    protected_before = {str(p): sha(p) for p in PROTECTED}
    component_hashes = {"validator": sha(VALIDATOR), "reference": sha(REFERENCE),
                        "wrapper": sha(WRAPPER), "protocol": sha(HERE / "B2_2_PROTOCOL.md")}
    expected_component_hashes = {
        "validator": "f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a",
        "reference": "15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b",
    }
    component_integrity = {k: component_hashes[k] == v for k, v in expected_component_hashes.items()}
    cases = build_cases()
    raw_results = [run_case(case) for case in cases]
    reachability = reachability_scan()
    v3 = v3_full_comparability()
    protected_after = {str(p): sha(p) for p in PROTECTED}
    integrity = {
        "component_hashes": component_hashes,
        "component_expected_match": component_integrity,
        "protected_before": protected_before,
        "protected_after": protected_after,
        "protected_unchanged": protected_before == protected_after and protected_after == {str(p): v for p, v in PROTECTED.items()},
        "manifest": {"model_calls": 0, "provider_calls": 0, "network_calls": 0, "spend_usd": 0},
    }
    results = {
        "schema": "b2-2-stage01-results/1",
        "experiment": "B2-2 constructed untrusted submission through real Stage01 components",
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "protocol": str(HERE / "B2_2_PROTOCOL.md"),
        "cases": raw_results,
        "v3_full_comparison": v3,
        "reachability": reachability,
        "integrity": integrity,
        "determination": {
            "reproduction": "A1 and A1b outcomes are reproduced through the frozen real components; clean is reproduced as a positive control.",
            "repair_validation": "The external wrapper rejects the constructed semantic candidate-to-execution mismatch and accepts the matching positive control; this validates the wrapper, not a repair of the original components.",
            "authenticated_baseline_comparison": "NOT_PERFORMED_IN_B2_2; V3-full is NOT_COMPARABLE to the Stage01 input contract without a separate authenticated adapter.",
            "operational_exploitability": "NOT_DEMONSTRATED",
            "reachability": reachability["determination"],
            "novelty": "NOT_ESTABLISHED; this is a real-component reproduction/repair-boundary measurement and may only reconfirm IAR-A.",
        },
    }
    out = HERE / "B2_2_RESULTS.json"
    write_json(out, results)
    results_sha = sha(out)
    summary = {
        "results": str(out), "results_sha256": results_sha,
        "component_hashes": component_hashes,
        "protected_unchanged": integrity["protected_unchanged"],
        "reachability": reachability["determination"],
        "v3_full": v3["status"],
        "cases": [
            {"name": row["case"]["name"],
             "validator": row["original_validator"]["verdict"],
             "reference": row["original_reference"]["verdict"],
             "wrapper": row["external_binding_wrapper"]["verdict"]}
            for row in raw_results
        ],
    }
    write_json(HERE / "B2_2_SUMMARY.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if integrity["protected_unchanged"] and all(component_integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
