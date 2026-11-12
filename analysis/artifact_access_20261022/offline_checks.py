import argparse
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def verify(root):
    root = root.resolve()
    manifest = json.loads((root / "MANIFEST.json").read_text())
    errors = []
    for relative, expected in manifest["files"].items():
        path = root / relative
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            errors.append({"path": relative, "error": "unsafe path"})
        elif not path.is_file():
            errors.append({"path": relative, "error": "missing"})
        elif path.stat().st_size != expected["bytes"] or sha(path) != expected["sha256"]:
            errors.append({"path": relative, "error": "changed"})
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()
              and p != root / "MANIFEST.json" and "__pycache__" not in p.parts}
    for relative in sorted(actual - manifest["files"].keys()):
        errors.append({"path": relative, "error": "unlisted"})
    phase = root / "source/sp2027/analysis/acts_next_phase_20261019_v2"
    if phase.is_dir():
        bindings = [
            ("stage1_e2a/runs/20261020T065943Z_confirmatory", "stage1_e2a/frozen"),
            ("heb2_contract_v1/runs/20261020T091958Z_v2", "heb2_contract_v1/trust"),
            ("stage4_arms/runs/attempt1_20261020T082440Z_model_arm", "stage4_arms/attempt1/trust"),
            ("stage4_arms/runs/20261020T090143Z_model_arm", "stage4_arms/trust"),
        ]
        for run, trust in bindings:
            trust_path = phase / trust / "issuers_public.json"
            certificates = list((phase / run / "cases").glob("*/certificate.e2a.json"))
            if not trust_path.is_file() or len(certificates) != 22:
                errors.append({"path": run, "error": "missing corpus or its own public trust bundle"})
                continue
            known = {row["key_id"] for row in json.loads(trust_path.read_text())["issuers"]}
            used = set()
            for path in certificates:
                for envelope in json.loads(path.read_text()).get("evidence", {}).values():
                    if isinstance(envelope, dict) and isinstance(envelope.get("record"), dict):
                        used.add(envelope["record"].get("key_id"))
            if used - known:
                errors.append({"path": run, "error": "certificate issuer IDs absent from selected trust bundle"})
    return {"integrity": "PASS" if not errors else "FAIL", "files": len(manifest["files"]),
            "errors": errors, "execution_performed": False}


def read(path):
    return json.loads(path.read_text())


def census(root):
    analysis = root / "source/sp2027/analysis"
    phase = analysis / "acts_next_phase_20261019_v2"
    fixed = [json.loads(line) for line in (root / "evidence/fixed_executor/operation_records.jsonl").read_text().splitlines() if line]
    fixed_rows = {}
    printed = {"RC4_Keystream": 0.214196, "ChaCha20_Nonce_Repeat": 0.131647,
               "CBC_Padding_Oracle": 1981.6, "ECDSA_Nonce_Reuse": 6.956}
    for condition in sorted({row["condition"] for row in fixed}):
        rows = [r for r in fixed if r["condition"] == condition]
        median = statistics.median(r["executor_op_span_ns"] for r in rows) / 1e6
        fixed_rows[condition] = {"successes": sum(r["verdict"] == "success" for r in rows),
            "records": len(rows), "median_executor_ms_from_this_file": median,
            "manuscript_reported_median_ms": printed[condition],
            "timing_provenance_resolved": abs(median - printed[condition]) < 0.01}
    ablations = {}
    paths = {"IAR-B dev": "iar_b/runs/20261019_112227/results.json",
             "IAR-B held-out": "iar_b_heldout/runs/20261019_114849/results.json",
             "IAR-C preserved": "iar_c/runs/20261019_121621/results.json"}
    c_attack = {f"S{i}" for i in range(4, 13)} | {"S14", "S15"}
    for name, relative in paths.items():
        cases = read(analysis / "experiment_b_20261019" / relative)["per_case"]
        def honest(case):
            a = case["adj"]
            return not a.get("malformed") and a.get("supported", 0) >= 1 and case.get("requested") is not None and case["requested"] <= a["supported"]
        attack = [c for c in cases if c["family"] in c_attack] if name == "IAR-C preserved" else [c for c in cases if not honest(c)]
        ablations[name] = {"cases": len(cases), "attack_inclusive": len(attack),
            "honest_within_evidence": sum(honest(c) for c in cases),
            "false_promotions": {v: sum(c["asserted"][v] == 6 and not c["adj"]["truth_strong"] for c in attack)
                                 for v in ["v2", "v3-sig", "v3-full"]}}
    soundness = []
    for path in sorted((phase / "heb2_contract_v1").glob("soundness_*.json")):
        d = read(path)
        soundness.append({"file": path.name, "corpus_size": d["corpus_size"],
            "evaluations_from_decision_census": sum(d["decision_census"].values()),
            "reported_evaluations": d["evaluations"], "violations": len(d["soundness_violations"]),
            "status": "archived aggregate reconstruction, not fresh evaluation"})
    translation = read(phase / "stage6_matched_translation/translation_results_v2.json")["rows"]
    toto = {arm: {"agreement": sum(r[arm]["accepted"] == (r["acts"]["output"]["decision"] == "ATTRIBUTED_SUCCESS") for r in translation),
                  "cases": len(translation)} for arm in ["in_toto_policy", "in_toto_policy_stateful"]}
    diagnostic = read(analysis / "lineage_20261020/lineage_recomputation.json")["ecdsa_cause_taxonomy"]
    defects = [r for r in diagnostic["sessions"] if r.get("order_defect")]
    return {"scope": "Recount retained records only; no candidate programs, policy evaluations or model calls executed",
            "fixed_executor": fixed_rows, "fixed_recorded_successes": sum(r["verdict"] == "success" for r in fixed),
            "ablation_record_recount": ablations, "soundness_aggregate_recount": soundness,
            "soundness_reported_evaluations": sum(r["evaluations_from_decision_census"] for r in soundness),
            "in_toto_archived_decision_recount": toto,
            "ecdsa_recorded_diagnostic": {"order_defect_records": len(defects), "recorded_corrected_scalars": sum(r["d_ok_with_correct_order"] for r in defects),
                                          "independently_reexecuted_now": False},
            "findings": [{"severity": "requires-provenance-resolution", "claim": "Fixed-executor timing medians",
                          "detail": "The supplied twelve recorded successes have different clock medians from the current manuscript. No values or records have been replaced."}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=["verify", "census"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output and args.output.resolve().is_relative_to(ROOT):
        raise SystemExit("Write reports outside the integrity-checked package")
    report = verify(ROOT)
    if report["integrity"] != "PASS":
        print(json.dumps(report, indent=2))
        raise SystemExit(1)
    if args.task == "census":
        report = census(ROOT)
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(payload)
    print(payload)
    raise SystemExit(2 if report.get("findings") else 0)
