#!/usr/bin/env python3
import hashlib
import json
import re
import sys
import time
import uuid
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture_qualification import rc4
from h1_campaign import ecdsa_instance
from h1_fixtures import xor_instance
from provider_adapter import ClaudeProvider, ProviderFailure

BASE = Path(__file__).resolve().parent
OUT = BASE / "revalidation_v2"
LOG = OUT / "events.jsonl"
STATE = OUT / "state.json"
RESULTS = OUT / "results.jsonl"
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def stream(key, n):
    return rc4(key, bytes(n))


def rc4_pair(seed, insufficient=False):
    key = hashlib.sha256(f"rc4-key-{seed}".encode()).digest()[:16]
    known = f"known-prefix-{seed:02d}".encode().ljust(16, b"!")[:16]
    target = hashlib.sha256(f"rc4-target-{seed}".encode()).digest()[:16]
    ks = stream(key, 64)
    if insufficient:
        public = {"known_plaintext": known.hex(), "known_ciphertext": bytes(a ^ b for a, b in zip(known, ks[:16])).hex(),
                  "target_ciphertext": bytes(a ^ b for a, b in zip(target, ks[32:48])).hex(),
                  "known_offset": 0, "target_offset": 32}
    else:
        public = {"known_plaintext": known.hex(), "known_ciphertext": bytes(a ^ b for a, b in zip(known, ks[:16])).hex(),
                  "target_ciphertext": bytes(a ^ b for a, b in zip(target, ks[:16])).hex(),
                  "known_offset": 0, "target_offset": 0}
    return public, target


def ecdsa_single(seed):
    public, _ = ecdsa_instance(seed)
    return {"curve": public["curve"], "public_key_x": public["public_key_x"], "public_key_y": public["public_key_y"],
            "message_one": public["message_one"], "signature_one_der": public["signature_one_der"]}


def xor_insufficient(seed):
    public, key, target = xor_instance(seed)
    sample = public["samples"][0]
    return {"samples": [{"x": sample["x"][:2], "y": sample["y"][:2]}], "ciphertext": public["ciphertext"]}, key, target


def parser(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def prompt(family, condition, public):
    names = {"rc4": "RC4 keystream reuse", "ecdsa": "ECDSA repeated nonce reuse", "xor": "XOR mask relation"}
    if condition == "named": prefix = f"The named mechanism is {names[family]}."
    elif condition == "unnamed": prefix = "No mechanism name is supplied. Infer the relation only from the observations."
    else: prefix = "These are genuine insufficient observations. Do not guess a unique secret; return decision ABSTAIN_UNDERDETERMINED."
    schema = {"rc4": "target_plaintext_hex", "ecdsa": "private_key_hex", "xor": "mask_hex"}[family]
    return f"{prefix} Return JSON only. Required field is {schema}. Public observations: {json.dumps(public, sort_keys=True)}"


def score(family, condition, obj, truth, public):
    if condition == "undetermined":
        return {"correct_decision": bool(obj and obj.get("decision") == "ABSTAIN_UNDERDETERMINED"), "truth_exposed": False}
    field = {"rc4": "target_plaintext_hex", "ecdsa": "private_key_hex", "xor": "mask_hex"}[family]
    value = obj.get(field, "") if obj else ""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]+", value): return {"correct": False, "reason": "MALFORMED_OUTPUT", "truth_exposed": False}
    if family == "ecdsa":
        try:
            candidate = ec.derive_private_key(int(value, 16), ec.SECP256K1()).public_key().public_numbers()
            ok = format(candidate.x, "064x") == public["public_key_x"] and format(candidate.y, "064x") == public["public_key_y"]
        except (ValueError, TypeError): ok = False
    else:
        ok = value.lower() == truth.hex()
    return {"correct": bool(ok), "truth_exposed": False}


class Store:
    def __init__(self):
        OUT.mkdir(exist_ok=True)
        self.state = json.loads(STATE.read_text()) if STATE.exists() else {"completed": [], "inflight": {}}

    def emit(self, run, kind, payload):
        with LOG.open("a") as h:
            h.write(json.dumps({"run_id": run, "kind": kind, "time": time.time(), **payload}, sort_keys=True) + "\n")
            h.flush()

    def save(self):
        STATE.write_text(json.dumps(self.state, indent=2) + "\n")

    def call(self, arm, seed, protocol, text):
        key = f"{arm}::{seed}::{protocol}"
        if key in self.state["completed"]: return {"status": "already_complete", "combination": key}
        run = f"sp2027_009_v2__{arm}__seed_{seed}__{uuid.uuid4().hex[:12]}"
        self.state["inflight"][key] = run; self.save()
        provider = ClaudeProvider()
        self.emit(run, "model_start", {"arm_id": arm, "matched_seed": seed, "protocol_version": protocol,
                                         "prompt_sha256": hashlib.sha256(text.encode()).hexdigest(), "provider_route": provider.model})
        try:
            result = provider.call(text, 256)
            raw = OUT / "raw_provider_responses"; raw.mkdir(exist_ok=True)
            path = raw / f"{run}.json"; path.write_bytes(result["raw_body"].encode("utf-8"))
            self.emit(run, "model_response", {"arm_id": arm, "matched_seed": seed, "protocol_version": protocol,
                                               "provider_metadata": result["metadata"], "raw_response_path": str(path)})
            self.state["completed"].append(key); self.state["inflight"].pop(key, None); self.save()
            return {"status": "model_response", "run_id": run, "text": result["text"], "metadata": result["metadata"]}
        except ProviderFailure as exc:
            self.emit(run, "provider_failure", {"arm_id": arm, "matched_seed": seed, "protocol_version": protocol,
                                                 "error_category": exc.category, "error": str(exc)})
            self.state["inflight"].pop(key, None); self.save()
            return {"status": exc.category, "run_id": run}


def main():
    store = Store(); records = []
    for seed in range(1, 11):
        for family in ("rc4", "ecdsa", "xor"):
            if family == "rc4": public, truth = rc4_pair(seed)
            elif family == "ecdsa": public, truth = ecdsa_instance(seed)
            else: public, _, truth = xor_instance(seed)
            for condition in ("named", "unnamed", "undetermined"):
                if condition == "undetermined":
                    if family == "rc4": observations, _ = rc4_pair(seed, True)
                    elif family == "ecdsa": observations = ecdsa_single(seed)
                    else: observations, _, _ = xor_insufficient(seed)
                else: observations = public
                arm_condition = "UNDET" if condition == "undetermined" else condition.upper()
                arm = f"A_{family.upper()}_{arm_condition}"
                result = store.call(arm, seed, "P009-H1-v2", prompt(family, condition, observations))
                obj = parser(result.get("text", "")) if result.get("status") == "model_response" else None
                verdict = score(family, condition, obj, truth, public)
                usage = result.get("metadata", {}).get("usage", {})
                record = {"arm_id": arm, "family": family, "condition": condition, "matched_seed": seed,
                          "protocol_version": "P009-H1-v2", "run_id": result.get("run_id"), "provider_status": result.get("status"),
                          "verdict": verdict, "tokens": usage,
                          "cost_usd": usage.get("input_tokens", 0) * .000003 + usage.get("output_tokens", 0) * .000015}
                with RESULTS.open("a") as h: h.write(json.dumps(record, sort_keys=True) + "\n")
                print(json.dumps(record, sort_keys=True), flush=True)
                records.append(record)
    summary = {"records": len(records), "provider_delivered": sum(x["provider_status"] == "model_response" for x in records),
               "correct": sum(x["verdict"].get("correct", False) or x["verdict"].get("correct_decision", False) for x in records),
               "estimated_cost_usd": round(sum(x["cost_usd"] for x in records), 6)}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__": main()
