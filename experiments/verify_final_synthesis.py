import ast
import collections
import csv
import hashlib
import importlib.util
import json
import pathlib
import sys
import types

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
BASE = ROOT / "sp2027/analysis/checkpoint007_active_experiments/runs_009"
CAT = ROOT / "docs/scientific_synthesis/2026-10-17-exhaustive-relation-discovery"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(BASE))
    spec = importlib.util.spec_from_file_location("h1_v2_contract_check", BASE / "revalidation_v2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    counts = collections.Counter()
    index = []
    csv.field_size_limit(20000000)
    with (CAT / "01_EXHAUSTIVE_EVIDENCE_CATALOG.csv").open() as handle:
        catalog = list(csv.DictReader(handle))
    families = sorted({row["experiment_family"] for row in catalog})
    for family in families:
        rows = [r for r in catalog if r["experiment_family"] == family]
        paths = sorted({p for r in rows for p in json.loads(r["source_paths"])})
        index.append({"claim_id": "FAMILY:" + family, "mechanism": family,
                      "experiment": ";".join(sorted({r["arm"] for r in rows})),
                      "cohort": ";".join(sorted({r["physical_run_or_cohort"] for r in rows})),
                      "run_ids": ";".join(sorted({r["run_ids"] for r in rows})),
                      "raw_evidence": json.dumps(paths), "result": "Catalog source mapping; see statement IDs",
                      "statistical_unit": "catalog family; overlapping experiments possible",
                      "limitations": "Catalog statements and copies are not independent trials; source-specific restrictions retained in catalog",
                      "final_conclusion": "Source-bound disposition in final synthesis",
                      "source_sha256": digest(CAT / "01_EXHAUSTIVE_EVIDENCE_CATALOG.csv"),
                      "statement_ids": ";".join(r["evidence_id"] for r in rows)})
    results = [json.loads(l) for l in (BASE / "revalidation_v2/results.jsonl").read_text().splitlines()]
    for row in results:
        path = BASE / "revalidation_v2/raw_provider_responses" / (row["run_id"] + ".json")
        raw = json.loads(path.read_text())
        text = "\n".join(b.get("text", "") for b in raw.get("content", []))
        obj = mod.parser(text)
        field = {"xor": "mask_hex", "rc4": "target_plaintext_hex", "ecdsa": "private_key_hex"}[row["family"]]
        counts["responses"] += 1
        counts["parseable"] += obj is not None
        if row["condition"] != "undetermined":
            counts["requested_candidate_fields"] += bool(obj and field in obj)
        corrected = None
        if row["family"] == "xor" and row["condition"] != "undetermined":
            public, mask, _ = mod.xor_instance(row["matched_seed"])
            corrected = bool(obj and obj.get("mask_hex", "").lower() == mask.hex())
            counts["xor_correct_requested_mask"] += corrected
        index.append({"claim_id": "H1:" + row["run_id"], "mechanism": row["family"],
                      "experiment": "P009-H1-v2", "cohort": row["condition"], "run_ids": row["run_id"],
                      "raw_evidence": str(path.relative_to(ROOT)),
                      "result": json.dumps({"stored": row["verdict"], "corrected_mask": corrected}),
                      "statistical_unit": "provider response; matched_seed=" + str(row["matched_seed"]),
                      "limitations": "XOR scorer truth mismatch; UNDET explicitly instructed; no program execution",
                      "final_conclusion": "response contract observation", "source_sha256": digest(path), "statement_ids": ""})
    checks = []
    for seed in range(1, 11):
        public, mask, target = mod.xor_instance(seed)
        sample = public["samples"][0]
        recovered = bytes(a ^ b for a, b in zip(bytes.fromhex(sample["x"]), bytes.fromhex(sample["y"])))
        checks.append({"seed": seed, "public_mask_correct": recovered == mask,
                       "correct_mask_rejected": not mod.score("xor", "named", {"mask_hex": recovered.hex()}, target, public)["correct"],
                       "plaintext_in_mask_field_accepted": mod.score("xor", "named", {"mask_hex": target.hex()}, target, public)["correct"]})
    assert all(all(v for k, v in r.items() if k != "seed") for r in checks)
    recent = []
    for directory in sorted(OUT.glob("*")):
        if not directory.is_dir() or not (directory / "results.jsonl").exists() or "output_contract" in directory.name:
            continue
        if not (directory.name.startswith("exploratory_code_feedback") or directory.name.startswith("blind_opportunity")):
            continue
        rows = [json.loads(l) for l in (directory / "results.jsonl").read_text().splitlines()]
        unique = {r["run_id"]: r for r in rows}
        recent.append({"namespace": directory.name, "records": len(rows), "unique_runs": len(unique),
                       "statuses": dict(collections.Counter(r["status"] for r in unique.values()))})
        for row in unique.values():
            index.append({"claim_id": "CODE:" + row["run_id"], "mechanism": directory.name,
                          "experiment": row.get("protocol", ""), "cohort": directory.name,
                          "run_ids": row["run_id"], "raw_evidence": str((directory / "events.jsonl").relative_to(ROOT)),
                          "result": row["status"], "statistical_unit": "session; seed=" + str(row["seed"]),
                          "limitations": "synthetic selected fixture; route identity only; blind ChaCha removes reference fact",
                          "final_conclusion": "verified local construction observation; v1 schema defect excluded",
                          "source_sha256": digest(directory / "results.jsonl"), "statement_ids": ""})
    duplicate_rows = list(csv.DictReader((CAT / "02_SOURCE_AND_DUPLICATE_MAP.csv").open()))
    groups = collections.Counter(r["sha256"] for r in duplicate_rows if r["sha256"])
    source = OUT / "run_code_feedback_chacha20.py"
    functions = [n for n in ast.parse(source.read_text()).body
                 if isinstance(n, ast.FunctionDef) and n.name in {"encrypt", "instance", "prompt"}]
    scope = {"hashlib": hashlib, "json": json, "Cipher": Cipher, "algorithms": algorithms,
             "os": types.SimpleNamespace(environ={"ACTS_PROMPT_VARIANT": "blind-opportunity-v1"})}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), "exec"), scope)
    blind_events = [json.loads(l) for l in (OUT / "blind_opportunity_chacha20_20261018/events.jsonl").read_text().splitlines()]
    chacha_checks = []
    for seed in (7, 8):
        public, truth = scope["instance"](seed)
        text = scope["prompt"](public)
        start = next(e for e in blind_events if e["kind"] == "model_start" and e["seed"] == seed and e["turn"] == 1)
        recovered = bytes(a ^ b for a, b in zip(bytes.fromhex(public["c1_hex"]), bytes.fromhex(public["c2_hex"])))
        chacha_checks.append({"seed": seed, "reconstructed_prompt_hash_matches": hashlib.sha256(text.encode()).hexdigest() == start["prompt_sha256"],
                              "algorithm_label_still_present": public.get("algorithm") == "ChaCha20",
                              "nonce_reuse_label_still_present": public.get("nonce_reuse") is True,
                              "zero_reference_fact_missing": "all-zero" not in text and "zero reference" not in text,
                              "zero_reference_solver_matches_truth": recovered == truth})
    assert all(all(v for k, v in r.items() if k != "seed") for r in chacha_checks)
    v4 = []
    transcripts = ROOT / "sp2027/agent-eval/runs_r1_clean_capture_first_v4_claude46_20261014_02/transcripts"
    for path in sorted(transcripts.glob("*/transcript.jsonl")):
        events = [json.loads(l) for l in path.read_text().splitlines()]
        runs = [e for e in events if e.get("type") == "run"]
        v4.append({"run_id": path.parent.name, "programs": len(runs),
                   "accepted_attempts": [i for i, e in enumerate(runs, 1) if (e.get("verdict") or {}).get("verdict") == "success"],
                   "nonzero_exits": sum(e.get("exit") != 0 for e in runs)})
    validation = {"catalog_families": len(families), "catalog_statements": len(catalog),
                  "h1_semantic_counts": dict(counts), "xor_positive_control_checks": checks,
                  "chacha_prompt_and_public_solver_checks": chacha_checks,
                  "v4_trajectories": v4,
                  "recent_namespaces": recent,
                  "existing_duplicate_map": {"rows": len(duplicate_rows), "hash_groups": len(groups),
                                             "duplicate_excess": sum(n - 1 for n in groups.values())},
                  "provider_calls_this_analysis": 0, "new_provider_cost_usd": 0,
                  "source_hashes": {str(p.relative_to(ROOT)): digest(p) for p in
                                    [BASE / "revalidation_v2.py", BASE / "h1_fixtures.py", OUT / "run_code_feedback_chacha20.py"]}}
    with (OUT / "ACTS_ATTACK_FINAL_EVIDENCE_INDEX.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(index[0]))
        writer.writeheader()
        writer.writerows(index)
    with (OUT / "final_synthesis_validation.jsonl").open("a") as handle:
        handle.write(json.dumps(validation, sort_keys=True) + "\n")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
