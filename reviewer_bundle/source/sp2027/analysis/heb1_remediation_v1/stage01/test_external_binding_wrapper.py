from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
WRAPPER = HERE / "external_binding_wrapper.py"
TEMPLATE = (HERE.parents[1] / "experiment_b_20261019" / "b2_2_stage01" / "cases" / "clean_control" / "public_certificate.json")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_case(tmp_path: Path, trace_value: str | None = None) -> Path:
    source = json.loads(TEMPLATE.read_text())
    case = tmp_path / "case"
    evidence_dir = case / "evidence"
    evidence_dir.mkdir(parents=True)
    candidate = case / "candidate.json"
    candidate.write_text('{"candidate_output":"not-program-source"}\n')
    source["agent_artifact"]["path"] = str(candidate)
    source["agent_artifact"]["sha256"] = digest(candidate)
    for item in source["evidence"]:
        target = evidence_dir / f"{item['kind']}.json"
        original = Path(item["path"])
        shutil.copy2(original, target)
        if item["kind"] == "execution_trace" and trace_value is not None:
            trace = json.loads(target.read_text())
            trace["candidate_sha256"] = trace_value
            target.write_text(json.dumps(trace, sort_keys=True) + "\n")
        item["path"] = str(target)
        item["sha256"] = digest(target)
    certificate = case / "certificate.json"
    certificate.write_text(json.dumps(source, sort_keys=True) + "\n")
    return certificate


def run_wrapper(certificate: Path) -> dict:
    completed = subprocess.run([sys.executable, str(WRAPPER), str(certificate)], capture_output=True, text=True, check=True)
    return json.loads(completed.stdout)


def test_matching_candidate_binding_accepts_and_preserves_validator_verdict(tmp_path: Path) -> None:
    certificate = make_case(tmp_path)
    candidate_hash = json.loads(certificate.read_text())["agent_artifact"]["sha256"]
    certificate_data = json.loads(certificate.read_text())
    trace_path = Path(next(item["path"] for item in certificate_data["evidence"] if item["kind"] == "execution_trace"))
    trace = json.loads(trace_path.read_text())
    trace["candidate_sha256"] = candidate_hash
    trace_path.write_text(json.dumps(trace, sort_keys=True) + "\n")
    for item in certificate_data["evidence"]:
        if item["kind"] == "execution_trace":
            item["sha256"] = digest(trace_path)
    certificate.write_text(json.dumps(certificate_data, sort_keys=True) + "\n")
    result = run_wrapper(certificate)
    assert result["status"] == "ACCEPT"
    assert result["raw_verdict"]["parsed"]["decision"] == "ACCEPT"
    assert result["candidate_artifact_sha256"] == candidate_hash


@pytest.mark.parametrize("mutation,expected", [("mismatch", "semantic-candidate-execution-mismatch"), ("duplicate", "duplicate-or-malformed-evidence"), ("malformed", "duplicate-or-malformed-evidence"), ("nul-path", "malformed-evidence-path"), ("tamper", "evidence-hash"), ("candidate", "candidate-pointer-hash")])
def test_binding_boundary_rejects_tampering_and_duplicates(tmp_path: Path, mutation: str, expected: str) -> None:
    certificate = make_case(tmp_path)
    certificate_data = json.loads(certificate.read_text())
    if mutation == "mismatch":
        trace_item = next(item for item in certificate_data["evidence"] if item["kind"] == "execution_trace")
        trace = json.loads(Path(trace_item["path"]).read_text())
        trace["candidate_sha256"] = "0" * 64
        Path(trace_item["path"]).write_text(json.dumps(trace, sort_keys=True) + "\n")
        trace_item["sha256"] = digest(Path(trace_item["path"]))
    elif mutation == "duplicate":
        certificate_data["evidence"].append(dict(certificate_data["evidence"][0]))
    elif mutation == "malformed":
        certificate_data["evidence"][0] = {"kind": "agent_artifact"}
    elif mutation == "nul-path":
        certificate_data["evidence"][0]["path"] = "bad\x00path"
    elif mutation == "candidate":
        certificate_data["agent_artifact"]["sha256"] = "0" * 64
    else:
        certificate_data["evidence"][0]["sha256"] = "0" * 64
    certificate.write_text(json.dumps(certificate_data, sort_keys=True) + "\n")
    result = run_wrapper(certificate)
    assert result["status"] == "REJECT"
    assert result["reason"] == expected or result["reason"].startswith(expected + ":")
    assert "raw_verdict" in result


def test_absent_binding_is_inconclusive_after_outer_integrity(tmp_path: Path) -> None:
    result = run_wrapper(make_case(tmp_path))
    assert result["status"] == "INCONCLUSIVE"
    assert result["reason"] == "trace-has-no-candidate-hash"


@pytest.mark.parametrize("trace_value", [[], None])
def test_non_object_trace_is_rejected(tmp_path: Path, trace_value: object) -> None:
    certificate = make_case(tmp_path)
    certificate_data = json.loads(certificate.read_text())
    trace_item = next(item for item in certificate_data["evidence"] if item["kind"] == "execution_trace")
    trace_path = Path(trace_item["path"])
    trace_path.write_text(json.dumps(trace_value) + "\n")
    trace_item["sha256"] = digest(trace_path)
    certificate.write_text(json.dumps(certificate_data, sort_keys=True) + "\n")
    result = run_wrapper(certificate)
    assert result["status"] == "REJECT"
    assert result["reason"] == "malformed-trace-object"
