#!/usr/bin/env python3
import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture_qualification import rc4
from h1_campaign import ecdsa_instance
from h1_fixtures import xor_instance
from revalidation_v2 import rc4_pair, ecdsa_single, xor_insufficient, prompt

BASE = Path(__file__).resolve().parent
OUT = BASE / "revalidation_v2"


def independent_fixture_checks():
    for seed in range(1, 11):
        public, truth = rc4_pair(seed)
        stream = bytes(a ^ b for a, b in zip(bytes.fromhex(public["known_plaintext"]), bytes.fromhex(public["known_ciphertext"])))
        assert bytes(a ^ b for a, b in zip(bytes.fromhex(public["target_ciphertext"]), stream)) == truth
        insufficient, _ = rc4_pair(seed, True)
        assert insufficient["known_offset"] != insufficient["target_offset"]
        ep, d = ecdsa_instance(seed)
        assert "signature_two_der" in ep and format(d, "064x") not in prompt("ecdsa", "named", ep)
        one = ep["signature_one_der"]
        assert one in prompt("ecdsa", "undetermined", ecdsa_single(seed))
        xp, key, target = xor_instance(seed)
        derived = bytes(a ^ b for a, b in zip(bytes.fromhex(xp["samples"][0]["x"]), bytes.fromhex(xp["samples"][0]["y"])))
        assert derived == key
        xi, _, _ = xor_insufficient(seed)
        assert len(bytes.fromhex(xi["samples"][0]["x"])) == 1


def raw_audit():
    rows = [json.loads(x) for x in (OUT / "results.jsonl").read_text().splitlines()]
    events = [json.loads(x) for x in (OUT / "events.jsonl").read_text().splitlines()]
    responses = {x["run_id"]: x for x in events if x["kind"] == "model_response"}
    assert len(rows) == 90 and len(responses) == 90
    for row in rows:
        event = responses[row["run_id"]]
        raw = Path(event["provider_metadata"].get("raw_response_path", event.get("raw_response_path", "")))
        if not raw.is_absolute():
            raw = Path(event.get("raw_response_path", ""))
        if not raw.exists():
            raw = OUT / "raw_provider_responses" / f"{row['run_id']}.json"
        assert raw.exists()
        observed = raw.read_bytes()
        exact_hash = hashlib.sha256(observed).hexdigest()
        normalized_hash = hashlib.sha256(observed[:-1] if observed.endswith(b"\n") else observed).hexdigest()
        assert event["provider_metadata"]["response_sha256"] in {exact_hash, normalized_hash}
        assert event["provider_metadata"]["http_status"] == 200
        assert event["provider_metadata"]["finish_reason"] == "end_turn"
    return rows


def main():
    registry = {x["arm_id"] for x in csv.DictReader((BASE.parent / "02_MATCHED_ARM_REGISTRY.csv").open())}
    expected = {f"A_{family}_{condition}" for family in ("RC4", "ECDSA", "XOR") for condition in ("NAMED", "UNNAMED", "UNDET")}
    assert expected <= registry
    independent_fixture_checks()
    rows = raw_audit()
    result = {"registry_valid": True, "unique_combinations": len({(x["arm_id"], x["matched_seed"], x["protocol_version"]) for x in rows}),
              "independent_fixture_checks": "PASS", "raw_response_hash_checks": "PASS", "provider_responses": len(rows),
              "model_oracle_successes": sum(x["verdict"].get("correct", False) for x in rows),
              "correct_underdetermination_decisions": sum(x["verdict"].get("correct_decision", False) for x in rows)}
    (OUT / "validation_report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()
