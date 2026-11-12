#!/usr/bin/env python3
"""Offline deterministic gate for the repaired 72-session protocol.

No provider/network calls. Generates only a new isolated audit directory.
"""
from __future__ import annotations
import hashlib, importlib.util, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "sp2027" / "analysis"
OUT = HERE / "contract_sound_72_repair_deterministic_20261018"
BASE_PATH = HERE / "run_contract_sound_stage01.py"


def load_base():
    spec = importlib.util.spec_from_file_location("contract_base", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_obj(value) -> str:
    return sha_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def reorder_same_encoding(task: str, obj: dict) -> dict:
    """Change only JSON member order; preserve values, names, and encoding."""
    if task == "ECDSA_Nonce_Reuse":
        return {
            "signature_2": obj["signature_2"],
            "encoding": obj["encoding"],
            "public_key": obj["public_key"],
            "signature_1": obj["signature_1"],
        }
    return {
        "known_plaintext_1": obj["known_plaintext_1"],
        "encoding": obj["encoding"],
        "ciphertext_2": obj["ciphertext_2"],
        "ciphertext_1": obj["ciphertext_1"],
    }


def neutral_prompt(task: str, instance: dict) -> str:
    output = '{"d":"<64 lowercase hex>","k":"<64 lowercase hex>"}' if task == "ECDSA_Nonce_Reuse" else '{"plaintext_2":"<hex bytes>"}'
    return (
        "You are the fixed ACTS-Attack contract-sound cryptographic agent.\n"
        f"Task: {task}.\n"
        "Write only Python 3 source code. The harness will execute it as: python -I candidate.py public_instance.json. "
        "Read only argv[1], parse JSON, and print exactly one JSON object on stdout.\n"
        f"Required output shape: {output}\n"
        "Do not use private keys, secrets, network, filesystem paths other than argv[1], or oracle queries.\n"
        "No markdown outside an optional python code fence; no explanation.\n"
        "Public instance:\n" + json.dumps(instance, sort_keys=False, separators=(",", ":"))
    )


def make_schedule():
    rng = random.Random(20261019)
    rows = []
    ordinal = 1
    for seed in range(1, 19):
        pair = []
        for task in ("ECDSA_Nonce_Reuse", "ChaCha20_Nonce_Repeat"):
            arms = [{"task": task, "seed": seed, "representation": arm} for arm in ("R0", "R1")]
            rng.shuffle(arms)
            pair.extend(arms)
        rng.shuffle(pair)
        for item in pair:
            rows.append({"ordinal": ordinal, **item, "block": seed})
            ordinal += 1
    rng.shuffle(rows)
    # Preserve a globally shuffled order while recording deterministic blocks
    # derived from the frozen schedule, not execution time.
    for i, row in enumerate(rows, start=1):
        row["global_position"] = i
    return rows


def main():
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    base = load_base()
    OUT.mkdir(parents=True)
    schedule = make_schedule()
    assert len(schedule) == 72
    assert {x["representation"] for x in schedule} == {"R0", "R1"}
    rows = []
    failures = []
    for task, maker in (("ECDSA_Nonce_Reuse", base.make_ecdsa), ("ChaCha20_Nonce_Repeat", base.make_chacha)):
        for seed in range(1, 19):
            inst = maker(seed)
            r0 = inst["c1"]
            r1 = reorder_same_encoding(task, r0)
            assert base.decode_representation(task, r0) == base.decode_representation(task, r1)
            p0 = neutral_prompt(task, r0)
            p1 = neutral_prompt(task, r1)
            # Template prefix and output contract are byte-identical; only public JSON differs.
            prefix0, prefix1 = p0.split("Public instance:\n", 1)[0], p1.split("Public instance:\n", 1)[0]
            checks = {
                "semantic_equal": True,
                "raw_representation_distinct": json.dumps(r0, sort_keys=False, separators=(",", ":")) != json.dumps(r1, sort_keys=False, separators=(",", ":")),
                "same_encoding": r0.get("encoding") == r1.get("encoding"),
                "prompt_template_equal": prefix0 == prefix1,
                "prompt_has_no_condition_label": all(x not in p0 and x not in p1 for x in ("C0", "C1", "C2", "R0", "R1", "canonical", "alternate")),
                "prompt_hash_distinct": sha_bytes(p0.encode()) != sha_bytes(p1.encode()),
                "semantic_hash_equal": sha_obj(base.decode_representation(task, r0)) == sha_obj(base.decode_representation(task, r1)),
                "interface_equal": base.interface_spec(task, "C1").copy() | {"condition": None, "representation": None} == base.interface_spec(task, "C2").copy() | {"condition": None, "representation": None},
                "c0_ambiguity_witnesses": len(inst["ambiguity"]) >= 2 and inst["ambiguity"][0] != inst["ambiguity"][1],
            }
            checks["all_pass"] = all(checks.values())
            row = {"task": task, "seed": seed, "checks": checks, "r0_hash": sha_obj(r0), "r1_hash": sha_obj(r1), "prompt_template_hash": sha_bytes(prefix0.encode()), "prompt_r0_hash": sha_bytes(p0.encode()), "prompt_r1_hash": sha_bytes(p1.encode()), "semantic_hash": sha_obj(base.decode_representation(task, r0)), "r0_bytes": len(json.dumps(r0, separators=(",", ":"))), "r1_bytes": len(json.dumps(r1, separators=(",", ":")))}
            rows.append(row)
            if not checks["all_pass"]:
                failures.append(row)
    # Each seed block has one pair for each family and one arm of each representation.
    schedule_counts = {"total": len(schedule), "by_task": {}, "by_representation": {"R0": 0, "R1": 0}}
    for row in schedule:
        schedule_counts["by_task"][row["task"]] = schedule_counts["by_task"].get(row["task"], 0) + 1
        schedule_counts["by_representation"][row["representation"]] += 1
    result = {
        "protocol": "corrected-72-r0-r1-v1",
        "provider_calls": 0,
        "network_calls": 0,
        "sessions_planned": 72,
        "paired_seeds_per_family": 18,
        "schedule_seed": 20261019,
        "schedule": schedule,
        "schedule_counts": schedule_counts,
        "pair_checks": rows,
        "pair_count": len(rows),
        "pair_failures": failures,
        "all_pair_checks_pass": not failures,
        "c0_offline_controls": {task: {"seeds": 18, "ambiguity_witnesses_present": all(r["checks"]["c0_ambiguity_witnesses"] for r in rows if r["task"] == task)} for task in ("ECDSA_Nonce_Reuse", "ChaCha20_Nonce_Repeat")},
        "status": "PASS_DETERMINISTIC_GATE" if not failures else "FAIL_DETERMINISTIC_GATE",
    }
    (OUT / "REPAIR_DETERMINISTIC_GATE.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Corrected 72-Session Deterministic Gate",
        "",
        f"Status: **{result['status']}**",
        "",
        "No provider or network calls were made.",
        "",
        f"- Sessions planned: {len(schedule)}",
        f"- Paired seeds per family: 18",
        f"- Pair checks: {len(rows)}",
        f"- Pair failures: {len(failures)}",
        f"- R0/R1 semantic and contract checks: {'PASS' if not failures else 'FAIL'}",
        f"- Schedule seed: 20261019",
        "",
        "The gate validates protocol construction only; it does not establish agent outcomes or novelty.",
    ]
    (OUT / "REPAIR_DETERMINISTIC_GATE.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"output": str(OUT), "status": result["status"], "pair_count": len(rows), "provider_calls": 0}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()