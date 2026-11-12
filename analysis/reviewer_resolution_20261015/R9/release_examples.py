import hashlib
import json
import math
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ARCHIVES = ROOT / "human_audit/source_freeze_20261005/archives"


def main():
    incalmo = ARCHIVES / "incalmo__Incalmo__932c5fcd_head.tar.gz"
    cybench = ARCHIVES / "cybench__cybench__ca483c6443f1.tar.gz"
    with tarfile.open(incalmo) as archive:
        result_member = next(m for m in archive if m.name.endswith("output/example_output/results.json"))
        result = json.load(archive.extractfile(result_member))
        action_member = next(m for m in archive if m.name.endswith("output/example_output/action_log.jsonl"))
        actions = [json.loads(line) for line in archive.extractfile(action_member) if line.strip()]
    pointers = []
    with tarfile.open(cybench) as archive:
        for member in archive:
            if member.isfile() and "agent/outputs/" in member.name and member.size < 256:
                data = archive.extractfile(member).read()
                if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
                    pointers.append({"path": member.name, "pointer_sha256": hashlib.sha256(data).hexdigest(),
                                     "pointer": data.decode().strip()})
    clocks = {k: result[k] for k in ("experiment_time", "execution_time", "setup_time")}
    checks = {"example_has_50_infected_hosts": len(result["hosts_infected"]) == 50,
              "example_has_48_exfiltrated_files": len(result["data_exfiltrated"]) == 48,
              "example_has_614_action_records": len(actions) == 614,
              "example_timing_components_sum": math.isclose(clocks["experiment_time"], clocks["execution_time"] + clocks["setup_time"], abs_tol=1e-9),
              "five_cybench_output_lfs_pointers": len(pointers) == 5}
    output = {"checks": checks, "all_pass": all(checks.values()), "incalmo_example": {"result_member": result_member.name,
               "actions_member": action_member.name, "action_records": len(actions), "timing_components_seconds": clocks},
              "cybench_pointer_evidence": pointers,
              "interpretation": "Positive example timing/log evidence is not full-grid historical reconstruction. LFS pointers establish object references, not payload contents or global nonpublication.",
              "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (incalmo, cybench)}}
    (OUT / "WORKED_EXAMPLES.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"checks": len(checks), "all_pass": output["all_pass"]}))
    if not output["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
