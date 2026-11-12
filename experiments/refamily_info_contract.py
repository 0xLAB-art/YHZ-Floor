#!/usr/bin/env python3
"""Regenerate the info-contract family-wise correction under ONE convention.

The published adjusted column could not be reproduced from the cohort artifacts
under any single rounding rule, so with the modern-AEAD wave closed this script
re-derives the whole family from the raw `results.jsonl` files and states the
conventions it uses:

  p            exact two-sided binomial on the paired C1-vs-C4 discordance,
               conditioned on the discordant pairs n = b10 + b01 (NOT on the
               number of evaluable pairs). Every member has zero discordant
               pairs in the C4 direction, so p = min(1, 2**(1-n)).
  Holm         step-down over the family sorted ascending, adjusted_i =
               min(1, max_{j<=i} (m-j+1) * p_j).
  rounding     three significant figures, ROUND_HALF_UP, decimal notation for
               |x| >= 1e-3 and scientific otherwise.
  Clopper-     exact two-sided 95% lower bound on the one-directional
  Pearson      discordance probability, two decimal places, ROUND_HALF_UP.
               With zero C4-direction pairs that is 0.025**(1/n).

Family membership: every evaluable paired replication registration. The
original discovery cohort (P010) and the controls with no discordance
(P011 saturated RC4, P012 observable-premise ECDSA) are excluded by design,
not by their values.

Run: python3 sp2027/research_execution/refamily_info_contract.py [--json PATH]
"""
from __future__ import annotations

import json
import math
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "analysis" / "INFO_CONTRACT_FAMILY.json"

TERM = {"HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
        "MALFORMED_PROVIDER_JSON", "PROVIDER_UNAVAILABLE", "CREDENTIAL_MISSING"}

# (name, cohort dir, optional arm subdir)
# The 2026-11-03 transport-repair wave re-ran every damaged registration on
# repaired routes; the family reads the COMPLETED registration for each member
# (the damaged first passes remain on disk as census exhibits).
ROSTER = [
    ("P010P", "info_contract_powered_20261025", None),
    ("P010N16", "info_contract_n16_20261026", None),
    ("P010X1", "info_contract_x1_gptoss_20261026", None),
    ("P010L2", "info_contract_label2_20261025__rerun_ar_20261103", None),
    ("P010L3", "info_contract_label3_20261029", None),
    ("P013", "info_contract_aesctr_20261026", None),
    ("P011-L3-N32", "info_contract_label3_n32_20261101__rerun_ar_20261103", None),
    ("P014", "info_contract_aesgcm_20261102__rerun_ar_20261103", None),
    ("P016-6.1sol", "info_contract_aesgcm_labels_gpt_6_1_sol__rerun_ar_20261103", None),
    ("P017", "info_contract_aesgcm_p017_20261102__rerun_ar_20261103", None),
    # P018: the transport-repair rerun of this cohort is LABEL-SPLIT at the
    # recorded boundary (12 instances re-run on the registered label, 12
    # completed on the author-directed substitute after the registered label's
    # quota exhaustion). The family member reads the registered label's own
    # complete 24-instance first pass (22 evaluable pairs); the rerun's two
    # label halves (12/0 and 12/0, p=4.9e-4 each) are disclosed per label in
    # S30 and Section 5 -- no blended number enters the family.
    ("P018", "info_contract_aesgcm_random_20261102", None),
    ("P019", "info_contract_chachapoly_random_20261102__rerun_ar_20261103", None),
    ("P021AR", "info_contract_aesgcm_random_p021ar_20261103", None),
    ("P022a", "info_contract_aesgcm_p022a_20261102__rerun_ar_20261103", None),
    ("P023", "info_contract_aesgcm_random_p023_20261103", None),
    ("P024a", "info_contract_aesgcm_p024a_20261103", None),
    # P024b removed from the family by author ruling (2026-11-04): its
    # completed registration holds a single evaluable pair (1/0, p=1.0,
    # 46/48 floor-exhausted) -- a degenerate read produced by
    # infrastructure collapse, not a replication measurement. It is
    # reported as a boundary condition in Section 5 (both codings,
    # printed in full); the family keeps only registrations whose
    # evaluable-pairs statistic is informative.
]
# P016-5.6sol and P022b contribute NO C1-vs-C4 members (their C4 arms are
# fully floor-exhausted at every floor tried, so under the registered
# evaluable-pairs rule they hold no discordant pairs); P024b's rerun holds
# one evaluable pair (1/0) and IS a member.
# Their label-split evidence lives in PAPER_EVIDENCE_20261103.json under the
# budget-bound coding, reported per cohort in S30.
RERUN_MEMBERS = {"P010L2", "P011-L3-N32", "P014", "P016-6.1sol",
                 "P017", "P018", "P019", "P021AR", "P022a"}


def paired(directory: Path) -> tuple[int, int, int]:
    """Return (discordant C1-only, discordant C4-only, evaluable pairs)."""
    best = {}
    for line in (directory / "results.jsonl").read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            best.setdefault((rec["seed"], rec["cell"]), rec)
    verdict = {}
    for (seed, cell), rec in best.items():
        if rec["status"] in TERM:
            verdict[(seed, cell)] = None
        else:
            verdict[(seed, cell)] = 1 if rec.get("oracle_verdict") == "accepted" else 0
    seeds = {s for (s, _) in best}
    b10 = b01 = pairs = 0
    for s in seeds:
        a, c = verdict.get((s, "C1")), verdict.get((s, "C4"))
        if isinstance(a, int) and isinstance(c, int):
            pairs += 1
            b10 += a == 1 and c == 0
            b01 += a == 0 and c == 1
    return b10, b01, pairs


def holm(ps: list[float]) -> list[float]:
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m
    run = 0.0
    for rank, i in enumerate(order, start=1):
        run = max(run, (m - rank + 1) * ps[i])
        adj[i] = min(1.0, run)
    return adj


def sig(x: float, n: int = 3) -> str:
    """n significant figures, ROUND_HALF_UP, decimal if |x| >= 1e-3."""
    if x == 0:
        return "0"
    d = Decimal(repr(x))
    e = d.adjusted()
    r = d.quantize(Decimal(1).scaleb(e - n + 1), rounding=ROUND_HALF_UP)
    if abs(r) >= Decimal("0.001"):
        return f"{r:.{max(0, n - 1 - e)}f}".rstrip("0").rstrip(".")
    e = r.adjusted()
    mant = r.scaleb(-e)
    return f"{mant:.{n - 1}f}\\times10^{{{e}}}"


def cp_lower(n: int, places: int = 2) -> str:
    """Two-sided 95% exact lower bound for n/n; 0.025**(1/n)."""
    v = 0.025 ** (1.0 / n)
    return str(Decimal(repr(v)).quantize(Decimal(1).scaleb(-places),
                                         rounding=ROUND_HALF_UP))


# The column printed in the revision before the AEAD wave closed, over the 14
# members that existed then, in rank order. Reproducing its *values* proves the
# recount moved only because the family grew. Its *presentation* does not
# reproduce: 6.9e-3 is two significant figures while 0.0117 next to it is
# three, and 0.03125 is printed one unit below nearest 3-figure rounding.
# That mixed precision is exactly why the column could not be regenerated as a
# string under a single rule, and why it is being regenerated now.
PUBLISHED_M14 = [4.2e-7, 1.6e-6, 5.8e-6, 4.2e-5, 1.5e-4, 2.8e-4, 2.8e-4,
                 6.9e-3, 0.0117, 0.0117, 0.031, 0.031, 0.031, 0.0625]
# the pre-wave registrations, for the historical m=14 reproduction check
LEGACY_ROSTER = [
    ("P010P", "info_contract_powered_20261025", None),
    ("P010N16", "info_contract_n16_20261026", None),
    ("P010X1", "info_contract_x1_gptoss_20261026", None),
    ("P010L2", "info_contract_label2_20261025", None),
    ("P010L3", "info_contract_label3_20261029", None),
    ("P013", "info_contract_aesctr_20261026", None),
    ("P011-L3-N32", "info_contract_label3_n32_20261101", None),
    ("P014", "info_contract_aesgcm_20261102", None),
    ("P016", "info_contract_aesgcm_labels_20261102", "gpt_6_1_sol"),
    ("P017", "info_contract_aesgcm_p017_20261102", None),
    ("P018", "info_contract_aesgcm_random_20261102", None),
    ("P019", "info_contract_chachapoly_random_20261102", None),
    ("P021", "info_contract_aesgcm_random_p021_20261102", None),
    ("P022a", "info_contract_aesgcm_p022a_20261102", None),
]
LEGACY_NEW = {"P023", "P024a", "P024b"}


def verify_m14(rows):
    """Recompute the pre-wave family from the pre-wave registrations and
    compare values, not formatting."""
    legacy = []
    for name, d, arm in LEGACY_ROSTER:
        b10, b01, pairs = paired(HERE / d / arm if arm else HERE / d)
        n = b10 + b01
        legacy.append({"cohort": name, "discordant_c1_only": b10,
                       "discordant_c4_only": b01, "evaluable_pairs": pairs,
                       "discordant_pairs": n,
                       "p_two_sided": 1.0 if n == 0 else min(1.0, 2.0 ** (1 - n))})
    sub = [r for r in legacy if r["cohort"] not in LEGACY_NEW]
    assert len(sub) == 14, len(sub)
    adj = sorted(holm([r["p_two_sided"] for r in sub]))
    bad = [(a, b) for a, b in zip(adj, PUBLISHED_M14)
           if abs(a - b) / b > 0.035]          # published carries 2 s.f.
    ok = not bad
    print(f"m=14 value reproduction: "
          f"{'all 14 AGREE within published precision' if ok else 'MISMATCH'}")
    for a, b in bad:
        print(f"  recomputed {a:.4g} vs published {b:.4g}")
    return ok


def main(argv):
    rows = []
    for name, d, arm in ROSTER:
        b10, b01, pairs = paired(HERE / d / arm if arm else HERE / d)
        if b01:
            raise SystemExit(f"{name}: non-zero C4-direction discordance; "
                             "this script assumes the one-directional case")
        n = b10 + b01          # the exact test conditions on discordant pairs
        p = 1.0 if n == 0 else min(1.0, 2.0 ** (1 - n))
        rows.append({"cohort": name, "discordant_c1_only": b10,
                     "discordant_c4_only": b01, "evaluable_pairs": pairs,
                     "discordant_pairs": n, "p_two_sided": p})

    adj = holm([r["p_two_sided"] for r in rows])
    for r, a in zip(rows, adj):
        r["holm_adjusted"] = a

    p_set = "{" + ", ".join(sig(r["p_two_sided"]) for r in
                            sorted(rows, key=lambda r: r["p_two_sided"])) + "}"
    a_set = "{" + ", ".join(sig(r["holm_adjusted"]) for r in
                            sorted(rows, key=lambda r: r["p_two_sided"])) + "}"
    cp_set = ", ".join(f"${r['discordant_c1_only']}/0$ at $\\ge{cp_lower(r['discordant_pairs'])}$"
                       for r in sorted(rows, key=lambda r: r["discordant_pairs"],
                                       reverse=True))

    print(f"family size m = {len(rows)}")
    for r in sorted(rows, key=lambda r: r["p_two_sided"]):
        print(f"  {r['cohort']:12s} {r['discordant_c1_only']:2d}/0 of "
              f"{r['discordant_pairs']:2d} discordant "
              f"({r['evaluable_pairs']:2d} pairs)  p={r['p_two_sided']:.6g}  "
              f"holm={r['holm_adjusted']:.6g}")
    if not verify_m14(rows):
        raise SystemExit("pre-wave values do not reproduce; recount is unsound")

    print()
    print("UNadjusted set :", p_set)
    print("Holm adjusted  :", a_set)
    print("Clopper-Pearson:", cp_set)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "family": "info-contract paired C1-vs-C4 exact tests",
        "members": rows,
        "m": len(rows),
        "conventions": {
            "p": "exact two-sided binomial; p = min(1, 2**(1-n)) with zero "
                 "C4-direction discordant pairs",
            "holm": "step-down, adjusted_i = min(1, max_{j<=i} (m-j+1)*p_j)",
            "rounding": "3 significant figures, ROUND_HALF_UP, decimal for "
                        "|x| >= 1e-3",
            "clopper_pearson": "two-sided 95% exact lower bound, 2 dp, "
                               "ROUND_HALF_UP",
        },
        "latex": {"p_set": p_set, "holm_set": a_set, "cp_set": cp_set},
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {OUT.relative_to(HERE.parents[1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
