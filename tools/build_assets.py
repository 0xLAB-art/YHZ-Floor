#!/usr/bin/env python3
"""Build the README figures as SVG, deterministically, from the frozen records.

Inputs (read, never executed):
  analysis/INFO_CONTRACT_FAMILY.json                  - the registered 16-member
      Holm family: per-cohort paired discordance (C1-stated vs C4-withheld)
  experiments/external_published_audit_20261110/SWEEP_PUBLISHED_AUDIT.json
                                                      - the M1 raised-allowance
      final state (28/50, 8/10 task pairs, 19 never-acted, 5 censored pairs)

The M1 declared-allowance figures (20/50 scored, 30/60 never acted) are stated
in experiments/external_published_audit_20261110/M1_FINAL_RESULTS_20261111.md
and are embedded here as documented constants with that provenance.

Outputs: assets/banner_owners.svg, assets/fig_family.svg, assets/fig_censoring.svg

    python3 tools/build_assets.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- design tokens
BG = "#0d1117"        # card background (deliberate dark card, theme-proof)
EDGE = "#30363d"      # card border + grid
TXT = "#e6edf3"       # primary text
SUB = "#9198a1"       # secondary text
BLUE = "#58a6ff"      # stated-arm wins
RED = "#f85149"       # withheld-arm wins (used sparingly)
AMBER = "#d29922"     # the borderline
GREEN = "#3fb950"     # recovered / solved
FONT = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def card(w: int, h: int) -> str:
    return (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" '
            f'fill="{BG}" stroke="{EDGE}" stroke-width="1"/>')

def header(w: int, title: str, sub: str) -> str:
    return (f'<text x="40" y="52" font-family="{FONT}" font-size="27" '
            f'font-weight="700" fill="{TXT}">{esc(title)}</text>'
            f'<text x="40" y="80" font-family="{FONT}" font-size="15" '
            f'fill="{SUB}">{esc(sub)}</text>')

# ---------------------------------------------------------------- 1. owner banner
OWNERS = [
    ("Admission", "regrade the frozen bytes", "−0.8 → −32.8 → +3.9 pp",
     "trigger executes in 100/101 traces", "#58a6ff"),
    ("Information contract", "withhold the zero-reference premise",
     "one-way in 16/16 contrasts", "96/0 paired · Holm 4.0×10⁻²⁸", "#bc8cff"),
    ("Session wrapper", "interactive vs one-shot", "0/32 each direction",
     "advantage ≤ 10.7% (Wilson 95%)", "#3fb950"),
    ("Compute allowance", "raise the declared budget", "20/50 → 28/50",
     "17 slots transport-unmeasured", "#f78166"),
    ("Execution evidence", "ablate the attribution", "0/44 combined",
     "constructed cases, not deployment", "#d29922"),
]

def build_banner() -> str:
    W, H = 1560, 470
    n = len(OWNERS)
    m = 26
    cw = (W - 2 * 40 - (n - 1) * m) // n
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             card(W, H),
             f'<text x="40" y="56" font-family="{FONT}" font-size="27" font-weight="700" fill="{TXT}">Who owns a published attack-success rate?</text>',
             f'<text x="40" y="84" font-family="{FONT}" font-size="15" fill="{SUB}">Five owners of every number. The audit freezes the contract, moves one owner at a time, and registers what moves.</text>']
    top = 118
    ch = 300
    for i, (name, q, res, bound, col) in enumerate(OWNERS):
        x = 40 + i * (cw + m)
        parts.append(f'<rect x="{x}" y="{top}" width="{cw}" height="{ch}" rx="10" fill="#161b22" stroke="{EDGE}"/>')
        parts.append(f'<rect x="{x}" y="{top}" width="5" height="{ch}" rx="2.5" fill="{col}"/>')
        cx = x + 22
        parts.append(f'<text x="{cx}" y="{top+44}" font-family="{FONT}" font-size="18.5" font-weight="700" fill="{TXT}">{esc(name)}</text>')
        # wrap the question to <=2 lines
        words, lines, cur = q.split(), [], ""
        for wq in words:
            trial = (cur + " " + wq).strip()
            if len(trial) > 20 and cur:
                lines.append(cur); cur = wq
            else:
                cur = trial
        lines.append(cur)
        for j, ln in enumerate(lines[:2]):
            parts.append(f'<text x="{cx}" y="{top+72+j*21}" font-family="{FONT}" font-size="13.5" fill="{SUB}">{esc(ln)}</text>')
        # result, wrapped to <=3 lines
        rw, rl, rc = res.split(), [], ""
        for wq in rw:
            trial = (rc + " " + wq).strip()
            if len(trial) > 16 and rc:
                rl.append(rc); rc = wq
            else:
                rc = trial
        rl.append(rc)
        ry = top + 148
        for j, ln in enumerate(rl[:3]):
            parts.append(f'<text x="{cx}" y="{ry+j*27}" font-family="{FONT}" font-size="21" font-weight="700" fill="{col}">{esc(ln)}</text>')
        # bound
        bw, bl, bc = bound.split(), [], ""
        for wq in bw:
            trial = (bc + " " + wq).strip()
            if len(trial) > 22 and bc:
                bl.append(bc); bc = wq
            else:
                bc = trial
        bl.append(bc)
        by = top + ch - 62
        parts.append(f'<line x1="{cx}" y1="{by-14}" x2="{x+cw-18}" y2="{by-14}" stroke="{EDGE}"/>')
        parts.append(f'<text x="{cx}" y="{by+6}" font-family="{FONT}" font-size="12.5" fill="{SUB}">BOUND</text>')
        for j, ln in enumerate(bl[:2]):
            parts.append(f'<text x="{cx}" y="{by+26+j*19}" font-family="{FONT}" font-size="13" fill="#c9d1d9">{esc(ln)}</text>')
    parts.append(f'<text x="40" y="{H-22}" font-family="{FONT}" font-size="13" fill="{SUB}">Every cell regenerates from the frozen per-seed rows in experiments/ — see the index and docs/VERIFYING.md.</text>')
    parts.append('</svg>')
    return "\n".join(parts)

# ---------------------------------------------------------------- 2. family chart
LABELS = {
    "P010P": "P010P — the borderline",
    "P010N16": "P010N16 — exact-test floor",
    "P010X1": "P010X1 — cross-label",
    "P010L2": "P010L2 — label replication",
    "P010L3": "P010L3 — label replication",
    "P013": "P013",
    "P011-L3-N32": "P011-L3-N32 — n=32 scale-up",
    "P014": "P014",
    "P016-6.1sol": "P016-6.1sol",
    "P017": "P017",
    "P018": "P018",
    "P019": "P019",
    "P021AR": "P021AR — 96-instance power cohort",
    "P022a": "P022a",
    "P023": "P023 — fresh-seed replication",
    "P024a": "P024a",
}

def sup(n: int) -> str:
    return str(n).translate(str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"))

def fmt_p(p: float) -> str:
    if p >= 0.001:
        return f"{p:.3g}"
    m = f"{p:.2e}".split("e")
    return f"{m[0]}×10{sup(int(m[1]))}"

def build_family() -> str:
    fam = json.loads((ROOT / "analysis/INFO_CONTRACT_FAMILY.json").read_text())
    members = sorted(fam["members"], key=lambda r: (-r["discordant_c1_only"], r["holm_adjusted"]))
    W, H = 1400, 720
    ML, MR, MT, MB = 330, 230, 132, 74
    pw = W - ML - MR
    xmax = 100
    scale = pw / xmax
    rh = (H - MT - MB) / len(members)
    bh = 15
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             card(W, H),
             header(W, "The registered family: every paired contrast is one-way",
                    "16 cohorts · paired discordance on shared seeds · stated-arm wins vs withheld-arm wins · Holm step-down, FWER 0.05"),
             f'<text x="{ML}" y="{MT-22}" font-family="{FONT}" font-size="13.5" font-weight="600" fill="{BLUE}">■ stated-arm wins</text>',
             f'<text x="{ML+160}" y="{MT-22}" font-family="{FONT}" font-size="13.5" font-weight="600" fill="{RED}">○ withheld-arm wins — zero in every row</text>',
             f'<text x="{W-40}" y="{MT-22}" font-family="{FONT}" font-size="13.5" font-weight="600" fill="{SUB}" text-anchor="end">Holm-adjusted p</text>']
    # gridlines
    for g in (0, 20, 40, 60, 80, 96):
        x = ML + g * scale
        parts.append(f'<line x1="{x:.1f}" y1="{MT}" x2="{x:.1f}" y2="{H-MB+8}" stroke="#21262d"/>')
        parts.append(f'<text x="{x:.1f}" y="{H-MB+26}" font-family="{FONT}" font-size="12.5" fill="{SUB}" text-anchor="middle">{g}</text>')
    parts.append(f'<text x="{ML+pw/2:.0f}" y="{H-30}" font-family="{FONT}" font-size="13" fill="{SUB}" text-anchor="middle">discordant pairs, stated minus withheld, on shared seeds</text>')
    y = MT
    for mem in members:
        c1, c4 = mem["discordant_c1_only"], mem["discordant_c4_only"]
        p = mem["holm_adjusted"]
        cy = y + rh / 2
        name = LABELS.get(mem["cohort"], mem["cohort"])
        border = mem["cohort"] == "P010P"
        col = AMBER if border else BLUE
        parts.append(f'<text x="{ML-12}" y="{cy+4.5:.1f}" font-family="{FONT}" font-size="13.5" fill="{TXT if not border else AMBER}" text-anchor="end">{esc(name)}</text>')
        parts.append(f'<rect x="{ML}" y="{cy-bh/2:.1f}" width="{c1*scale:.1f}" height="{bh}" rx="3" fill="{col}" opacity="{0.95 if not border else 0.9}"/>')
        parts.append(f'<circle cx="{ML + c4*scale:.1f}" cy="{cy:.1f}" r="5.5" fill="{BG}" stroke="{RED}" stroke-width="2"/>')
        if c1 * scale >= 110:
            parts.append(f'<text x="{ML + c1*scale - 10:.1f}" y="{cy+4.5:.1f}" font-family="{FONT}" font-size="13.5" font-weight="700" fill="{BG}" text-anchor="end">{c1}/{c4}</text>')
        else:
            parts.append(f'<text x="{ML + c1*scale + 10:.1f}" y="{cy+4.5:.1f}" font-family="{FONT}" font-size="13.5" font-weight="600" fill="{TXT}">{c1}/{c4}</text>')
        ptxt = fmt_p(p)
        pc = AMBER if border else ("#7ee787" if p < 0.05 else SUB)
        parts.append(f'<text x="{W-40}" y="{cy+4.5:.1f}" font-family="{FONT}" font-size="13.5" fill="{pc}" text-anchor="end">{ptxt}</text>')
        if border:
            parts.append(f'<text x="{W-40}" y="{cy+21:.1f}" font-family="{FONT}" font-size="11.5" fill="{AMBER}" text-anchor="end">prints as its own bound</text>')
        y += rh
    parts.append(f'<text x="40" y="{H-10}" font-family="{FONT}" font-size="12.5" fill="{SUB}">Source: analysis/INFO_CONTRACT_FAMILY.json (registered). The one borderline prints as its own bound — never absorbed.</text>')
    parts.append('</svg>')
    return "\n".join(parts)

# ---------------------------------------------------------------- 3. censoring chart
def build_censoring() -> str:
    W, H = 1400, 560
    # declared: 20/50 solved (M1_FINAL_RESULTS_20261111.md); raised final state from SWEEP
    sweep = json.loads((ROOT / "experiments/external_published_audit_20261110/SWEEP_PUBLISHED_AUDIT.json").read_text())
    solved_raised = sweep["session_level"]["C1_whole_stdout"]          # 28
    task_pairs_raised = sweep["task_level"]["C1_whole_stdout"]         # 8
    never_acted_raised = sweep["censoring"]["never_acted"]             # 19
    solved_decl, total = 20, 50                                        # documented constants
    pairs_decl = 6                                                     # documented constant
    ML, MT = 40, 110
    bw, gap = 250, 130
    plot_h = 300
    scale = plot_h / total
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             card(W, H),
             header(W, "The allowance censors the number",
                    "One published protocol, re-run on its own frozen inputs. Only the token allowance moves — each raise a numbered amendment, recorded before it ran."),
             f'<line x1="{ML}" y1="{MT+plot_h}" x2="{ML+2*bw+gap+60}" y2="{MT+plot_h}" stroke="{EDGE}"/>']
    for i, (cap, solved, pairs, col) in enumerate([
            ("declared allowance — 12,000 tokens", solved_decl, pairs_decl, "#6e7681"),
            ("raised — 32k, then 64k", solved_raised, task_pairs_raised, GREEN)]):
        x = ML + 30 + i * (bw + gap)
        bh_ = solved * scale
        parts.append(f'<rect x="{x}" y="{MT+plot_h-bh_:.1f}" width="{bw}" height="{bh_:.1f}" rx="8" fill="{col}" opacity="0.85"/>')
        parts.append(f'<text x="{x+bw/2}" y="{MT+plot_h-bh_-14:.1f}" font-family="{FONT}" font-size="30" font-weight="700" fill="{TXT}" text-anchor="middle">{solved}/50</text>')
        parts.append(f'<text x="{x+bw/2}" y="{MT+plot_h+28}" font-family="{FONT}" font-size="15.5" font-weight="600" fill="{TXT}" text-anchor="middle">{esc(cap)}</text>')
        parts.append(f'<text x="{x+bw/2}" y="{MT+plot_h+52}" font-family="{FONT}" font-size="14" fill="{SUB}" text-anchor="middle">task-level pairs: {pairs}/10</text>')
    ax = ML + 2 * bw + gap + 90
    items = [
        ("30 of 60 sessions never acted", "every turn consumed by hidden reasoning — zero submissions at the declared allowance"),
        ("recovered, not failed", f"the raises turn censored slots into solves: {pairs_decl}/10 → {task_pairs_raised}/10 pairs, identical under all five evaluator rules"),
        ("transport-unmeasured: 17 slots", "HTTP 504, zero turns, every retry — excluded from the scored set; never a model failure"),
    ]
    iy = MT + 16
    for head, body in items:
        parts.append(f'<text x="{ax}" y="{iy}" font-family="{FONT}" font-size="16.5" font-weight="700" fill="{TXT}">{esc(head)}</text>')
        words, lines, cur = body.split(), [], ""
        for wq in words:
            trial = (cur + " " + wq).strip()
            if len(trial) > 46 and cur:
                lines.append(cur); cur = wq
            else:
                cur = trial
        lines.append(cur)
        for j, ln in enumerate(lines[:3]):
            parts.append(f'<text x="{ax}" y="{iy+22+j*19}" font-family="{FONT}" font-size="13.5" fill="{SUB}">{esc(ln)}</text>')
        iy += 108
    parts.append(f'<text x="40" y="{H-20}" font-family="{FONT}" font-size="13" fill="{SUB}">A published rate is only as strong as the allowance it was measured under — one that does not state its allowance has not stated its own meaning.</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def main() -> int:
    out = ROOT / "assets"
    (out / "banner_owners.svg").write_text(build_banner())
    (out / "fig_family.svg").write_text(build_family())
    (out / "fig_censoring.svg").write_text(build_censoring())
    print("assets written: banner_owners.svg fig_family.svg fig_censoring.svg")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
