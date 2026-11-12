import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from durable_runner import DurableRunner


def grader_map():
    candidate = b"IDENTICAL_CANDIDATE_BYTES"
    variants = []
    for name, label in (("V1", "ACCEPT"), ("V2", "REJECT"), ("V3", "ACCEPT")):
        underlying_accept = candidate == b"IDENTICAL_CANDIDATE_BYTES"
        variants.append({"variant": name, "candidate_sha256": __import__("hashlib").sha256(candidate).hexdigest(),
                         "recorded_label": label, "underlying_accept": underlying_accept})
    return {"candidate_bytes_identical": len({x["candidate_sha256"] for x in variants}) == 1,
            "underlying_acceptance_invariant": len({x["underlying_accept"] for x in variants}) == 1,
            "recorded_labels_differ": len({x["recorded_label"] for x in variants}) > 1,
            "variants": variants}


def exec_contract():
    code = "import sys; print('VERDICT_ACCEPT_ON_ARGV' if sys.argv[1:] == ['contract'] else 'NO_VERDICT')"
    argv = subprocess.run([sys.executable, "-c", code, "contract"], capture_output=True, text=True, check=False)
    stdin = subprocess.run([sys.executable, "-c", code], input="contract\n", capture_output=True, text=True, check=False)
    return {"argv_stdout": argv.stdout.strip(), "stdin_stdout": stdin.stdout.strip(),
            "argv_verdict": argv.stdout.strip() == "VERDICT_ACCEPT_ON_ARGV",
            "stdin_failure_reproduced": stdin.stdout.strip() == "NO_VERDICT"}


def main():
    runner = DurableRunner()
    gm = grader_map()
    ec = exec_contract()
    print(json.dumps({"E_GRADER_MAP": gm, "E_EXEC_CONTRACT": ec}, indent=2))
    assert gm["candidate_bytes_identical"] and gm["underlying_acceptance_invariant"] and gm["recorded_labels_differ"]
    assert ec["argv_verdict"] and ec["stdin_failure_reproduced"]
    runner.complete_local_control("E_GRADER_MAP", gm)
    runner.complete_local_control("E_EXEC_CONTRACT", ec)


if __name__ == "__main__":
    main()
