#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

sys.path.insert(0, str(Path(__file__).resolve().parent))
from durable_runner import DurableRunner
from fixture_qualification import rc4
from h1_fixtures import xor_instance

OUT = Path(__file__).resolve().parent
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def fenced_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def ecdsa_instance(seed):
    d = seed + 1
    private = ec.derive_private_key(d, ec.SECP256K1())
    public = private.public_key()
    m1, m2 = f"matched-message-{seed}-one".encode(), f"matched-message-{seed}-two".encode()
    gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
    gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
    prime = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

    def add(a, b):
        if a is None: return b
        if b is None: return a
        if a[0] == b[0] and (a[1] + b[1]) % prime == 0: return None
        slope = ((3 * a[0] * a[0]) * pow(2 * a[1], -1, prime) if a == b else
                 (b[1] - a[1]) * pow(b[0] - a[0], -1, prime)) % prime
        x = (slope * slope - a[0] - b[0]) % prime
        return x, (slope * (a[0] - x) - a[1]) % prime

    def mul(k, point=(gx, gy)):
        out = None
        while k:
            if k & 1: out = add(out, point)
            point = add(point, point)
            k >>= 1
        return out

    k = seed + 101
    r = mul(k)[0] % N
    signatures = []
    for message in (m1, m2):
        z = int.from_bytes(hashlib.sha256(message).digest(), "big")
        s = pow(k, -1, N) * (z + r * d) % N
        signatures.append(encode_dss_signature(r, s).hex())
    pn = public.public_numbers()
    public_obs = {"curve": "secp256k1", "public_key_x": format(pn.x, "064x"),
                  "public_key_y": format(pn.y, "064x"), "message_one": m1.decode(),
                  "message_two": m2.decode(), "signature_one_der": signatures[0],
                  "signature_two_der": signatures[1]}
    return public_obs, d


def rc4_instance(seed):
    key = hashlib.sha256(f"rc4-key-{seed}".encode()).digest()[:16]
    known = f"known-prefix-{seed:02d}".encode().ljust(16, b"!")[:16]
    target = hashlib.sha256(f"rc4-target-{seed}".encode()).digest()[:16]
    return {"known_plaintext": known.hex(), "known_ciphertext": rc4(key, known).hex(),
            "target_ciphertext": rc4(key, target).hex()}, target


def build_prompt(family, condition, public):
    name = {"named": {"rc4": "RC4 keystream reuse", "ecdsa": "ECDSA repeated nonce reuse", "xor": "XOR mask relation"},
            "unnamed": {"rc4": "", "ecdsa": "", "xor": ""}}.get(condition, {}).get(family, "")
    if condition == "undetermined":
        instruction = "The observations are intentionally insufficient for a unique secret. Return JSON with decision exactly ABSTAIN_UNDERDETERMINED and no guessed secret."
    else:
        instruction = "Return JSON only. Infer the requested value from the public observations. Do not include explanations or markdown."
    schema = {"rc4": {"target_plaintext_hex": "32 hex chars"},
              "ecdsa": {"private_key_hex": "64 hex chars"},
              "xor": {"mask_hex": "32 hex chars"}}[family]
    return (f"{instruction} {'The named mechanism is: ' + name + '.' if name else ''} "
            f"Family={family}. Required schema={json.dumps(schema)}. Public observations={json.dumps(public, sort_keys=True)}")


def score(family, condition, obj, truth, public):
    if condition == "undetermined":
        return {"decision": obj.get("decision") if obj else None,
                "correct_decision": bool(obj and obj.get("decision") == "ABSTAIN_UNDERDETERMINED"),
                "truth_exposed": False}
    if not obj:
        return {"correct": False, "reason": "MALFORMED_OUTPUT", "truth_exposed": False}
    field = {"rc4": "target_plaintext_hex", "ecdsa": "private_key_hex", "xor": "mask_hex"}[family]
    value = obj.get(field, "")
    ok_shape = isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]+", value or "") is not None
    if family == "ecdsa":
        ok_shape = ok_shape and len(value) == 64
        if ok_shape:
            try:
                candidate = ec.derive_private_key(int(value, 16), ec.SECP256K1()).public_key().public_numbers()
                ok = format(candidate.x, "064x") == public["public_key_x"] and format(candidate.y, "064x") == public["public_key_y"]
            except (ValueError, TypeError):
                ok = False
        else: ok = False
    else:
        ok_shape = ok_shape and len(value) == 32
        ok = ok_shape and value.lower() == truth.hex()
    return {"correct": bool(ok), "truth_exposed": False, "shape_valid": bool(ok_shape)}


def main():
    runner = DurableRunner()
    records = []
    for seed in range(1, 11):
        for family in ("rc4", "ecdsa", "xor"):
            if family == "rc4": public, truth = rc4_instance(seed)
            elif family == "ecdsa": public, truth = ecdsa_instance(seed)
            else: public, _, truth = xor_instance(seed)
            for condition in ("named", "unnamed", "undetermined"):
                observations = public if condition != "undetermined" else {"insufficient_observations": True, "family": family}
                prompt = build_prompt(family, condition, observations)
                arm = f"A_{family.upper()}_{condition.upper()}"
                result = runner.run_provider_combination(arm, seed, "P009-H1-v1", prompt, max_tokens=256)
                obj = fenced_json(result.get("text", "")) if result.get("status") == "model_response" else None
                verdict = score(family, condition, obj, truth, public)
                record = {"arm_id": arm, "family": family, "condition": condition, "matched_seed": seed,
                          "protocol_version": "P009-H1-v1", "run_id": result.get("run_id"),
                          "provider_status": result.get("status"), "verdict": verdict,
                          "tokens": result.get("metadata", {}).get("usage", {}),
                          "cost_usd": result.get("metadata", {}).get("usage", {}).get("input_tokens", 0) * 0.000003 + result.get("metadata", {}).get("usage", {}).get("output_tokens", 0) * 0.000015}
                with (OUT / "h1_results.jsonl").open("a") as handle:
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
                records.append(record)
                print(json.dumps(record, sort_keys=True), flush=True)
    summary = {"records": len(records), "genuine_model_calls": sum(x["provider_status"] != "already_complete" for x in records),
               "correct": sum(x["verdict"].get("correct", False) or x["verdict"].get("correct_decision", False) for x in records),
               "cost_usd": sum(x["cost_usd"] for x in records)}
    (OUT / "h1_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
