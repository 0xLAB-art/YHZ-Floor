#!/usr/bin/env python3
"""
fleiss_kappa.py — E6 inter-annotator agreement (the W5 fill's κ half).

Fills the agreement statistics behind the paper's six [PENDING-W5] marks:
  - annotators-vs-annotators Fleiss' κ over the 30-item packet,
  - each annotator vs the frozen classifier (percent agreement + κ where
    the classifier's labels are treated as one fixed rater — pairwise
    Cohen-style via the same Fleiss machinery on the 2-rater subset),
  - per-category κ (the eight-status taxonomy) with the small-sample caveat
    printed, never smoothed over.

Fleiss' κ over the frozen definition ( Fleiss 1971 [fleiss]):
  P_i = (1/(n(n-1))) (Σ_j n_ij^2 − n)   per item
  P̄  = (1/N) Σ P_i
  p̄_j = (1/(N n)) Σ_i n_ij
  κ  = (P̄ − Σ_j p̄_j^2) / (1 − Σ_j p̄_j^2)

Input format (one JSON): {"items": [{"id": ..., "annotations": [s1, s2, s3],
"classifier": s}] , "categories": [...]}  — the round-1 packet layout the
annotators/CODEBOOK.md protocol already implies; a validator check warns if
any item's annotation count != the declared rater count.

USAGE:
    python3 sp2027/analysis/fleiss_kappa.py sp2027/annotators/round1.json
Exit: 0 emitted; 2 missing input.

Interpretation guardrails printed with the numbers (never inserted into the
paper by this tool): κ is chance-corrected and meaningless when one category
dominates; the paper reports κ beside raw percent agreement and the
confusion pattern, per the frozen text.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def fleiss_kappa(mat: list[list[int]], n_raters: int) -> dict:
    """mat[i][j] = #raters assigning item i to category j."""
    N = len(mat)
    if N == 0 or n_raters < 2:
        return {"kappa": None, "P_bar": None, "p_bar": None,
                "detail": "need >= 1 item and >= 2 raters"}
    total = n_raters * N
    cat_sums = [sum(row[j] for row in mat) for j in range(len(mat[0]))]
    p_bar_j = [s / total for s in cat_sums]
    P_exp = sum(p * p for p in p_bar_j)
    P_obs = sum((sum(x * x for x in row) - n_raters)
                / (n_raters * (n_raters - 1)) for row in mat) / N
    if P_exp == 1.0:
        return {"kappa": None, "P_bar": P_obs, "p_bar": p_bar_j,
                "detail": "single-category data — κ undefined (chance = 1)"}
    k = (P_obs - P_exp) / (1 - P_exp)
    return {"kappa": k, "P_bar": P_obs, "P_expected": P_exp,
            "p_bar": p_bar_j, "n_items": N, "n_raters": n_raters}


def percent_agreement(mat: list[list[int]], n_raters: int) -> float:
    N = len(mat)
    agree = sum(1 for row in mat
                if max(row) == n_raters)          # unanimous items
    return agree / N if N else 0.0


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    data = json.loads(Path(sys.argv[1]).read_text())
    items = data["items"]
    n_raters = data.get("n_raters") or (
        max(len(it["annotations"]) for it in items) if items else 0)
    cats = data.get("categories") or sorted(
        {a for it in items for a in it["annotations"]}
        | {it.get("classifier") for it in items if it.get("classifier")})
    cat_ix = {c: j for j, c in enumerate(cats)}

    bad = [it["id"] for it in items if len(it["annotations"]) != n_raters]
    if bad:
        print(f"WARN: {len(bad)} items with != {n_raters} annotations: {bad[:5]}")

    mat = [[it["annotations"].count(c) for c in cats] for it in items]
    full = fleiss_kappa(mat, n_raters)
    pa = percent_agreement(mat, n_raters)
    print("=== Fleiss' κ — annotators vs annotators ===")
    print(f"items={full.get('n_items')} raters={n_raters} "
          f"categories={len(cats)}  κ={full['kappa']:.3f}  "
          f"unanimous-agreement={pa:.1%}" if full.get("kappa") is not None
          else f"κ undefined: {full.get('detail')}")

    # per-annotator vs the frozen classifier (2-rater Fleiss machinery)
    print("\n=== each annotator vs the frozen classifier ===")
    cls_rows = []
    for r in range(n_raters):
        sub = []
        for it in items:
            if it.get("classifier") is None:
                continue
            a = it["annotations"][r]
            sub.append(([a.count(c) for c in cats]) and
                       [ (1 if x == a else 0) + (1 if x == it["classifier"] else 0)
                         for x in cats ])
        if sub:
            k2 = fleiss_kappa(sub, 2)
            agree = sum(1 for it in items
                        if it.get("classifier") is not None
                        and it["annotations"][r] == it["classifier"])
            n = sum(1 for it in items if it.get("classifier") is not None)
            print(f"  annotator-{r+1}: agreement {agree}/{n} = {agree/n:.1%}"
                  + (f"  κ={k2['kappa']:.3f}" if k2.get("kappa") is not None
                     else f"  κ undefined ({k2.get('detail')})"))
        else:
            print(f"  annotator-{r+1}: no classifier labels present")

    print("\n=== per-category κ (one-vs-rest binarization) ===")
    for c in cats:
        bin_mat = [[row[cat_ix[c]], n_raters - row[cat_ix[c]]] for row in mat]
        kc = fleiss_kappa(bin_mat, n_raters)
        marg = sum(row[cat_ix[c]] for row in mat) / (n_raters * len(mat))
        s = f"κ={kc['kappa']:.3f}" if kc.get("kappa") is not None else "κ undefined"
        print(f"  {c:22s} {s}  (marginal {marg:.1%})"
              + ("  [rare category — κ unstable, report with raw agreement]"
                 if 0.05 < marg <= 0.15 or 0.85 <= marg < 0.95 else "")
              + ("  [very rare — κ meaningless here]" if marg <= 0.05 or marg >= 0.95 else ""))

    print("\nGuardrails: κ is chance-corrected; report beside raw percent "
          "agreement and the confusion pattern (frozen text).")
    out = Path(sys.argv[1]).with_suffix(".kappa.json")
    out.write_text(json.dumps(
        {"source": sys.argv[1], "overall": full,
         "unanimous_agreement": pa, "categories": cats}, indent=2) + "\n")
    print(f"evidence: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
