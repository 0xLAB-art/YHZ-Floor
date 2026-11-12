#!/usr/bin/env python3
"""Write P023's _REGISTRATION.json before the first provider call.

Refuses to overwrite an existing registration. Computes runner and adapter
hashes from disk and reads the seed receipt verbatim, so no value is retyped.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RECEIPT = ROOT / "seeds_random_20261103T080050Z.json"
RUNNER = ROOT / "run_info_contract_2x2_aesgcm.py"
ADAPTER = ROOT / "provider_adapter_agentrouter_p023.py"
PROTOCOL = "P023-INFO-CONTRACT-2X2-AESGCM-CSPRNG-SEEDS-v2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = HERE / "_REGISTRATION.json"
    if out.exists():
        raise SystemExit(f"refusing to overwrite registration: {out}")
    receipt = json.loads(RECEIPT.read_text())
    seeds = list(receipt["draw_order"])
    if len(seeds) != 96 or len(set(seeds)) != 96:
        raise SystemExit("seed receipt is not 96 distinct values")
    if receipt["seeds_sha256"] != hashlib.sha256(json.dumps(
            sorted(seeds), separators=(",", ":")).encode()).hexdigest():
        raise SystemExit("seed receipt hash does not verify")
    src = ADAPTER.read_text()
    floor = [ln for ln in src.splitlines() if ln.startswith("P017_TOKEN_FLOOR =")]
    if floor != ["P017_TOKEN_FLOOR = 4200"]:
        raise SystemExit(f"adapter floor is not 4200: {floor}")
    reg = {
        "protocol": PROTOCOL,
        "fixture": "aesgcm",
        "label": "gpt-6-astra",
        "token_floor": 4200,
        "runner_path": "run_info_contract_2x2_aesgcm.py",
        "runner": sha(RUNNER),
        "adapter": "provider_adapter_agentrouter_p023.py",
        "adapter_sha256": sha(ADAPTER),
        "transport_policy": {
            "max_attempts_per_call": 4,
            "backoff_seconds": [2, 5, 12],
            "jitter": False,
            "retried": "transport failures with no completion delivered",
            "never_retried": ["EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
                              "HTTP_ERROR outside the retry class",
                              "oracle/parse outcomes"],
            "forensics": "failure_log.jsonl (attempt, category, HTTP status, body excerpt)",
        },
        "same_design_as": "P021-INFO-CONTRACT-2X2-AESGCM-CSPRNG-SEEDS-v1",
        "seed_receipt": RECEIPT.name,
        "seeds": seeds,
        "seeds_sha256": receipt["seeds_sha256"],
        "sessions_registered": 384,
        "preregistration": "PREREGISTRATION.md",
    }
    out.write_text(json.dumps(reg, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in reg.items() if k != "seeds"},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
