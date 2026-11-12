import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def has_key(value, key):
    return isinstance(value, dict) and (key in value or any(has_key(v, key) for v in value.values())) or isinstance(value, list) and any(has_key(v, key) for v in value)


def main():
    repo = ROOT / "ACTS-ATTACK"
    relative = "data/A1_openssl_timing.json"
    revisions = subprocess.check_output(["git", "-C", str(repo), "log", "--all", "--format=%H", "--", relative], text=True).splitlines()
    history = []
    for revision in revisions:
        raw = subprocess.check_output(["git", "-C", str(repo), "show", revision + ":" + relative])
        value = json.loads(raw)
        history.append({"commit": revision, "blob_sha256": hashlib.sha256(raw).hexdigest(),
                        "contains_n_valid": has_key(value, "n_valid")})
    paths = [repo / relative, repo / "data/A1_vmware_timing.json"]
    wsl, vm = [json.loads(p.read_text()) for p in paths]
    checks = {"wsl_current_has_no_n_valid": not has_key(wsl, "n_valid"),
              "reachable_named_path_versions_have_no_n_valid": bool(history) and all(not v["contains_n_valid"] for v in history),
              "wsl_method_records_trials_and_rounds": "10k rounds, 10 trials" in wsl["results_v6_interleaved"]["method"],
              "vmware_explicit_n_valid": vm["parameters"]["n_valid"] == vm["results"]["n_valid"] == 90000}
    report = {"checks": checks, "all_pass": all(checks.values()), "named_path_git_history": history,
              "wsl_method": wsl["results_v6_interleaved"]["method"], "vmware_n_valid": vm["results"]["n_valid"],
              "interpretation": "No comparable WSL2 retained-valid-sample count established. Do not promote counts from later summaries or multiply round/chunk/trial units into an invented trimmed census.",
              "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (OUT / "COUNT_TRACE.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"checks": len(checks), "all_pass": report["all_pass"], "git_versions": len(history)}))
    if not report["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
