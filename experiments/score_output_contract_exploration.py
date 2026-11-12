import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
RUNS = BASE / "sp2027/analysis/checkpoint007_active_experiments/runs_009"
OUT = Path(__file__).resolve().parent / "exploratory_output_contract_20261017"
sys.path.insert(0, str(RUNS))
from fixture_qualification import rc4
from h1_campaign import ecdsa_instance
from h1_fixtures import xor_instance
from cryptography.hazmat.primitives.asymmetric import ec


def payload(path):
    d = json.loads(path.read_text())
    text = "\n".join(x.get("text", "") for x in d.get("content", []) if isinstance(x, dict))
    try:
        x = json.loads(text.strip())
        return x if isinstance(x, dict) else None
    except Exception:
        return None


def main():
    rows = []
    for row in [json.loads(x) for x in (OUT / "results.jsonl").read_text().splitlines() if x.strip()]:
        if row.get("provider_status") != "model_response":
            continue
        seed, family = int(row["seed"]), row["family"]
        d = payload(Path(row["raw_path"]))
        if family == "rc4":
            key = __import__("hashlib").sha256(f"rc4-key-{seed}".encode()).digest()[:16]
            known = f"known-prefix-{seed:02d}".encode().ljust(16, b"!")[:16]
            target = __import__("hashlib").sha256(f"rc4-target-{seed}".encode()).digest()[:16]
            ks = rc4(key, bytes(64))
            truth, field = target, "target_plaintext_hex"
            public = {"known_plaintext": known.hex(), "known_ciphertext": bytes(a ^ b for a, b in zip(known, ks[:16])).hex(), "target_ciphertext": bytes(a ^ b for a, b in zip(target, ks[:16])).hex()}
        elif family == "xor":
            public, _, truth = xor_instance(seed); field = "mask_hex"
        else:
            public, truth = ecdsa_instance(seed); field = "private_key_hex"
        value = d.get(field) if d else None
        valid = isinstance(value, str)
        if family == "ecdsa" and valid:
            try:
                point = ec.derive_private_key(int(value, 16), ec.SECP256K1()).public_key().public_numbers()
                recovered = format(point.x, "064x") == public["public_key_x"] and format(point.y, "064x") == public["public_key_y"]
            except (ValueError, TypeError):
                recovered = False
        else:
            recovered = valid and value.lower() == truth.hex()
        rows.append({"run_id": row["run_id"], "family": family, "seed": seed, "strict_json": bool(d), "candidate_field_present": field in d if d else False, "oracle_recovery": bool(recovered)})
    (OUT / "scored_results.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in rows))
    summary = json.loads((OUT / "summary.json").read_text())
    summary.update({"scored_provider_responses": len(rows), "oracle_recoveries": sum(x["oracle_recovery"] for x in rows), "scoring": "local qualified fixture/verifier; secrets not written to output"})
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
