#!/usr/bin/env python3
"""Write a P024 arm _REGISTRATION.json after the floor probe, before its first call.

Usage: build_p024_registration.py --arm a|b --floor 4200|8400
Refuses to overwrite. The seed receipt must verify and hold 24 distinct values;
both arms read the same receipt, enforcing the paired design.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "seeds_random_p024_20261103.json"
RUNNER = HERE / "run_info_contract_2x2_aesgcm.py"
ADAPTER = HERE / "provider_adapter_agentrouter_p024.py"
PROBE = HERE / "probe_p024_floor.json"
LABELS = {"a": "gpt-6.1-sol", "b": "gpt-5.6-sol"}
PROTOCOL = {"a": "P024A-INFO-CONTRACT-2X2-AESGCM-CSPRNG-PAIRED-v1",
            "b": "P024B-INFO-CONTRACT-2X2-AESGCM-CSPRNG-PAIRED-v1"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["a", "b"])
    ap.add_argument("--floor", required=True, type=int)
    ap.add_argument("--out", default=None, help="test hook: registration path")
    ap.add_argument("--probe", default=str(PROBE), help="test hook: probe path")
    args = ap.parse_args()

    out = Path(args.out) if args.out else (
        HERE / f"info_contract_aesgcm_p024{args.arm}_20261103" / "_REGISTRATION.json")
    out_dir = out.parent
    if out.exists():
        raise SystemExit(f"refusing to overwrite registration: {out}")
    receipt = json.loads(RECEIPT.read_text())
    seeds = list(receipt["draw_order"])
    if len(seeds) != 24 or len(set(seeds)) != 24:
        raise SystemExit("seed receipt is not 24 distinct values")
    canonical = json.dumps(sorted(seeds), separators=(",", ":")).encode()
    if hashlib.sha256(canonical).hexdigest() != receipt["seeds_sha256"]:
        raise SystemExit("seed receipt hash does not verify")
    probe = json.loads(Path(args.probe).read_text())
    if int(probe["decided_floor"]) != args.floor:
        raise SystemExit("floor does not match the probe decision")
    if args.floor not in (4200, 8400):
        raise SystemExit("floor must be the probed value 4200 or 8400")
    reg = {
        "protocol": PROTOCOL[args.arm],
        "fixture": "aesgcm",
        "label": LABELS[args.arm],
        "token_floor": args.floor,
        "token_floor_probe": {"file": PROBE.name,
                              "sha256": sha(Path(args.probe)),
                              "decision_rule": probe["decision_rule"],
                              "decided_floor": probe["decided_floor"],
                              "arm_b_expected_model_level_null":
                                  probe["arm_b_expected_model_level_null"]},
        "runner_path": "run_info_contract_2x2_aesgcm.py",
        "runner": sha(RUNNER),
        "adapter": "provider_adapter_agentrouter_p024.py",
        "adapter_sha256": sha(ADAPTER),
        "adapter_sha256_note": "P023 transport + registered floor + textless attribution",
        "transport_policy": {
            "max_attempts_per_call": 4,
            "backoff_seconds": [2, 5, 12],
            "jitter": False,
            "retried": "transport failures with no completion delivered",
            "never_retried": ["EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
                              "HTTP_ERROR outside the retry class",
                              "oracle/parse outcomes"],
            "forensics": "failure_log.jsonl (attempt, category, status, stop_reason, usage, body)",
        },
        "same_design_as": "P022-INFO-CONTRACT-2X2-AESGCM-CSPRNG-P022A/B-v1",
        "seed_receipt": RECEIPT.name,
        "seeds": seeds,
        "seeds_sha256": receipt["seeds_sha256"],
        "sessions_registered": 96,
        "paired_arm": "same 24 CSPRNG instances in both arms; floor identical across arms",
        "preregistration": "PREREGISTRATION.md",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(reg, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in reg.items() if k != "seeds"},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
