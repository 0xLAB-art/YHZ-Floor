#!/usr/bin/env python3
"""Audit Table tab:scale-inventory (Section 1) against the retained artifacts.

Each family is measured twice --- as results.jsonl ROW counts and as unique
seed x cell SLOTS --- because the printed table mixed the two: the
information-contract row carried slots (2,112) while the scale-up row carried
rows (129, one flagged duplicate included). A column must not switch unit
silently, so both are reported and the manuscript prints rows.

Run: python3 sp2027/research_execution/audit_scale_inventory.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTRO = (ROOT / "sp2027/paper/capability_revision_20261020/"
         "arxiv_version_evidence_revision_20261022/appendix_shared.tex")
OUT = ROOT / "sp2027/analysis/SCALE_INVENTORY.json"

# The 24 cohorts of Appendix D.1, excluding the separately-listed P011-L3-N32
# scale-up. P016 is one registered cohort with two arms, counted once.
INFO = [
    ("P010", "info_contract_2x2_20261018"),
    ("P011", "info_contract_2x2_rc4_20261024"),
    ("P010P", "info_contract_powered_20261025"),
    ("P010N16", "info_contract_n16_20261026"),
    ("P010L2", "info_contract_label2_20261025"),
    ("P010L3", "info_contract_label3_20261029"),
    ("P010L4", "info_contract_label4_20261030"),
    ("P010X1", "info_contract_x1_gptoss_20261026"),
    ("P012", "info_contract_ecdsa_20261026"),
    ("P013", "info_contract_aesctr_20261026"),
    ("P010L5", "info_contract_label5_20261030"),
    ("P010L5R", "info_contract_label5r_20261030"),
    ("P014", "info_contract_aesgcm_20261102"),
    ("P016", "info_contract_aesgcm_labels_20261102"),
    ("P017", "info_contract_aesgcm_p017_20261102"),
    ("P018", "info_contract_aesgcm_random_20261102"),
    ("P019", "info_contract_chachapoly_random_20261102"),
    ("P020", "info_contract_gcmsiv_random_20261102"),
    ("P021", "info_contract_aesgcm_random_p021_20261102"),
    ("P022a", "info_contract_aesgcm_p022a_20261102"),
    ("P022b", "info_contract_aesgcm_p022b_20261102"),
    ("P023", "info_contract_aesgcm_random_p023_20261103"),
    ("P024a", "info_contract_aesgcm_p024a_20261103"),
    ("P024b", "info_contract_aesgcm_p024b_20261103"),
]

FAMILIES = [
    ("Admission counterfactual (L3)", 1, []),
    ("Information contract (premise/slot)", len(INFO), [d for _, d in INFO]),
    ("Info-contract scale-up P011-L3-N32", 1, ["info_contract_label3_n32_20261101"]),
    ("Wrapper / agency (H2)", 3, ["h2_pairs_extension_20261024",
                                  "h2_cbc_agency_20261023",
                                  "h2_pairs_powered_20261107"]),
    ("External boundary", 4, ["external_admission_20261024",
                              "external_admission_amend1_20261024",
                              "external_admission_amend3_20261105",
                              "external_admission_amend4_frontier_20261106"]),
]


def measure(dirs):
    rows = slots = 0
    for d in dirs:
        for f in sorted((HERE / d).rglob("results.jsonl")):
            if "readjudication" in f.parts:
                # post-hoc re-adjudication rows re-read recorded sessions
                # (each carries a registered_run_id back-pointer into the
                # extension cohort); they are not cohort sessions.
                continue
            recs = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
            rows += len(recs)
            slots += len({(r.get("seed"), r.get("cell")) for r in recs})
    return rows, slots


def main():
    # H1-R3 is a campaign record, not a results.jsonl cohort: its session total
    # is the retained DERIVED.json value (801+20+28+2+1 = 852).
    adm = json.loads(
        (ROOT / "sp2027/analysis/h1r3_20261019/DERIVED.json").read_text())["sessions"]

    printed = {}
    for m in re.finditer(
            r"(?m)^([A-Z][^&]*?)\s*&\s*(\d+)\s*&\s*([\d,]+)\s*&", INTRO.read_text()):
        printed[re.sub(r"\s+", " ", m.group(1)).strip()] = int(
            m.group(3).replace(",", ""))

    table = []
    for name, cohorts, dirs in FAMILIES:
        rows, slots = (adm, adm) if not dirs else measure(dirs)
        table.append({"family": name, "cohorts": cohorts, "rows": rows,
                      "slots": slots, "printed": printed.get(name)})

    total_rows = sum(r["rows"] for r in table)
    total_slots = sum(r["slots"] for r in table)

    print(f"{'family':38s} {'coh':>4s} {'rows':>6s} {'slots':>6s} {'printed':>8s}")
    for r in table:
        print(f"{r['family']:38s} {r['cohorts']:4d} {r['rows']:6d} "
              f"{r['slots']:6d} {str(r['printed']):>8s}")
    print(f"{'TOTAL':38s} {sum(r['cohorts'] for r in table):4d} {total_rows:6d} "
          f"{total_slots:6d} {str(printed.get('Total')):>8s}")

    drift = [{"family": r["family"], "printed": r["printed"], "rows": r["rows"],
              "delta": r["rows"] - r["printed"]}
             for r in table if r["printed"] != r["rows"]]
    print("\nrow-count drift vs the printed table:")
    for d in drift:
        print(f"  {d['family']}: printed {d['printed']}, rows {d['rows']} "
              f"({d['delta']:+d})")
    print(f"total: printed {printed.get('Total')}, rows {total_rows} "
          f"({total_rows - printed.get('Total', 0):+d}), slots {total_slots}")

    OUT.write_text(json.dumps({
        "families": table,
        "total_rows": total_rows,
        "total_slots": total_slots,
        "printed_total": printed.get("Total"),
        "drift": drift,
        "rule": "the printed session column must be results.jsonl row counts; "
                "slot counts are recorded here because the information-contract "
                "row printed slots (7 flagged duplicates excluded) beside a "
                "scale-up row printed as rows (1 duplicate included)",
    }, indent=2) + "\n")
    print(f"\nwrote {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
