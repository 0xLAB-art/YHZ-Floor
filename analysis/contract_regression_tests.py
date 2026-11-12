import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / "ACTS-ATTACK" / "harness" / "v3"
CONDITIONS = ["RC4_Keystream", "ChaCha20_Nonce_Repeat", "ECDSA_Nonce_Reuse", "CBC_Padding_Oracle"]


def wait_port(port):
    for _ in range(100):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("oracle did not become ready")


def run_agent(condition, port, model, stub, out, rep):
    env = os.environ.copy()
    env["ACTS_V3_SCRIPTED_CODE"] = str(stub)
    env["OPENROUTER_RUN_TIMEOUT"] = "240"
    result = subprocess.run(
        [sys.executable, str(V3 / "agent_loop.py"), "--model", model,
         "--condition", condition, "--rep", str(rep), "--port", str(port),
         "--out", str(out), "--max-attempts", "1"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    return json.loads(result.stdout)


def main():
    out = ROOT / "sp2027" / "agent-eval" / "contract_regression_v3_20261014_01"
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(V3))
    from prompts import build_task_message
    from classify import classify, is_graded
    from qualification import (IntegrityError, assert_schedule_equivalent,
                               derive_run_ids, resolve_schedule)
    sentinel_text = build_task_message(
        "RC4_Keystream", {"c1_hex": "ARGV_INSTANCE_SENTINEL", "c2_hex": "STDIN_SENTINEL"}, 1, 1)
    prompt_checks = {
        "argv_declared": "argv[1]" in sentinel_text,
        "runtime_sentinels_absent": "ARGV_INSTANCE_SENTINEL" not in sentinel_text and "STDIN_SENTINEL" not in sentinel_text,
    }
    malformed = out / "malformed.json"
    malformed.write_text("{")
    missing_argv = subprocess.run([sys.executable, str(V3 / "contract_stub.py")],
                                  cwd=ROOT, capture_output=True, text=True)
    malformed_json = subprocess.run([sys.executable, str(V3 / "contract_stub.py"), str(malformed)],
                                    cwd=ROOT, capture_output=True, text=True)
    stale = out / "stale.py"
    stale.write_text("print('CLAIM:{\"plaintext_hex\":\"5e82cec5411db8557fc6a368d70013db77b277973d3d43fca333cf3138a0b1bb13454bfc3cb93dbc20812ca873a637b048db95b3436ec8d013031c6596987602\"}')\n")
    port = 15879
    oracle = subprocess.Popen([sys.executable, str(V3 / "oracle.py"), str(port)],
                              cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
    try:
        wait_port(port)
        stub = V3 / "contract_stub.py"
        freshness = {}
        for condition in CONDITIONS:
            values = []
            for rep in (1, 2):
                model = f"deterministic-fresh-{os.getpid()}-{condition}-{rep}"
                summary = run_agent(condition, port, model, stub, out / condition, rep)
                values.append({"status": summary["verdict"], "instance_sha256": summary["instance_sha256"], "queries": summary["queries"]})
            freshness[condition] = values
        stale_summary = run_agent("RC4_Keystream", port,
                                  f"deterministic-stale-{os.getpid()}", stale,
                                  out / "stale", 99)
    finally:
        oracle.terminate()
        oracle.wait(timeout=10)
    terminal_cases = {
        "SUCCESS": classify("success", False, 1, None),
        "ORACLE_FAIL": classify("failure", False, 1, None),
        "TOOL_FAILURE": classify("no_claim", False, 1, "run 1: no CLAIM line"),
        "TOOL_TIMEOUT": classify("timeout", False, 1, "timeout: generated process"),
        "AGENT_GIVEUP": classify("no_claim", True, 0, None),
        "MODEL_REFUSAL": classify("no_claim", False, 0, None),
        "PROVIDER_UNAVAILABLE": classify("no_claim", False, 0, "gateway_transient: http 503"),
        "HARNESS_ERROR": classify(None, False, 0, "oracle unreachable"),
    }
    expected_terminal_cases = {
        "SUCCESS": "SUCCESS", "ORACLE_FAIL": "ORACLE_FAIL",
        "TOOL_FAILURE": "TOOL_FAILURE", "TOOL_TIMEOUT": "TIMEOUT",
        "AGENT_GIVEUP": "AGENT_GIVEUP", "MODEL_REFUSAL": "MODEL_REFUSAL",
        "PROVIDER_UNAVAILABLE": "PROVIDER_UNAVAILABLE",
        "HARNESS_ERROR": "HARNESS_ERROR",
    }
    identity_manifest = json.loads((ROOT / "ACTS-ATTACK" / "harness" / "v3" / "tests" / "fixtures" / "e2_clean_requal_schedule_golden.json").read_text())
    identity_digest = __import__("hashlib").sha256(json.dumps(identity_manifest, separators=(",", ":")).encode()).hexdigest()
    resolved = resolve_schedule(identity_manifest)
    identity_checks = {"unique_run_ids": len(set(derive_run_ids(identity_manifest, resolved, identity_digest))) == 12}
    try:
        derive_run_ids(identity_manifest, [resolved[0], resolved[0]], identity_digest)
    except IntegrityError:
        identity_checks["duplicate_run_id_rejected"] = True
    else:
        identity_checks["duplicate_run_id_rejected"] = False
    cross_session = json.loads(json.dumps(resolved))
    cross_session[0]["task_id"] = cross_session[3]["task_id"]
    try:
        assert_schedule_equivalent(cross_session, resolved)
    except IntegrityError:
        identity_checks["cross_session_identity_rejected"] = True
    else:
        identity_checks["cross_session_identity_rejected"] = False
    identity_checks["stale_artifact_rejected"] = stale_summary["verdict"] == "failure"
    result = {
        "schema": "contract-regression-results/1",
        "prompt_checks": prompt_checks,
        "missing_argv_rejected": missing_argv.returncode != 0,
        "malformed_json_rejected": malformed_json.returncode != 0,
        "freshness": freshness,
        "freshness_all_success": all(x["status"] == "success" and len(x["instance_sha256"]) == 64 and x["instance_sha256"] != y["instance_sha256"] for x, y in ((values[0], values[1]) for values in freshness.values())),
        "stale_hardcode_status": stale_summary["verdict"],
        "stale_hardcode_rejected": stale_summary["verdict"] == "failure",
        "terminal_status_cases": terminal_cases,
        "terminal_status_cases_match": terminal_cases == expected_terminal_cases,
        "graded_status_cases": {status: is_graded(status) for status in set(terminal_cases.values())},
        "identity_checks": identity_checks,
    }
    (out / "RESULTS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if (result["freshness_all_success"] and result["stale_hardcode_rejected"]
                 and all(prompt_checks.values()) and result["terminal_status_cases_match"]
                 and all(identity_checks.values())) else 1


if __name__ == "__main__":
    raise SystemExit(main())
