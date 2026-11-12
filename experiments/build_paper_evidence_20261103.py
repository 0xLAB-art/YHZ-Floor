#!/usr/bin/env python3
"""Single source of truth for the paper's rerun-wave evidence.

Turns the three reporting caveats into structure:

  1. LABEL PURITY   — every (seed, cell) judgment is attributed to its label
     group (primary vs author-directed substitute) using the boundary recorded
     in each cohort's RECOVERY_LABEL_SUBSTITUTION.md. Acceptance rates and
     paired tests are computed PER GROUP; nothing mixes them.
  2. OUTCOME TAXONOMY — accepted / text-failed / FLOOR_EXHAUSTED / transport
     are distinct outcomes. FLOOR_EXHAUSTED (HTTP 200, output_tokens == floor,
     stop_reason "length", empty text block) is a measurement-layer event: it
     is never counted as acceptance evidence and never as transport loss.
  3. PROVENANCE     — paper-facing numbers come from THIS artifact only:
     it dedupes (seed, cell) judgments (a pair counts accepted iff ANY of its
     judgments succeeded), computes the paired exact tests per label group,
     and emits JSON + markdown + ready-to-paste tex snippets.

Idempotent: rerun any time; the freeze step is "numbers stopped changing".
Writes: PAPER_EVIDENCE_20261103.json, PAPER_EVIDENCE_20261103.md,
paper_tables_20261103/*.tex
"""
import json, math, re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "PAPER_EVIDENCE_20261103.json"
OUT_MD = HERE / "PAPER_EVIDENCE_20261103.md"
TEX_DIR = HERE / "paper_tables_20261103"
BEARING = {"C1", "C3"}
WITHHELD = {"C2", "C4"}
CELLS = ["C1", "C2", "C3", "C4"]
BAD = {"HTTP_ERROR", "MALFORMED_PROVIDER_JSON", "NO_SUBMISSION", "TIMEOUT",
       "INCOMPLETE_RESPONSE", "PROVIDER_UNAVAILABLE"}

PAIRS = [  # (rerun namespace, original namespace, fixture, label, floor)
    ("info_contract_aesgcm_random_p021ar_20261103", "info_contract_aesgcm_random_p021_20261102", "AES-GCM", "gpt-6-astra", 4200),
    ("info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103", "info_contract_aesgcm_random_p023_20261103", "AES-GCM", "gpt-6-astra", 4200),
    ("info_contract_aesgcm_20261102__rerun_ar_20261103", "info_contract_aesgcm_20261102", "AES-GCM", "gpt-6-astra", 2800),
    ("info_contract_aesgcm_random_20261102__rerun_ar_20261103", "info_contract_aesgcm_random_20261102", "AES-GCM", "gpt-6-astra", 4200),
    ("info_contract_aesgcm_p017_20261102__rerun_ar_20261103", "info_contract_aesgcm_p017_20261102", "AES-GCM", "gpt-6-astra", 4200),
    ("info_contract_aesgcm_p022a_20261102__rerun_ar_20261103", "info_contract_aesgcm_p022a_20261102", "AES-GCM", "gpt-6.1-sol", 4200),
    ("info_contract_aesgcm_p022b_20261102__rerun_ar_20261103", "info_contract_aesgcm_p022b_20261102", "AES-GCM", "gpt-5.6-sol", 4200),
    ("info_contract_aesgcm_p024b_20261103__rerun_ar_20261103", "info_contract_aesgcm_p024b_20261103", "AES-GCM", "gpt-5.6-sol", 8400),
    ("info_contract_chachapoly_random_20261102__rerun_ar_20261103", "info_contract_chachapoly_random_20261102", "ChaCha20-Poly1305", "gpt-6-astra", 4200),
    ("info_contract_gcmsiv_random_20261102__rerun_ar_20261103", "info_contract_gcmsiv_random_20261102", "AES-GCM-SIV", "gpt-6-astra", 4200),
    ("info_contract_label2_20261025__rerun_ar_20261103", "info_contract_label2_20261025", "ChaCha20", "gpt-6.1-sol", 2800),
    ("info_contract_label3_n32_20261101__rerun_ar_20261103", "info_contract_label3_n32_20261101", "ChaCha20", "gpt-6.1-sol", 2800),
    ("info_contract_label4_20261030__rerun_ar_20261103", "info_contract_label4_20261030", "ChaCha20", "gpt-5.6-sol", 2800),
    ("info_contract_aesgcm_labels_gpt_6_1_sol__rerun_ar_20261103", "info_contract_aesgcm_labels_20261102/gpt_6_1_sol", "AES-GCM", "gpt-6.1-sol", 2800),
    ("info_contract_aesgcm_labels_gpt_5_6_sol__rerun_ar_20261103", "info_contract_aesgcm_labels_20261102/gpt_5_6_sol", "AES-GCM", "gpt-5.6-sol", 2800),
]

def load_rows(ns: Path):
    rows = []
    for rp in [ns / "results.jsonl"] + sorted(ns.glob("shard_*/results.jsonl")):
        if rp.exists():
            rows += [json.loads(l) for l in rp.read_text().splitlines() if l.strip()]
    return rows

def label_boundary(ns: Path):
    """Rows after this 0-based index belong to the substitute label."""
    note = ns / "RECOVERY_LABEL_SUBSTITUTION.md"
    if not note.exists():
        return None
    m = re.search(r"Rows 1\.\.(\d+) of results\.jsonl are primary", note.read_text())
    return int(m.group(1)) if m else None

def pair_outcome(judgments):
    """Any-SUCCESS-wins merge of a pair's judgments -> one outcome."""
    statuses = [j.get("status", "?") for j in judgments]
    if "SUCCESS" in statuses:
        return "accepted"
    non_transport = [s for s in statuses if s not in BAD]
    last = judgments[-1].get("status", "?")
    if non_transport:
        # keep the most informative non-transport judgment
        for j in reversed(judgments):
            if j.get("status") not in BAD:
                last = j.get("status", "?")
                break
    if last == "ORACLE_FAIL":
        return "text_fail"
    if last == "EMPTY_RESPONSE":
        return "floor_exhausted"
    return "transport"

def paired_exact_p(discordant_one_way: int, discordant_other_way: int):
    """Two-sided exact binomial (McNemar) on discordant pairs."""
    n = discordant_one_way + discordant_other_way
    if n == 0:
        return None, 0
    k = min(discordant_one_way, discordant_other_way)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * p), n

def analyze_pair(rerun_ns, orig_ns, fixture, label, floor):
    rerun_path = HERE / rerun_ns
    orig_path = HERE / orig_ns
    rows = load_rows(rerun_path)
    boundary = label_boundary(rerun_path)
    # dedup + label attribution: a pair's group = the group of its LAST
    # primary judgment, unless the pair only has substitute judgments
    by_pair = {}
    last_idx = {}
    for i, r in enumerate(rows):
        key = (r.get("seed"), r.get("cell"))
        by_pair.setdefault(key, []).append(r)
        last_idx[key] = i
    groups = {"primary": defaultdict(list), "substitute": defaultdict(list)}
    for key, judgments in by_pair.items():
        # the pair's group is decided by its LAST judgment's position: a pair
        # re-judged inside the substitute-label recovery pass belongs to the
        # substitute group even if an earlier primary-label judgment exists
        idx = last_idx[key]
        g = "substitute" if (boundary is not None and idx >= boundary) else "primary"
        groups[g][key].extend(judgments)

    out = {"rerun": rerun_ns, "original": orig_ns, "fixture": fixture,
           "label": label, "token_floor": floor,
           "label_boundary_row": boundary, "rows_raw": len(rows),
           "pairs_total": len(by_pair), "groups": {}}
    for g, pairs in groups.items():
        cells = {c: Counter() for c in CELLS}
        seeds_cells = defaultdict(dict)  # seed -> cell -> outcome
        for (seed, cell), judgments in pairs.items():
            oc = pair_outcome(judgments)
            c = cell if cell in CELLS else "?"
            cells[c][oc] += 1
            cells[c]["sessions"] += 1
            seeds_cells[seed][cell] = oc
        acc = sum(cells[c]["accepted"] for c in CELLS)
        grp = {"sessions": sum(cells[c]["sessions"] for c in CELLS),
               "accepted": acc,
               "per_cell": {c: {k: v for k, v in cells[c].items()} for c in cells},
               }
        # paired C1-vs-C2 (stated vs withheld, both oracle-bearing)
        d_one = d_other = 0
        for seed, sc in seeds_cells.items():
            a, w = sc.get("C1"), sc.get("C2")
            if a and w:
                if a == "accepted" and w != "accepted":
                    d_one += 1
                elif w == "accepted" and a != "accepted":
                    d_other += 1
        p, n = paired_exact_p(d_one, d_other)
        grp["paired_C1_vs_C2"] = {"discordant_stated_wins": d_one,
                                  "discordant_withheld_wins": d_other,
                                  "n_discordant": n,
                                  "exact_two_sided_p": p}
        # paired C1-vs-C4 under the REGISTERED evaluable-pairs rule: a pair
        # counts iff both cells ended accepted or text_fail; floor-exhausted
        # and transport sessions are terminal outcomes outside the statistic
        e_one = e_other = e_pairs = 0
        for seed, sc in seeds_cells.items():
            a, w = sc.get("C1"), sc.get("C4")
            ev = lambda o: o in ("accepted", "text_fail")
            if a and w and ev(a) and ev(w):
                e_pairs += 1
                if a == "accepted" and w != "accepted":
                    e_one += 1
                elif w == "accepted" and a != "accepted":
                    e_other += 1
        ep, en = paired_exact_p(e_one, e_other)
        grp["paired_C1_vs_C4"] = {"discordant_stated_wins": e_one,
                                  "discordant_withheld_wins": e_other,
                                  "evaluable_pairs": e_pairs,
                                  "exact_two_sided_p": ep}
        # premise marginals (accepted/evaluable), floor-exhausted and transport
        # kept beside them as the separate terminal outcomes they are
        marg = {}
        for side_name, side_cells in (("stated", ("C1", "C3")),
                                      ("withheld", ("C2", "C4"))):
            acc = ev = fe = tx = 0
            for sc in seeds_cells.values():
                for cell, oc in sc.items():
                    if cell not in side_cells:
                        continue
                    acc += oc == "accepted"
                    ev += oc in ("accepted", "text_fail")
                    fe += oc == "floor_exhausted"
                    tx += oc == "transport"
            marg[side_name] = {"accepted": acc, "evaluable": ev,
                               "floor_exhausted": fe, "transport": tx}
        grp["marginals"] = marg
        out["groups"][g] = grp
    # original tally (accepted only; originals may use older row vocabularies)
    if orig_path.exists():
        orows = load_rows(orig_path)
        ob = {}
        for r in orows:
            ob.setdefault((r.get("seed"), r.get("cell")), []).append(r)
        oacc = sum(1 for v in ob.values() if any(j.get("status") == "SUCCESS" for j in v))
        out["original"] = {"rows_raw": len(orows), "pairs": len(ob), "accepted_any": oacc}
    return out

def deliberation_gradient(ns="info_contract_aesgcm_random_p021ar_20261103"):
    """Per-cell turn-1 output tokens for text-bearing responses (measurement layer)."""
    import statistics
    D = HERE / ns / "raw_provider_responses"
    stats = defaultdict(list)
    if not D.exists():
        return {}
    for f in D.glob("*_turn1.json"):
        m = re.search(r"__(C\d)__seed_", f.name)
        if not m:
            continue
        try:
            b = json.loads(f.read_text())
        except Exception:
            continue
        out = (b.get("usage") or {}).get("output_tokens")
        if out:
            stats[m.group(1)].append(out)
    return {c: {"n": len(v), "median": statistics.median(v),
                "min": min(v), "max": max(v)} for c, v in stats.items()}

def main():
    cohorts = [analyze_pair(*p) for p in PAIRS]
    p026_rows = load_rows(HERE / "info_contract_aesgcm_c2_floor8000_p026_20261103")
    p026b = {}
    for r in p026_rows:
        p026b.setdefault((r.get("seed"), r.get("cell")), []).append(r)
    p026_out = Counter(pair_outcome(v) for v in p026b.values())
    p026 = {"sessions": sum(p026_out.values()), "outcomes": dict(p026_out),
            "note": ("floor-sensitivity cohort (registered P026): C2 only, floor 8000, "
                     "same 96 seeds as P021AR — validates the floor-exhaustion "
                     "mechanism; measurement layer, not acceptance evidence")}
    gradient = deliberation_gradient()
    payload = {"generated": "2026-11-03 (idempotent; rerun at freeze)",
               "rules": {
                   "dedup": "a (seed, cell) pair counts accepted iff ANY judgment succeeded",
                   "labels": "primary vs author-directed substitute, split at the recorded boundary; never mixed",
                   "floor_exhausted": "measurement layer: HTTP 200 + output_tokens == floor + stop_reason length + empty text; not acceptance evidence, not transport loss",
               },
               "cohorts": cohorts, "p026": p026,
               "deliberation_gradient_p021ar": gradient}
    OUT_JSON.write_text(json.dumps(payload, indent=1))

    # markdown report
    lines = ["# Paper evidence — rerun wave (single source of truth)", ""]
    for c in cohorts:
        lines.append(f"## {c['rerun'].replace('__rerun_ar_20261103','').replace('info_contract_','')} "
                     f"[{c['fixture']}, {c['label']}, floor {c['token_floor']}]")
        for g, grp in sorted(c["groups"].items(), key=lambda kv: (kv[0] != "primary", -kv[1]["sessions"])):
            if g != "primary" and grp["sessions"] == 0:
                continue  # no substitute rows for this cohort yet
            tag = "primary label" if g == "primary" else "SUBSTITUTE label (disclosed)"
            pr = grp["paired_C1_vs_C2"]
            ptxt = f"{pr['exact_two_sided_p']:.2e}" if pr["exact_two_sided_p"] is not None else "n/a"
            lines.append(f"- **{tag}**: {grp['sessions']} sessions, accepted {grp['accepted']}"
                         f" | paired C1-vs-C2: {pr['discordant_stated_wins']}/{pr['n_discordant']} one-way, p={ptxt}")
            for cell in CELLS:
                pc = grp["per_cell"].get(cell, {})
                lines.append(f"    - {cell}: acc {pc.get('accepted',0)} / tx-fail {pc.get('text_fail',0)}"
                             f" / FLOOR_EXH {pc.get('floor_exhausted',0)} / transport {pc.get('transport',0)}"
                             f" ({pc.get('sessions',0)} sessions)")
        if "original" in c:
            lines.append(f"- original: {c['original']['pairs']} pairs, accepted(any-judgment) {c['original']['accepted_any']}")
        lines.append("")
    lines.append(f"## P026 floor-sensitivity (measurement layer): {p026['sessions']} sessions — {p026['outcomes']}")
    lines.append(f"## Deliberation gradient (P021AR turn-1 output tokens): "
                 + ", ".join(f"{c}: med {v['median']:.0f} (n={v['n']})" for c, v in sorted(gradient.items())))
    OUT_MD.write_text("\n".join(lines) + "\n")

    # tex snippets
    TEX_DIR.mkdir(exist_ok=True)
    tex = ["% GENERATED by build_paper_evidence_20261103.py — do not hand-edit",
           "% Per-cohort rerun outcomes, label groups kept separate", ""]
    for c in cohorts:
        g = c["groups"].get("primary", {})
        if not g:
            continue
        pr = g["paired_C1_vs_C2"]
        tex.append(f"% {c['rerun']}")
        for cell in CELLS:
            pc = g["per_cell"].get(cell, {})
            tex.append(f"%   {cell}: accepted {pc.get('accepted',0)}/{pc.get('sessions',0)}"
                       f"  floor-exhausted {pc.get('floor_exhausted',0)}"
                       f"  transport {pc.get('transport',0)}")
        if pr["n_discordant"]:
            tex.append(f"%   paired C1-vs-C2: {pr['discordant_stated_wins']}/{pr['n_discordant']}"
                       f" two-sided p={pr['exact_two_sided_p']:.2e}")
        tex.append("")
    (TEX_DIR / "rerun_outcomes.tex").write_text("\n".join(tex) + "\n")

    # modern-AEAD table values: the registered-rule (evaluable-pairs C1-vs-C4)
    # statistic and the premise marginals, per label group — the numbers the
    # main-text table and prose print, generated, never hand-derived
    vals = ["% GENERATED by build_paper_evidence_20261103.py — do not hand-edit",
            "% Registered rule: paired C1-vs-C4 over evaluable pairs",
            "% (accepted|text_fail both sides); floor-exhausted/transport reported beside.",
            "% Table formatting (2 s.f. p, row labels) happens in the tex; these are the values.", ""]
    for c in cohorts:
        for gname in ("primary", "substitute"):
            g = c["groups"].get(gname)
            if not g or g["sessions"] == 0:
                continue
            pr4 = g["paired_C1_vs_C4"]
            p4 = pr4["exact_two_sided_p"]
            p4txt = f"{p4:.2e}" if p4 is not None else "n/a"
            m = g["marginals"]
            pr2 = g["paired_C1_vs_C2"]
            p2 = pr2["exact_two_sided_p"]
            p2txt = f"{p2:.2e}" if p2 is not None else "n/a"
            vals.append(f"% {c['rerun']} [{gname}]")
            vals.append(f"%   paired C1-vs-C4: {pr4['discordant_stated_wins']}/{pr4['discordant_withheld_wins']}"
                        f" over {pr4['evaluable_pairs']} evaluable  p={p4txt}")
            vals.append(f"%   stated {m['stated']['accepted']}/{m['stated']['evaluable']}"
                        f" (fe {m['stated']['floor_exhausted']}, tx {m['stated']['transport']})"
                        f"  withheld {m['withheld']['accepted']}/{m['withheld']['evaluable']}"
                        f" (fe {m['withheld']['floor_exhausted']}, tx {m['withheld']['transport']})")
            vals.append(f"%   budget-bound C1-vs-C2: {pr2['discordant_stated_wins']}/{pr2['n_discordant']}  p={p2txt}")
            vals.append("")
    vals.append(f"% P021AR deliberation gradient (turn-1 output tokens, text-bearing): "
                + ", ".join(f"{c} med {v['median']:.0f} (n={v['n']})" for c, v in sorted(gradient.items())))
    (TEX_DIR / "modern_aead_values.tex").write_text("\n".join(vals) + "\n")
    n_prim = sum(1 for c in cohorts if c["groups"].get("primary"))
    print(f"cohorts={len(cohorts)} (primary groups: {n_prim}) "
          f"p026={p026['sessions']} -> PAPER_EVIDENCE_20261103.{{json,md}} + paper_tables_20261103/")

if __name__ == "__main__":
    main()
