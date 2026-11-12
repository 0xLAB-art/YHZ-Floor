#!/usr/bin/env python3
"""Instance-level paired bootstrap for the same-program admission counterfactual.

External review (S&P simulation, R2 round 2) observed that the printed
regrade interval [-42.2, -21.9] pp has endpoints exactly equal to the two
per-family point estimates -- the signature of resampling at the family
level (2 units), which makes the percentile interval collapse to min/max.

This script recomputes the interval the honest way: the SAME estimand
(per-family regrade change, families weighted equally), with instances
resampled with replacement WITHIN each family, 50,000 draws, seed 20261021.

Internal gates (abort on failure, nothing is written unless all pass):
  1. the reconstructed pairs must total 128 (64 XOR + 64 ECDSA);
  2. the declared-rule contrast must reproduce -0.8 pp;
  3. the legacy-rule contrast must reproduce -32.8 pp;
  4. the per-family changes must reproduce -21.9 (XOR) and -42.2 (ECDSA)
     and their equal-weight combination -32.0 pp (point estimate unchanged;
     only the interval's resampling level is corrected).

Reads only frozen retained records. No provider call, no re-execution.
Writes analysis/regrade_bootstrap_instance_level.json when all gates pass.
"""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
H1R3 = HERE / "h1r3_20261019"
LEGACY_ALLOWED = {"json", "sys", "base64"}
LEVEL = "L3"
ARMS = ("R0", "R2")
SEED = 20261021
DRAWS = 50_000
FAMILIES = ("XOR_Keystream_Reuse", "ECDSA_Nonce_Reuse")

sys.path.insert(0, str(H1R3))
from policy_sensitivity import load, admitted  # noqa: E402


def main() -> int:
    imports, disp, ledger = load(H1R3)
    imports_by_session = {r["session_id"]: r["imported_modules"] for r in imports["rows"]}

    prim = [r for r in disp["rows"] if r.get("kind") == "primary"]
    groups = defaultdict(dict)
    for r in prim:
        if r.get("level") != LEVEL:
            continue
        groups[(r.get("family"), r.get("instance_id"))][r.get("arm")] = r
    complete = {k: v for k, v in groups.items() if set(ARMS) <= set(v)}

    ok = lambda r: bool(r.get("terminal_success"))
    pairs = []
    for (family, _iid), arms in sorted(complete.items()):
        base, treat = arms["R0"], arms["R2"]
        d_cur = int(ok(treat)) - int(ok(base))
        d_leg = (int(ok(treat) and admitted(imports_by_session,
                                            treat.get("session_id"), LEGACY_ALLOWED))
                 - int(ok(base) and admitted(imports_by_session,
                                             base.get("session_id"), LEGACY_ALLOWED)))
        pairs.append({"family": family, "d_current": d_cur, "d_legacy": d_leg})

    by_family = defaultdict(list)
    for p in pairs:
        by_family[p["family"]].append(p)

    # ---- gates -------------------------------------------------------------
    gates = {}
    gates["pairs_128"] = len(pairs) == 128
    gates["families_64_each"] = all(len(by_family.get(f, [])) == 64 for f in FAMILIES)
    cur_pp = 100.0 * sum(p["d_current"] for p in pairs) / len(pairs)
    leg_pp = 100.0 * sum(p["d_legacy"] for p in pairs) / len(pairs)
    gates["declared_minus_0_8"] = round(cur_pp, 1) == -0.8
    gates["legacy_minus_32_8"] = round(leg_pp, 1) == -32.8

    fam_change = {}
    for f in FAMILIES:
        rows = by_family[f]
        d_cur = sum(p["d_current"] for p in rows) / len(rows)
        d_leg = sum(p["d_legacy"] for p in rows) / len(rows)
        fam_change[f] = 100.0 * (d_leg - d_cur)
    gates["xor_minus_21_9"] = round(fam_change["XOR_Keystream_Reuse"], 1) == -21.9
    gates["ecdsa_minus_42_2"] = round(fam_change["ECDSA_Nonce_Reuse"], 1) == -42.2
    combined = (fam_change["XOR_Keystream_Reuse"] + fam_change["ECDSA_Nonce_Reuse"]) / 2
    gates["combined_minus_32_0"] = round(combined, 1) == -32.0

    if not all(gates.values()):
        print(json.dumps({"gates": gates, "abort": True}, indent=1))
        return 1

    # ---- instance-level within-family bootstrap ----------------------------
    rng = random.Random(SEED)
    stats = []
    xor_rows, ecdsa_rows = by_family["XOR_Keystream_Reuse"], by_family["ECDSA_Nonce_Reuse"]
    for _ in range(DRAWS):
        vals = []
        for rows in (xor_rows, ecdsa_rows):
            n = len(rows)
            d_cur = sum(rows[rng.randrange(n)]["d_current"] for _ in range(n)) / n
            d_leg = sum(rows[rng.randrange(n)]["d_legacy"] for _ in range(n)) / n
            vals.append(100.0 * (d_leg - d_cur))
        stats.append((vals[0] + vals[1]) / 2)
    stats.sort()

    def pct(q):
        i = q * (DRAWS - 1)
        lo = int(i)
        frac = i - lo
        if lo + 1 < DRAWS:
            return stats[lo] + frac * (stats[lo + 1] - stats[lo])
        return stats[lo]

    interval = [round(pct(0.025), 1), round(pct(0.975), 1)]

    # per-family intervals for transparency
    fam_intervals = {}
    for name, rows in (("XOR_Keystream_Reuse", xor_rows),
                       ("ECDSA_Nonce_Reuse", ecdsa_rows)):
        n = len(rows)
        ss = []
        for _ in range(DRAWS):
            dc = sum(rows[rng.randrange(n)]["d_current"] for _ in range(n)) / n
            dl = sum(rows[rng.randrange(n)]["d_legacy"] for _ in range(n)) / n
            ss.append(100.0 * (dl - dc))
        ss.sort()
        fam_intervals[name] = [round(ss[int(0.025 * (DRAWS - 1))], 1),
                               round(ss[int(0.975 * (DRAWS - 1))], 1)]

    out = {
        "schema": "regrade-bootstrap-instance-level/1.0",
        "motivation": "R2 round-2 observation: the printed interval's endpoints "
                      "equal the per-family point estimates, i.e. the earlier "
                      "resampling unit was the family (2 units). This script "
                      "resamples instances within family; the point estimate "
                      "is unchanged.",
        "seed": SEED,
        "draws": DRAWS,
        "gates": gates,
        "point_estimates_pp": {
            "declared_rule": round(cur_pp, 1),
            "legacy_rule": round(leg_pp, 1),
            "change_combined": round(combined, 1),
            "per_family": {f: round(v, 1) for f, v in fam_change.items()},
        },
        "instance_level_ci_95_pp": {
            "combined": interval,
            "per_family": fam_intervals,
        },
        "manuscript_sentence_after": (
            "a paired bootstrap (50,000 draws, seed 20261021; instances "
            "resampled within family, families weighted equally) gives an "
            f"unadjusted 95% interval [{interval[0]}, {interval[1]}] points "
            "for the -32.0 point change"),
    }
    dest = HERE / "regrade_bootstrap_instance_level.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("gates", "point_estimates_pp",
                                          "instance_level_ci_95_pp")}, indent=1))
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
