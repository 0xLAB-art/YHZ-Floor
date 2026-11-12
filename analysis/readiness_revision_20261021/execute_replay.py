#!/usr/bin/env python3
import argparse
import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def sandbox_command(program, observations):
    command = ["prlimit", "--cpu=10", "--as=536870912", "--fsize=1048576", "--nofile=32",
               "bwrap", "--unshare-all", "--die-with-parent", "--new-session"]
    for directory in ("/usr", "/lib", "/lib64"):
        if Path(directory).exists():
            command += ["--ro-bind", directory, directory]
    return command + ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--dir", "/case",
                      "--ro-bind", str(program), "/case/candidate.py",
                      "--ro-bind", str(observations), "/case/public_instance.json",
                      "--chdir", "/case", "--clearenv", "--setenv", "PATH", "/usr/bin",
                      "--setenv", "PYTHONHASHSEED", "0", "/usr/bin/python3", "-I",
                      "/case/candidate.py", "/case/public_instance.json"]


def execute_one(root, output, row, contract, helper):
    sid = row["session_id"]
    case = root / "runs/confirmatory/sessions" / sid
    dest = output / "sessions" / sid
    dest.mkdir(parents=True)
    program, observations = case / "candidate.py", case / "public_instance.json"
    qualification = contract.qualify_source(program.read_text(), "v3")
    record = {"session_id": sid, "qualification": qualification,
              "source_sha256": helper.sha(program), "observations_sha256": helper.sha(observations),
              "candidate_output_path": str(dest / "candidate_output.json")}
    if not qualification["qualified"]:
        record["status"] = "SOURCE_PARSE_REJECTED" if qualification["status"] == "SOURCE_PARSE_REJECTED" else "SOURCE_REJECTED"
    else:
        try:
            process = subprocess.run(sandbox_command(program, observations), capture_output=True,
                                     timeout=20, env={"PATH": "/usr/bin:/bin"}, check=False)
            (dest / "stdout.txt").write_bytes(process.stdout)
            (dest / "stderr.txt").write_bytes(process.stderr)
            record["returncode"] = process.returncode
            if b"bwrap:" in process.stderr or b"prlimit:" in process.stderr:
                record["status"] = "SANDBOX_ERROR"
            elif process.returncode != 0:
                record["status"] = "EXECUTION_FAILED"
            else:
                lines = [line.strip() for line in process.stdout.decode().splitlines() if line.strip()]
                try:
                    candidate = json.loads(lines[-1])
                    if not isinstance(candidate, dict):
                        raise ValueError("candidate is not an object")
                    (dest / "candidate_output.json").write_text(json.dumps(candidate, sort_keys=True) + "\n")
                    record["status"] = "EXECUTED"
                except (IndexError, ValueError):
                    record["status"] = "OUTPUT_SCHEMA_INVALID"
        except subprocess.TimeoutExpired:
            record["status"] = "EXECUTION_TIMEOUT"
    (dest / "execution.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def adjudicate_fresh(root, row, execution, reference, helper, output):
    case = root / "runs/confirmatory/sessions" / row["session_id"]
    dest = output / "sessions" / row["session_id"]
    bundle = json.loads((case / "reference_bundle.json").read_text())
    cert = json.loads((case / "certificate.private.json").read_text())
    for item in cert["evidence"]:
        item["path"] = str(helper.relocate(item["path"], root))
    cert["agent_artifact"]["path"] = str(helper.relocate(cert["agent_artifact"]["path"], root))
    cert_path = dest / "relocated_historical_certificate.json"
    cert_path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    for key in ("artifact_path", "private_state_path", "public_instance_path"):
        bundle[key] = str(helper.relocate(bundle[key], root))
    bundle["candidate_output_path"] = execution["candidate_output_path"]
    bundle["certificate_path"] = str(cert_path)
    bundle_path = dest / "fresh_reference_bundle.json"
    bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n")
    captured, previous = io.StringIO(), sys.argv
    try:
        sys.argv = ["h1r3_reference.py", str(bundle_path)]
        with contextlib.redirect_stdout(captured):
            status = reference.main()
    finally:
        sys.argv = previous
    if status != 0:
        raise RuntimeError("reference failed")
    verdict = json.loads(captured.getvalue())
    (dest / "fresh_reference.json").write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n")
    return verdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4, choices=range(1, 9))
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.is_relative_to(root):
        raise ValueError("fresh execution must be outside retained package")
    for binary in ("bwrap", "prlimit"):
        if shutil.which(binary) is None:
            raise RuntimeError(f"missing dependency: {binary}")
    helper_spec = importlib.util.spec_from_file_location("retained_helper", root / "replay.py")
    helper = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper)
    runner_sha256 = helper.sha(Path(__file__).resolve())
    manifest = json.loads((root / "MANIFEST.json").read_text())
    for rel, digest in manifest["files"].items():
        path = (root / rel).resolve()
        if not path.is_relative_to(root) or not path.is_file() or helper.sha(path) != digest:
            raise ValueError(f"manifest mismatch: {rel}")
    rows = [json.loads(line) for line in (root / "runs/confirmatory/results.jsonl").read_text().splitlines()]
    if len(rows) != 852 or len({row["session_id"] for row in rows}) != 852:
        raise ValueError("expected complete census")
    for row in rows:
        if Path(row["session_id"]).name != row["session_id"] or row["session_id"] in {".", ".."}:
            raise ValueError("invalid session ID")
    contract = helper.load_module(root / "code/h1r3_contract.py", "fresh_contract")
    reference = helper.load_module(root / "code/h1r3_reference.py", "fresh_reference")
    output.mkdir(parents=True, exist_ok=False)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        executions = list(pool.map(lambda row: execute_one(root, output, row, contract, helper), rows))
    details = []
    for row, execution in zip(rows, executions):
        fresh = adjudicate_fresh(root, row, execution, reference, helper, output)
        candidate_path = Path(execution["candidate_output_path"])
        retained = root / "runs/confirmatory/sessions" / row["session_id"] / "candidate_output.json"
        same_output = (json.loads(candidate_path.read_text()) == json.loads(retained.read_text())
                       if candidate_path.exists() and retained.exists() else not candidate_path.exists() and not retained.exists())
        details.append({"session_id": row["session_id"], "kind": row["kind"], "status": execution["status"],
                        "fresh_predicate": fresh["cryptographic_predicate"], "fresh_verdict": fresh["verdict"],
                        "retained_verdict": row["reference"]["verdict"], "same_output": same_output,
                        "verdict_agreement": fresh["verdict"] == row["reference"]["verdict"]})
    census = Counter(item["status"] for item in details)
    mismatches = sum(not item["verdict_agreement"] for item in details)
    infrastructure_errors = sum(item["status"] in {"SANDBOX_ERROR", "EXECUTION_TIMEOUT"} for item in details)
    summary = {"status": "PASS" if not mismatches and not infrastructure_errors else "FAIL",
               "sessions": len(rows), "execution_statuses": dict(census), "verdict_disagreements": mismatches,
               "infrastructure_errors": infrastructure_errors,
               "fresh_exploit_acceptances": sum(item["fresh_verdict"] == "ACCEPTED" and item["kind"] != "c0" for item in details),
               "fresh_correct_abstentions": sum(item["fresh_verdict"] == "ACCEPTED" and item["kind"] == "c0" for item in details),
               "identical_parsed_outputs_or_same_absence": sum(item["same_output"] for item in details),
               "retained_manifest_sha256": helper.sha(root / "MANIFEST.json"),
               "runner_sha256": runner_sha256,
               "scope": "fresh deterministic program execution on retained public inputs, with independent cryptographic checks; no model generations",
               "sandbox": "only Python runtime, program and public observations mounted; network/PID/IPC/user namespaces isolated",
               "python": sys.version, "details": details}
    (output / "report.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    hashes = {str(path.relative_to(output)): helper.sha(path) for path in sorted(output.rglob("*")) if path.is_file()}
    (output / "MANIFEST.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "details"}, indent=2))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
