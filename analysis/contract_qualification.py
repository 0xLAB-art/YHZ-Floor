import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / "ACTS-ATTACK" / "harness" / "v3"
CARDS = ROOT / "sp2027" / "pre-registration" / "cards_v3"
CONDITIONS = ["RC4_Keystream", "ChaCha20_Nonce_Repeat", "ECDSA_Nonce_Reuse", "CBC_Padding_Oracle"]
CARD_NAMES = {
    "RC4_Keystream": "rc4_keystream_reuse.json",
    "ChaCha20_Nonce_Repeat": "chacha20_nonce_reuse.json",
    "ECDSA_Nonce_Reuse": "ecdsa_nonce_reuse.json",
    "CBC_Padding_Oracle": "cbc_padding_oracle.json",
}
TASK_IDS = {
    "RC4_Keystream": "rc4_keystream_reuse",
    "ChaCha20_Nonce_Repeat": "chacha20_nonce_reuse",
    "ECDSA_Nonce_Reuse": "ecdsa_nonce_reuse",
    "CBC_Padding_Oracle": "cbc_padding_oracle",
}


def wait_port(port):
    for _ in range(100):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("oracle did not become ready")


def run_condition(condition, port, out, model, stub):
    loop_out = out / "loop"
    loop_out.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["ACTS_V3_SCRIPTED_CODE"] = str(stub)
    env["OPENROUTER_RUN_TIMEOUT"] = "240"
    command = [sys.executable, str(V3 / "agent_loop.py"), "--model", model,
               "--condition", condition, "--rep", "1", "--port", str(port),
               "--out", str(loop_out), "--max-attempts", "1"]
    proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                          text=True, check=False)
    summary = json.loads(proc.stdout)
    log_path = loop_out / f"agent_session_{model}_{condition}_rep1.jsonl"
    session_log = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]
    return summary, session_log, proc.stderr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--port", type=int, default=15875)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    model = f"deterministic-contract-qual-{os.getpid()}"
    stub = V3 / "contract_stub.py"
    oracle = subprocess.Popen([sys.executable, str(V3 / "oracle.py"), str(args.port)],
                              cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
    try:
        wait_port(args.port)
        sys.path.insert(0, str(V3))
        from record_builder import build_run_record, build_task_card, write_session
        results = []
        for condition in CONDITIONS:
            condition_dir = args.output / condition
            condition_dir.mkdir(parents=True, exist_ok=True)
            summary, session_log, stderr = run_condition(condition, args.port,
                                                         condition_dir, model, stub)
            task_id = TASK_IDS[condition]
            run_id = f"contract_qual_v3__{task_id}__T1_known__rep1"
            summary.update({"run_id": run_id, "track": "T1_known",
                            "verdict_obj": summary.get("verdict_obj") or {}})
            card = build_task_card(CARDS / CARD_NAMES[condition])
            model_config = {
                "provider": "local_deterministic_stub",
                "access_path": "other",
                "model_id": model,
                "model_snapshot": "deterministic-contract-stub-v3",
                "temperature": 0.0,
                "top_p": 1.0,
                "token_budget": 0,
                "system_prompt_sha256": hashlib.sha256((V3 / "prompts.py").read_bytes()).hexdigest(),
                "tool_schemas_sha256": None,
            }
            artifact_paths = [summary["instance_path"]]
            for index in range(1, int(summary.get("attempts") or 0) + 1):
                path = Path("/tmp") / f"acts_agent_{model}_{condition}_1_{index}.py"
                if path.exists():
                    artifact_paths.append(str(path))
            environment = {
                "qualification": {
                    "namespace": "CONTRACT-QUALIFICATION-V3-20261014-01",
                    "contract": "agent-contract-v3",
                },
                "python": sys.version.split()[0],
            }
            run = build_run_record(summary, session_log, card, model_config,
                                   environment, artifact_paths)
            write_session(run, session_log, condition_dir)
            results.append({"condition": condition, "status": run["session"]["status"],
                            "queries": run["session"]["queries"],
                            "instance_sha256": summary["instance_sha256"],
                            "stderr": stderr[-500:]})
        (args.output / "RESULTS.json").write_text(json.dumps({
            "schema": "contract-qualification-results/1",
            "contract": "agent-contract-v3",
            "results": results,
            "all_success": all(x["status"] == "SUCCESS" for x in results),
        }, indent=2) + "\n")
    finally:
        oracle.terminate()
        oracle.wait(timeout=10)


if __name__ == "__main__":
    main()
