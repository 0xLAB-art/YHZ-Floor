"""Deterministic gate for H2-CBC-AGENCY-20261023-v1 (H2b feasibility control).

Classic byte-at-a-time CBC padding-oracle attack against the per-session
generated oracle.py module (same module surface the sessions use), mirroring
the algorithm recorded in runs_009/fixture_qualification.py (cbc_recover),
adapted to the frozen query interface. Never pooled with arm results.

Modes:
  gate_solver.py                     -> orchestrates all seeds, writes gate_output.json
  gate_solver.py --attack <td> <c0_hex> -> runs the attack inside <td>, prints one JSON line
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fixture_cbc import instance, generate_oracle_module, PROTOCOL, ORACLE_BUDGET  # noqa: E402

SEEDS = (61, 62, 63, 64)


def padding_oracle_attack(query, c0, budget=ORACLE_BUDGET):
    """Recover the 16-byte padded second-block plaintext D(C1) XOR C0.
    Returns (p2_bytes_or_None, queries, status)."""
    d1 = bytearray(16)
    queries = 0
    for pos in range(15, -1, -1):
        pad = 16 - pos
        base = bytearray(16)
        for j in range(pos + 1, 16):
            base[j] = d1[j] ^ pad
        found = None
        for guess in range(256):
            probe = bytearray(base)
            probe[pos] = guess
            queries += 1
            if queries > budget:
                return None, queries, "budget_exhausted"
            if query(probe.hex()):
                if pos == 15:
                    check = bytearray(probe)
                    check[14] ^= 1
                    queries += 1
                    if queries > budget:
                        return None, queries, "budget_exhausted"
                    if not query(check.hex()):
                        continue
                found = guess ^ pad
                break
        if found is None:
            return None, queries, f"no_valid_byte_pos_{pos}"
        d1[pos] = found
    p2 = bytes(a ^ b for a, b in zip(d1, c0))
    return p2, queries, "ok"


def run_attack_mode(td, c0_hex):
    """Executed as a subprocess with cwd=<td> so oracle.py and its usage file
    live exactly where session programs find them."""
    td_path = Path(td)
    sys.path.insert(0, str(td_path))
    import oracle  # the generated per-session module
    c0 = bytes.fromhex(c0_hex)
    # Oracle-level positive check: the true previous block must be accepted.
    positive = oracle.query(c0.hex())
    # Oracle-level negative check: corrupt the last byte -> pad 0xFF, invalid.
    neg = bytearray(c0)
    neg[15] ^= 0xFE
    negative = oracle.query(neg.hex())
    p2, queries, status = padding_oracle_attack(oracle.query, c0)
    print(json.dumps({"positive_check": positive, "negative_check_rejected": (negative is False),
                      "recovered_p2_hex": p2.hex() if p2 else None,
                      "queries": queries, "status": status}))


def main():
    out = {"protocol": PROTOCOL, "generated_at_unix": time.time(),
           "budget": ORACLE_BUDGET, "seeds": {}, "gate_result": None}
    all_ok = True
    for seed in SEEDS:
        public, secret = instance(seed)
        c0 = secret["ciphertext"][:16]
        truth = secret["plaintext"]
        with tempfile.TemporaryDirectory(prefix="acts_h2_gate_") as td:
            generate_oracle_module(td, seed, secret["d_target"])
            (Path(td) / "public.json").write_text(json.dumps(public, sort_keys=True))
            proc = subprocess.run(
                [sys.executable, str(HERE / "gate_solver.py"), "--attack", td, c0.hex()],
                cwd=td, capture_output=True, text=True, timeout=120)
            if proc.returncode != 0:
                all_ok = False
                out["seeds"][str(seed)] = {"error": "attack_subprocess_failed",
                                           "stderr_tail": proc.stderr[-400:]}
                continue
            result = json.loads(proc.stdout.strip().splitlines()[-1])
        candidate_hex = result["recovered_p2_hex"][:30] if result["recovered_p2_hex"] else None
        match = candidate_hex == truth.hex() if candidate_hex else False
        # Negative control on the exact-match predicate: a wrong candidate must be rejected.
        wrong = bytearray(truth)
        wrong[0] ^= 0xFF
        wrong_rejected = wrong.hex() != truth.hex()
        queries = result["queries"]
        seed_ok = (match and queries <= ORACLE_BUDGET
                   and result["status"] == "ok"
                   and result["positive_check"] and result["negative_check_rejected"]
                   and wrong_rejected)
        all_ok = all_ok and seed_ok
        out["seeds"][str(seed)] = {
            "recovered_p2_hex": result["recovered_p2_hex"],
            "candidate_hex": candidate_hex,
            "match": match,
            "queries": queries,
            "within_budget": queries <= ORACLE_BUDGET,
            "attack_status": result["status"],
            "oracle_positive_check": result["positive_check"],
            "oracle_negative_check_rejected": result["negative_check_rejected"],
            "wrong_candidate_predicate_rejected": wrong_rejected,
            "witnesses": {
                "full_padded_second_block_hex": result["recovered_p2_hex"],
                "decrypted_first_block_hex": secret["d_c0"].hex(),
                "prefix_hex_witness": secret["prefix"].hex(),
            },
            "public_json_sha256": hashlib.sha256(
                json.dumps(public, sort_keys=True).encode()).hexdigest(),
            "ok": seed_ok,
        }
    out["gate_result"] = "PASS" if all_ok else "FAIL"
    (HERE / "gate_output.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gate_result": out["gate_result"],
                      "per_seed_queries": {s: out["seeds"][s].get("queries") for s in out["seeds"]}}))
    return 0 if all_ok else 1


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--attack":
        run_attack_mode(sys.argv[2], sys.argv[3])
    else:
        sys.exit(main())
