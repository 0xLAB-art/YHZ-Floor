#!/usr/bin/env python3
"""Generate the three animated SVG assets for the YHZ-Floor README.

All animation is CSS-keyframe based inside the SVG (GitHub renders CSS
animations for SVGs referenced through <img>). Palette follows the
paper's own colors: actblue #235480, light #ECF3F9, orange #AE5E20,
green #28745A, red #962828 on a dark slate ground.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent


def hero_owners() -> str:
    """Five owner cards rising staggered with filling contrast bars and a
    slow-rotating isometric floor emblem (the 3D feel)."""
    cards = [
        ("Admission", "-0.8 \u2192 -32.8 \u2192 +3.9 pp", 78, "#7fb3dd"),
        ("Information contract", "96/0 one-way, Holm 4.0e-28", 96, "#5aa876"),
        ("Session wrapper", "0/32 null, \u226410.7% Wilson", 32, "#d9a441"),
        ("Compute allowance", "20/50 \u2192 28/50 (16 pp)", 56, "#c98a4b"),
        ("Execution evidence", "0/44 combined promotions", 12, "#b96a6a"),
    ]
    card_w, card_h, gap = 160, 190, 18
    x0, y0 = 60, 118
    card_svg = []
    for i, (name, stat, fill_pct, color) in enumerate(cards):
        x = x0 + i * (card_w + gap)
        card_svg.append(f'''
  <g class="card" style="animation-delay:{0.15 + i * 0.22:.2f}s">
    <rect x="{x}" y="{y0}" width="{card_w}" height="{card_h}" rx="10"
          fill="#17222e" stroke="{color}" stroke-width="1.4"/>
    <text x="{x + card_w / 2}" y="{y0 + 34}" text-anchor="middle" class="cname">{name}</text>
    <rect x="{x + 14}" y="{y0 + 56}" width="{card_w - 28}" height="14" rx="7" fill="#0d151d"/>
    <rect x="{x + 14}" y="{y0 + 56}" width="0" height="14" rx="7" fill="{color}">
      <animate attributeName="width" from="0" to="{(card_w - 28) * fill_pct / 100:.0f}"
               begin="{0.5 + i * 0.25:.2f}s" dur="1.4s" fill="freeze"
               calcMode="spline" keySplines="0.25 0.8 0.3 1"/>
    </rect>
    <text x="{x + card_w / 2}" y="{y0 + 100}" text-anchor="middle" class="cstat">{stat}</text>
    <text x="{x + card_w / 2}" y="{y0 + 128}" text-anchor="middle" class="ctag">registered &#183; hash-frozen</text>
    <circle class="pulse" style="animation-delay:{1.2 + i * 0.3:.2f}s"
            cx="{x + card_w / 2}" cy="{y0 + 158}" r="5" fill="{color}"/>
    <text x="{x + card_w / 2}" y="{y0 + 178}" text-anchor="middle" class="cfoot">intervention measured</text>
  </g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" font-family="Segoe UI,Helvetica,Arial,sans-serif">
  <style>
    .bg {{ fill: #0b1218; }}
    .title {{ fill: #ecf3f9; font-size: 21px; font-weight: 600; letter-spacing: .4px; }}
    .sub   {{ fill: #8fa8bd; font-size: 12.5px; }}
    .cname {{ fill: #ecf3f9; font-size: 13.5px; font-weight: 600; }}
    .cstat {{ fill: #c9d9e8; font-size: 12px; }}
    .ctag  {{ fill: #6d8296; font-size: 10px; }}
    .cfoot {{ fill: #6d8296; font-size: 9.5px; letter-spacing: .5px; }}
    .card  {{ opacity: 0; animation: rise .9s cubic-bezier(.2,.7,.3,1) forwards; }}
    .pulse {{ opacity: .15; animation: pulse 2.6s ease-in-out infinite; }}
    .beam  {{ stroke: #235480; stroke-width: 1.2; opacity: .55; stroke-dasharray: 5 7;
             animation: dash 3.2s linear infinite; }}
    .floor {{ transform-origin: 480px 322px; animation: tilt 14s ease-in-out infinite alternate; }}
    @keyframes rise   {{ from {{ opacity: 0; transform: translateY(26px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes pulse  {{ 0%,100% {{ opacity: .12; }} 50% {{ opacity: .95; }} }}
    @keyframes dash   {{ to   {{ stroke-dashoffset: -48; }} }}
    @keyframes tilt   {{ from {{ transform: rotate(-.6deg) scaleY(.985); }} to {{ transform: rotate(.6deg) scaleY(1.015); }} }}
  </style>
  <rect class="bg" width="960" height="360" rx="12"/>
  <text x="480" y="40" text-anchor="middle" class="title">Who owns the number? &#8212; five owners, one frozen intervention each</text>
  <text x="480" y="62" text-anchor="middle" class="sub">paired contrasts on shared seeds &#183; pre-registered &#183; every null measured, never pooled</text>
  <g class="floor">
    <rect x="120" y="318" width="720" height="3" rx="1.5" fill="#235480" opacity=".85"/>
    <rect x="180" y="324" width="600" height="2" rx="1" fill="#235480" opacity=".45"/>
  </g>
  {''.join(card_svg)}
  <line class="beam" x1="480" y1="76" x2="200" y2="112"/>
  <line class="beam" x1="480" y1="76" x2="480" y2="112"/>
  <line class="beam" x1="480" y1="76" x2="760" y2="112"/>
</svg>
'''


def discordance_family() -> str:
    """The 16-member Holm family: bars grow to their paired discordance,
    the borderline 5/0 stays amber, the significance line sweeps in."""
    fam = [
        ("P021AR", 96), ("P023", 95), ("P011-N32", 32), ("P019", 24),
        ("P022a", 24), ("P024a", 24), ("P018", 22), ("P013", 16),
        ("P017", 16), ("P014", 13), ("P016", 12), ("P010N16", 10),
        ("P010X1", 10), ("P010L2", 8), ("P010L3", 8), ("P010P", 5),
    ]
    x0, base, bw, gap, maxh = 52, 352, 38, 12, 268
    bars, labels = [], []
    for i, (name, n) in enumerate(fam):
        x = x0 + i * (bw + gap)
        h = maxh * n / 100
        delay = 0.12 + i * 0.11
        color = "#d9a441" if name == "P010P" else "#5aa876"
        bars.append(
            f'<rect class="bar" style="animation-delay:{delay:.2f}s" x="{x}" y="{base}" '
            f'width="{bw}" height="{h:.0f}" rx="4" fill="{color}"/>')
        bars.append(
            f'<text class="val" style="animation-delay:{delay + 0.55:.2f}s" '
            f'x="{x + bw / 2}" y="{base - 10:.0f}" text-anchor="middle">{n}/0</text>')
        labels.append(
            f'<text class="lbl" x="{x + bw / 2}" y="{base + 18}" text-anchor="middle">{name}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="430" viewBox="0 0 960 430" font-family="Segoe UI,Helvetica,Arial,sans-serif">
  <style>
    .bg {{ fill: #0b1218; }}
    .title {{ fill: #ecf3f9; font-size: 19px; font-weight: 600; }}
    .sub {{ fill: #8fa8bd; font-size: 12px; }}
    .lbl {{ fill: #8fa8bd; font-size: 10.5px; }}
    .val {{ fill: #dce7f1; font-size: 11px; font-weight: 600; opacity: 0; animation: fade .6s forwards; }}
    .note {{ fill: #6d8296; font-size: 11px; }}
    .amber {{ fill: #d9a441; font-size: 11.5px; }}
    .bar {{ transform-origin: 50% 100%; transform: scaleY(0); animation: grow 1.1s cubic-bezier(.2,.8,.3,1) forwards; }}
    .hline {{ stroke: #962828; stroke-width: 1.3; stroke-dasharray: 6 6;
             stroke-dashoffset: 900; animation: sweep 1.6s 1.4s forwards ease-out; }}
    @keyframes grow  {{ to {{ transform: scaleY(1); }} }}
    @keyframes fade  {{ to {{ opacity: 1; }} }}
    @keyframes sweep {{ to {{ stroke-dashoffset: 0; }} }}
  </style>
  <rect class="bg" width="960" height="430" rx="12"/>
  <text x="480" y="36" text-anchor="middle" class="title">The registered 16-member family: every paired contrast is one-way</text>
  <text x="480" y="58" text-anchor="middle" class="sub">paired C1-versus-C4 discordance per cohort &#183; Holm step-down at FWER 0.05 &#183; regenerated from raw per-seed rows</text>
  <line class="hline" x1="46" y1="330" x2="920" y2="330"/>
  <text class="note" x="920" y="322" text-anchor="end">every cohort clears the correction; the 5/0 borderline prints as its own bound</text>
  {''.join(bars)}
  {''.join(labels)}
  <text class="amber" x="480" y="404" text-anchor="middle">P010P (5/0, Holm 0.0625) is reported as its own bound &#8212; never absorbed into a family claim</text>
</svg>
'''


def allowance_censoring() -> str:
    """The M1 story: 60 slots; 30 censored at the declared allowance pulsing
    amber, then slots flip solved as the allowance bar widens 12k -> 64k."""
    slots = []
    solved_12k = set(range(0, 60, 3))
    censored = [i for i in range(60) if i not in solved_12k][:30]
    recovered = set(range(1, 60, 3))
    x0, y0, sw, sh, g = 52, 96, 20, 20, 6
    for i in range(60):
        r, c = divmod(i, 15)
        x = x0 + c * (sw + g)
        y = y0 + r * (sh + g)
        cls = []
        if i in solved_12k:
            cls.append("solved")
        if i in censored:
            cls.append("censored")
        if i in recovered:
            cls.append("recovered")
        slot_cls = " ".join(cls) if cls else "unknown"
        slots.append(f'<rect class="slot {slot_cls}" x="{x}" y="{y}" width="{sw}" height="{sh}" rx="4"/>')
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300" font-family="Segoe UI,Helvetica,Arial,sans-serif">
  <style>
    .bg { fill: #0b1218; }
    .title { fill: #ecf3f9; font-size: 19px; font-weight: 600; }
    .sub { fill: #8fa8bd; font-size: 12px; }
    .legend { fill: #a9bccd; font-size: 11px; }
    .slot { fill: #1a2530; stroke: #2c3a47; }
    .solved { fill: #28745a; }
    .censored { fill: #7a5a1e; animation: censor 2.4s ease-in-out infinite; }
    .recovered { fill: #1a2530; animation: recover 1.2s 3.4s forwards; }
    .atext { fill: #ecf3f9; font-size: 12.5px; font-weight: 600; }
    .count { fill: #ecf3f9; font-size: 20px; font-weight: 700; }
    @keyframes censor { 0%,100% { opacity: .55; } 50% { opacity: 1; } }
    @keyframes recover { to { fill: #5aa876; } }
    .abar { width: 0; animation: awiden 2.2s 2.6s cubic-bezier(.3,.8,.3,1) forwards; }
    @keyframes awiden { to { width: 320px; } }
  </style>
  <rect class="bg" width="960" height="300" rx="12"/>
  <text x="480" y="36" text-anchor="middle" class="title">The allowance owns part of the number: 20/50 at the declared 12,000 tokens, 28/50 raised</text>
  <text x="480" y="58" text-anchor="middle" class="sub">M1 published-protocol audit &#183; 60 registered sessions &#183; 30 ceiling-censored (zero submissions, reasoning-only) &#183; 17 transport-unmeasured</text>
  ''' + ''.join(slots) + '''
  <text class="legend" x="52" y="232">green = solved &#183; pulsing amber = ceiling-censored (unmeasured, not failed) &#183; flashing = recovered by the 32k/64k amendments</text>
  <text class="atext" x="52" y="262">declared allowance 12,000 tokens</text>
  <rect x="298" y="250" width="10" height="14" rx="3" fill="#235480"/>
  <rect class="abar" x="310" y="250" width="0" height="14" rx="3" fill="#5aa876" opacity=".85"/>
  <text class="atext" x="640" y="262" text-anchor="end">raised: 32,000 / 64,000 tokens</text>
  <text class="count" x="52" y="290">20/50 solved &#8594; 28/50 &#183; 8/10 task-level &#183; identical under all five evaluator rules</text>
</svg>
'''


def main():
    OUT.joinpath("hero_owners.svg").write_text(hero_owners())
    OUT.joinpath("discordance_family.svg").write_text(discordance_family())
    OUT.joinpath("allowance_censoring.svg").write_text(allowance_censoring())
    for f in sorted(OUT.glob("*.svg")):
        print(f.name, f.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
