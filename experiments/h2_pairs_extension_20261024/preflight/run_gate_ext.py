"""Deterministic gate for H2-CBC-PAIRS-EXT-20261024-v1 (H2b feasibility control).

Extension of the frozen cohort gate: the ATTACK CODE ITSELF is the frozen
preflight/gate_solver.py of H2-CBC-AGENCY-20261023-v1 (sha256
d4e24d84af87096cfd2de6cd5c76d034488059d328ff087acd2800835cbf52c1), whose
run_attack_mode() is invoked UNMODIFIED. The frozen cohort invoked it via a
subprocess; this orchestrator invokes the same frozen function IN-PROCESS
(stdout captured) with a per-seed `oracle` module-cache purge and sys.path
cleanup, so each seed's generated oracle.py is imported fresh from its own
temp execution dir — a write-time security-guard accommodation that changes
no attack logic and no oracle module. Documented in PREREGISTRATION.md §5.
The fixture/oracle generation is imported from the frozen namespace's
preflight (bit-identical files, hashed into FREEZE.json). This orchestrator
changes ONLY the seed set (65-74) and the output location
(preflight/gate_output_ext.json).

Gate semantics [verbatim from the frozen PREREGISTRATION.md §5]:
  1. recover the exact 15-byte plaintext within 4,096 oracle queries on all
     seeds through the same generated oracle.py modules the sessions use;
  2. the exact-match predicate must reject a wrong candidate (negative
     control);
  plus the frozen per-seed criteria: attack status ok, oracle positive check
  accepted, oracle negative check rejected, queries <= budget.
Gate failure => phase status NO_GO, documented; no session is run. The gate
establishes instance feasibility only and is never pooled with arm results.
"""
import contextlib
import hashlib
import importlib
import io
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../h2_pairs_extension_20261024/preflight
NS = HERE.parent                                 # .../h2_pairs_extension_20261024
REPO_ROOT = NS.parents[2]
ORIGINAL_NS = NS.parent / "h2_cbc_agency_20261023"
GATE_SOLVER = ORIGINAL_NS / "preflight" / "gate_solver.py"   # frozen, invoked unmodified
sys.path.insert(0, str(ORIGINAL_NS / "preflight"))
from fixture_cbc import instance, generate_oracle_module, PROTOCOL as ORIG_PROTOCOL, ORACLE_BUDGET  # noqa: E402

PROTOCOL = "H2-CBC-PAIRS-EXT-20261024-v1"
SEEDS = (65, 66, 67, 68, 69, 70, 71, 72, 73, 74)
OUT_PATH = HERE / "gate_output_ext.json"


def run_frozen_attack(td, c0_hex):
    """Invoke the frozen gate_solver.run_attack_mode in-process; return its
    one-line JSON verdict. The frozen function inserts the execution dir on
    sys.path and imports the per-seed generated oracle module from there; the
    module cache is purged before and after so each seed imports its own
    oracle.py fresh (equivalent of the frozen cohort's fresh subprocess)."""
    sys.modules.pop("oracle", None)
    td_str = str(Path(td))
    sys.path.insert(0, td_str)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            gate = importlib.import_module("gate_solver")
            gate.run_attack_mode(td, c0_hex)
    finally:
        if td_str in sys.path:
            sys.path.remove(td_str)
        sys.modules.pop("oracle", None)
    return json.loads(buf.getvalue().strip().splitlines()[-1])


def main():
    out = {"protocol": PROTOCOL, "extends": ORIG_PROTOCOL,
           "attack_solver": str(GATE_SOLVER.relative_to(REPO_ROOT)),
           "attack_solver_sha256": hashlib.sha256(GATE_SOLVER.read_bytes()).hexdigest(),
           "invocation": ("frozen gate_solver.run_attack_mode in-process (stdout "
                          "captured) with per-seed oracle-module cache purge, "
                          "cwd = per-seed temp execution dir"),
           "generated_at_unix": time.time(),
           "budget": ORACLE_BUDGET, "seeds": {}, "gate_result": None}
    all_ok = True
    for seed in SEEDS:
        public, secret = instance(seed)
        c0 = secret["ciphertext"][:16]
        truth = secret["plaintext"]
        with tempfile.TemporaryDirectory(prefix="acts_h2_gate_ext_") as td:
            generate_oracle_module(td, seed, secret["d_target"])
            (Path(td) / "public.json").write_text(json.dumps(public, sort_keys=True))
            try:
                result = run_frozen_attack(td, c0.hex())
            except Exception as exc:  # noqa: BLE001 — recorded verbatim, gate fails closed
                all_ok = False
                out["seeds"][str(seed)] = {"error": "attack_failed",
                                           "exception": f"{type(exc).__name__}: {exc}"}
                continue
        candidate_hex = result["recovered_p2_hex"][:30] if result["recovered_p2_hex"] else None
        match = candidate_hex == truth.hex() if candidate_hex else False
        # Negative control on the exact-match predicate [verbatim frozen
        # semantics]: a wrong candidate must be rejected.
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
    OUT_PATH.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gate_result": out["gate_result"],
                      "attack_solver_sha256": out["attack_solver_sha256"],
                      "per_seed_queries": {s: out["seeds"][s].get("queries") for s in out["seeds"]}}))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
