import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

from offline_checks import verify

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=["h1r3", "property", "intoto"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(ROOT):
        raise SystemExit("Use a fresh output directory outside the package")
    integrity = verify(ROOT)
    if integrity["integrity"] != "PASS":
        raise SystemExit(json.dumps(integrity))
    output.mkdir(parents=True)
    if args.task == "h1r3":
        component = ROOT / "h1r3/h1r3_complete_replay_v1"
        return subprocess.call([sys.executable, "-B", str(component / "execute_replay.py"),
            "--root", str(component / "retained"), "--output", str(output / "fresh_execution")])

    workspace = output / "workspace"
    shutil.copytree(ROOT / "source", workspace)
    phase = workspace / "sp2027/analysis/acts_next_phase_20261019_v2"
    if args.task == "property":
        stage = phase / "stage1_e2a"
        model = phase / "stage4_arms"
        contract = phase / "heb2_contract_v1"
        corpora = [
            ("stage1_scripted", stage / "runs/20261020T065943Z_confirmatory", stage / "frozen"),
            ("heb2_scripted", contract / "runs/20261020T091958Z_v2", contract / "trust"),
            ("model_arm_run1", model / "runs/attempt1_20261020T082440Z_model_arm", model / "attempt1/trust"),
            ("model_arm_run2", model / "runs/20261020T090143Z_model_arm", model / "trust"),
        ]
        for name, run, trust in corpora:
            code = subprocess.call([sys.executable, "-B", str(contract / "soundness_check_v2.py"),
                                    str(run), str(trust), str(output / (name + ".json"))])
            if code:
                return code
        return 0

    tools = [shutil.which(name) for name in ["in-toto-sign", "in-toto-verify"]]
    if not all(tools) or Path(tools[0]).parent != Path(tools[1]).parent:
        raise SystemExit("Install the observed in-toto dependencies in one environment before requesting this optional evaluation")
    relocations = []
    for path in phase.rglob("*.json"):
        if "baseline" not in path.parts:
            continue
        original = json.loads(path.read_text())
        def relocate(value):
            if isinstance(value, str) and value.startswith("/mnt/nvme5/ACTS-Attack/"):
                return str(workspace / value.removeprefix("/mnt/nvme5/ACTS-Attack/"))
            if isinstance(value, list):
                return [relocate(v) for v in value]
            if isinstance(value, dict):
                return {k: relocate(v) for k, v in value.items()}
            return value
        rebased = relocate(original)
        if rebased != original:
            path.write_text(json.dumps(rebased, indent=2, sort_keys=True) + "\n")
            relocations.append(str(path.relative_to(workspace)))
    (output / "relocations.json").write_text(json.dumps({"scope": "unsigned baseline copies only; signed E2A evidence unchanged",
        "files": relocations, "experimental_validation_of_adapter": "not performed during packaging"}, indent=2) + "\n")
    module_path = phase / "stage6_matched_translation/run_translation_v2.py"
    spec = importlib.util.spec_from_file_location("review_translation", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.VENV = Path(tools[0]).parent.parent
    module.RESULTS_PATH = output / "translation_results.json"
    module.run_slsa = lambda *_: {"returncode": 77, "stdout": "", "stderr": "SLSA network arm not run by the offline adapter", "stage": "not-run-offline"}
    sys.argv = [str(module_path), "--work", str(output / "translation_work")]
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
