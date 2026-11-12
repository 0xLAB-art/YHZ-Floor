#!/usr/bin/env python3
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relocate(value, root):
    marker = "runs/confirmatory/sessions/"
    if not isinstance(value, str) or marker not in value:
        raise ValueError("unrecognized retained evidence path")
    suffix = value[value.index(marker):]
    path = (root / suffix).resolve()
    if not path.is_relative_to(root / "runs/confirmatory/sessions"):
        raise ValueError("evidence path escapes package")
    return path


def adjudicate(root, row, reference, work):
    case = root / "runs/confirmatory/sessions" / row["session_id"]
    bundle = json.loads((case / "reference_bundle.json").read_text())
    cert = json.loads((case / "certificate.private.json").read_text())
    for item in cert["evidence"]:
        item["path"] = str(relocate(item["path"], root))
    cert["agent_artifact"]["path"] = str(relocate(cert["agent_artifact"]["path"], root))
    cert_path = work / "certificate.json"
    cert_path.write_text(json.dumps(cert))
    for key in ("artifact_path", "candidate_output_path", "private_state_path", "public_instance_path"):
        bundle[key] = str(relocate(bundle[key], root))
    bundle["certificate_path"] = str(cert_path)
    bundle_path = work / "bundle.json"
    bundle_path.write_text(json.dumps(bundle))
    saved = sys.argv
    captured = io.StringIO()
    try:
        sys.argv = ["h1r3_reference.py", str(bundle_path)]
        with contextlib.redirect_stdout(captured):
            status = reference.main()
    finally:
        sys.argv = saved
    if status != 0:
        raise ValueError("reference did not complete")
    return json.loads(captured.getvalue())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / "MANIFEST.json").read_text())
    bad = []
    for rel, expected in manifest["files"].items():
        path = (root / rel).resolve()
        if not path.is_relative_to(root) or not path.is_file() or sha(path) != expected:
            bad.append(rel)
    if bad:
        print(json.dumps({"status": "FAIL", "manifest_mismatches": bad}))
        return 1
    rows = [json.loads(line) for line in (root / "runs/confirmatory/results.jsonl").read_text().splitlines()]
    if len(rows) != 852 or len({row["session_id"] for row in rows}) != 852:
        raise ValueError("incomplete or duplicated census")
    for row in rows:
        sid = row["session_id"]
        if not isinstance(sid, str) or Path(sid).name != sid or sid in {".", ".."}:
            raise ValueError("invalid session ID")
    reference = load_module(root / "code/h1r3_reference.py", "retained_reference")
    contract = load_module(root / "code/h1r3_contract.py", "retained_contract")
    differences, verdicts, kinds, terminals = [], Counter(), Counter(), Counter()
    details = []
    with tempfile.TemporaryDirectory(prefix="acts-oracle-replay-") as temporary:
        work = Path(temporary)
        for row in rows:
            sid = row["session_id"]
            case = root / "runs/confirmatory/sessions" / sid
            result = adjudicate(root, row, reference, work)
            source = (case / "candidate.py").read_text()
            current = contract.qualify_source(source, "v3")
            legacy = contract.qualify_source(source, "legacy")
            issues = []
            if result["verdict"] != row["reference"]["verdict"]:
                issues.append("reference-verdict")
            if result["cryptographic_predicate"] != row["reference"]["cryptographic_predicate"]:
                issues.append("cryptographic-predicate")
            if not result["certificate_integrity"]:
                issues.append("certificate-integrity")
            if current["qualified"] != row["qualification"]["qualified"]:
                issues.append("current-source-policy")
            if legacy["qualified"] != row["qualification_legacy"]["qualified"]:
                issues.append("legacy-source-policy")
            if sha(case / "prompt.txt") != row["prompt_sha256"]:
                issues.append("prompt-binding")
            raw = json.loads((case / "provider_raw.json").read_text())
            text = "\n".join(item.get("text", "") for item in raw["content"] if item.get("type") == "text")
            if source.strip() not in text:
                issues.append("program-response-binding")
            verdicts[result["verdict"]] += 1
            kinds[row["kind"]] += 1
            terminals[row["terminal"]] += 1
            detail = {"session_id": sid, "kind": row["kind"], "verdict": result["verdict"],
                      "cryptographic_predicate": result["cryptographic_predicate"],
                      "certificate_integrity": result["certificate_integrity"], "issues": issues}
            details.append(detail)
            if issues:
                differences.append(detail)
    report = {"status": "PASS" if not differences else "FAIL", "sessions": len(rows),
              "reference_verdicts": dict(verdicts), "kinds": dict(kinds),
              "recorded_terminal_counts": dict(terminals), "disagreements": len(differences),
              "scope": "re-adjudication of retained outputs and integrity bindings; not fresh program execution or hosted-model regeneration",
              "manifest_sha256": sha(root / "MANIFEST.json"), "details": details}
    if args.report:
        if args.report.resolve().is_relative_to(root):
            raise ValueError("report must be outside immutable package")
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "details"}, indent=2))
    return 0 if not differences else 1


if __name__ == "__main__":
    raise SystemExit(main())
