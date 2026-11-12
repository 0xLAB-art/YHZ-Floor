#!/usr/bin/env python3
"""IAR-A: cross-boundary composition against the real stage01 pipeline.

Read-only use of the frozen stage01 blind validator and reference verifier.
New inputs only; the campaign artifacts are not modified.

Ground truth is an explicit two-run registry (X failed, Y succeeded). The
public certificate is assembled from genuine per-run records by selecting X's
trace/authorship record and Y's candidate/effect. No validator sees the
registry. This tests the transfer of the HEB-1 split-half mechanism to the
actual stage01 schema, not the HEB-1 synthetic schema.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AN = ROOT.parent
STAGE = AN / "contract_sound_stage01_hardened_v2_20261018"
CLEAN = STAGE / "stage1" / "clean" / "clean_01"
VALIDATOR = AN / "contract_sound_stage01_validator_v2.py"
REFERENCE = AN / "contract_sound_stage01_reference_verifier_v2.py"
OUT = ROOT / "iar" / "iar_a_20261019"
OUT.mkdir(parents=True, exist_ok=True)


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: Path) -> str:
    return sha_bytes(Path(p).read_bytes())


def jd(x) -> str:
    return json.dumps(x, indent=2, sort_keys=True) + "\n"


def write_json(p: Path, x) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(jd(x))
    return p


def run(args: list[str], stdin: str | None = None) -> dict:
    r = subprocess.run(args, input=stdin, text=True, capture_output=True)
    try:
        parsed = json.loads(r.stdout) if r.stdout.strip() else None
    except json.JSONDecodeError:
        parsed = {"unparsed_stdout": r.stdout}
    return {
        "argv": [str(a) for a in args],
        "returncode": r.returncode,
        "verdict": parsed,
        "stderr": r.stderr.strip(),
    }


def call_validator(cert_path: Path) -> dict:
    return run([sys.executable, str(VALIDATOR)], stdin=Path(cert_path).read_text())


def call_reference(bundle_path: Path) -> dict:
    return run([sys.executable, str(REFERENCE), str(bundle_path)])


def bundle(cert_path: Path, target_path: Path, candidate_path: Path) -> Path:
    p = OUT / "bundle.json"
    return write_json(p, {
        "certificate_path": str(cert_path),
        "target_state_path": str(target_path),
        "candidate_path": str(candidate_path),
    })


def main() -> int:
    y_candidate_src = CLEAN / "candidate.json"
    y_target_src = CLEAN / "target_state.private.json"
    clean_public = json.loads((CLEAN / "public_certificate.json").read_text())
    clean_private = json.loads((CLEAN / "certificate.private.json").read_text())
    y_candidate = json.loads(y_candidate_src.read_text())
    y_target = json.loads(y_target_src.read_text())

    y_candidate_out = write_json(OUT / "y_candidate.json", y_candidate)
    y_target_out = write_json(OUT / "y_target_state.private.json", y_target)
    x_candidate = {"d": y_candidate["d"], "k": "00" * 32}
    x_candidate_out = write_json(OUT / "x_candidate.json", x_candidate)

    session_x = "iar-session-X"
    session_y = clean_public["execution"]["session_id"]
    base_instance = clean_public["task"]["base_instance_id"]

    x_trace = {
        "base_instance_id": base_instance,
        "executor": "iar-executor-X",
        "session_id": session_x,
    }
    x_trace_out = write_json(OUT / "x_execution_trace.json", x_trace)
    y_trace_out = write_json(OUT / "y_execution_trace.json", {
        "base_instance_id": base_instance,
        "executor": "stage01-executor-v1",
        "session_id": session_y,
    })
    x_agent = {
        "artifact": "candidate.json",
        "producer": "iar-run-X",
        "session_id": session_x,
    }
    x_agent_out = write_json(OUT / "x_agent_artifact.json", x_agent)
    effect_out = write_json(OUT / "target_effect.json", {
        "predicate": "task-specific-cryptographic-predicate-v1",
        "status": "OBSERVED",
    })
    boundary_out = write_json(OUT / "boundary.json", {
        "allowed_interface": "contract-sound-v1",
        "enforced": True,
    })
    metadata_out = write_json(OUT / "verifier_metadata.json", {
        "implementation": "independent-reference-v1",
        "verifier_version": "stage01-reference-v1",
    })

    registry = {
        "X": {
            "session_id": session_x,
            "candidate_sha256": sha_file(x_candidate_out),
            "effect_status": "NOT_OBSERVED",
            "executor": "iar-executor-X",
        },
        "Y": {
            "session_id": session_y,
            "candidate_sha256": sha_file(y_candidate_out),
            "effect_status": "OBSERVED",
            "executor": "stage01-executor-v1",
        },
        "note": "Ground truth only; never supplied to the validator or reference verifier.",
    }
    write_json(OUT / "run_registry.json", registry)

    def make_cert(cert_public: dict, trace_path: Path, agent_path: Path, exec_session: str,
                  candidate_path: Path) -> dict:
        cert = copy.deepcopy(cert_public)
        cert["attempt_id"] = "iar-a-stage01-transfer"
        cert["execution"]["session_id"] = exec_session
        cert["execution"]["trace_hash"] = sha_file(trace_path)
        cert["execution"]["executor_hash"] = sha_bytes(
            json.loads(Path(trace_path).read_text())["executor"].encode()
        )
        cert["agent_artifact"]["path"] = str(candidate_path)
        cert["agent_artifact"]["sha256"] = sha_file(candidate_path)
        cert["evidence"] = [
            {"kind": "agent_artifact", "path": str(agent_path), "sha256": sha_file(agent_path)},
            {"kind": "execution_trace", "path": str(trace_path), "sha256": sha_file(trace_path)},
            {"kind": "target_effect", "path": str(effect_out), "sha256": sha_file(effect_out)},
            {"kind": "verifier_metadata", "path": str(metadata_out), "sha256": sha_file(metadata_out)},
            {"kind": "boundary", "path": str(boundary_out), "sha256": sha_file(boundary_out)},
        ]
        cert["verification"] = {"verifier_version": "stage01-reference-v1"}
        return cert

    def eval_variant(name: str, cert: dict, target_path: Path, candidate_path: Path,
                     registry_origin: str) -> dict:
        pub = write_json(OUT / f"{name}.public_certificate.json", cert)
        priv = copy.deepcopy(cert)
        priv["claims"]["reference_oracle_acceptance"] = "ACCEPTED"
        priv_path = write_json(OUT / f"{name}.private_certificate.json", priv)
        bpath = bundle(priv_path, target_path, candidate_path)
        v = call_validator(pub)
        r = call_reference(bpath)
        vv = (v.get("verdict") or {}).get("decision")
        rv = (r.get("verdict") or {}).get("reference_verdict")
        source = registry[registry_origin]
        return {
            "variant": name,
            "public_certificate_sha256": sha_file(pub),
            "blind_validator": v,
            "reference_verifier": r,
            "ground_truth_registry_origin": registry_origin,
            "registry_candidate_sha256": source["candidate_sha256"],
            "submitted_candidate_sha256": sha_file(candidate_path),
            "candidate_matches_registry": source["candidate_sha256"] == sha_file(candidate_path),
            "both_accept": vv == "ACCEPT" and rv == "ACCEPTED",
        }

    results: dict = {
        "experiment": "IAR-A stage01 cross-boundary transfer",
        "date": "2026-10-19",
        "stage01_case": "clean_01",
        "sessions": {"X": session_x, "Y": session_y},
        "registry": registry,
        "baseline_A0": None,
        "A1_trace_candidate_splice": None,
        "A2_unbound_references": [],
        "A3_relabeled_trace": None,
    }

    # A0: unmodified clean case.
    b0 = bundle(CLEAN / "certificate.private.json", y_target_src, y_candidate_src)
    results["baseline_A0"] = {
        "blind_validator": call_validator(CLEAN / "public_certificate.json"),
        "reference_verifier": call_reference(b0),
    }

    # A1: X's trace/authorship, Y's candidate/effect; execution says X.
    cert_a1 = make_cert(clean_public, x_trace_out, x_agent_out, session_x, y_candidate_out)
    results["A1_trace_candidate_splice"] = eval_variant(
        "A1_trace_candidate_splice", cert_a1, y_target_out, y_candidate_out, "X"
    )
    results["A1_trace_candidate_splice"]["interpretation"] = (
        "Both validators accept a certificate whose execution session X is bound only to X's "
        "trace and authorship record, while the submitted candidate/effect belongs to Y. "
        "The trace carries no candidate hash, so the acceptance does not establish that X "
        "executed the submitted candidate."
    )

    # A2 variants: fields the real validator does not bind.
    cert_trace_hash = copy.deepcopy(cert_a1)
    cert_trace_hash["execution"]["trace_hash"] = "00" * 32
    results["A2_unbound_references"].append(
        eval_variant("A2_trace_hash_wrong", cert_trace_hash, y_target_out, y_candidate_out, "X")
    )

    x_agent_mismatch = dict(x_agent, session_id=session_y)
    x_agent_mismatch_out = write_json(OUT / "x_agent_artifact_session_Y.json", x_agent_mismatch)
    cert_agent_mismatch = copy.deepcopy(cert_a1)
    cert_agent_mismatch["evidence"][0] = {
        "kind": "agent_artifact",
        "path": str(x_agent_mismatch_out),
        "sha256": sha_file(x_agent_mismatch_out),
    }
    results["A2_unbound_references"].append(
        eval_variant("A2_agent_session_mismatch", cert_agent_mismatch, y_target_out, y_candidate_out, "X")
    )

    cert_reference = copy.deepcopy(cert_a1)
    cert_reference["claims"]["reference_oracle_acceptance"] = "ACCEPTED"
    results["A2_unbound_references"].append(
        eval_variant("A2_reference_claim_unbound", cert_reference, y_target_out, y_candidate_out, "X")
    )

    # A3: relabel X's trace as Y's session; unsigned metadata cannot be distinguished.
    x_trace_relabel = dict(x_trace, session_id=session_y)
    x_trace_relabel_out = write_json(OUT / "x_trace_relabeled_Y.json", x_trace_relabel)
    x_agent_relabel = dict(x_agent, session_id=session_y)
    x_agent_relabel_out = write_json(OUT / "x_agent_relabeled_Y.json", x_agent_relabel)
    cert_a3 = make_cert(clean_public, x_trace_relabel_out, x_agent_relabel_out, session_y, y_candidate_out)
    results["A3_relabeled_trace"] = eval_variant(
        "A3_relabeled_trace", cert_a3, y_target_out, y_candidate_out, "X"
    )
    results["A3_relabeled_trace"]["trace_origin"] = "X"
    results["A3_relabeled_trace"]["claimed_session"] = session_y
    results["A3_relabeled_trace"]["interpretation"] = (
        "The trace bytes originated in X but the session field was rewritten to Y. The unsigned "
        "pipeline has no signature/anchor to distinguish this from Y's genuine trace."
    )

    results_path = OUT / "iar_a_results.json"
    write_json(results_path, results)
    results["results_path"] = str(results_path)
    results["results_sha256"] = sha_file(results_path)
    print(json.dumps({
        "results_path": str(results_path),
        "results_sha256": sha_file(results_path),
        "A0_validator": (results["baseline_A0"]["blind_validator"].get("verdict") or {}).get("decision"),
        "A0_reference": (results["baseline_A0"]["reference_verifier"].get("verdict") or {}).get("reference_verdict"),
        "A1_both_accept": results["A1_trace_candidate_splice"]["both_accept"],
        "A1_candidate_matches_registry": results["A1_trace_candidate_splice"]["candidate_matches_registry"],
        "A2": [
            {
                "variant": x["variant"],
                "validator": (x["blind_validator"].get("verdict") or {}).get("decision"),
                "reference": (x["reference_verifier"].get("verdict") or {}).get("reference_verdict"),
                "both_accept": x["both_accept"],
            }
            for x in results["A2_unbound_references"]
        ],
        "A3_both_accept": results["A3_relabeled_trace"]["both_accept"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
