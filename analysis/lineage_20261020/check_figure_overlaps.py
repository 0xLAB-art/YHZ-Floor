"""Check the rendered figures for colliding labels.

Extracts every word box on the pages that carry a figure and reports any two
word boxes that overlap by more than a hair, which is the objective form of
"the labels collide".  Words on the same baseline that merely abut are not
overlaps.

Usage:  python3 check_figure_overlaps.py <pdf> <page> [<page> ...]
"""

import re
import subprocess
import sys
from pathlib import Path


def words(pdf, page):
    xml = subprocess.run(
        ["pdftotext", "-bbox", "-f", str(page), "-l", str(page), str(pdf), "-"],
        capture_output=True, text=True).stdout
    out = []
    for m in re.finditer(
            r'<word xMin="([0-9.]+)" yMin="([0-9.]+)" xMax="([0-9.]+)" yMax="([0-9.]+)">(.*?)</word>',
            xml):
        x0, y0, x1, y1 = (float(m.group(i)) for i in range(1, 5))
        w = m.group(5)
        out.append((x0, y0, x1, y1, w))
    return out


def overlap(a, b):
    """Area of intersection and whether the boxes are on the same baseline."""
    ix = min(a[2], b[2]) - max(a[0], b[0])
    iy = min(a[3], b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    # vertical centres within 1pt of each other => same text line, not a collision
    same_line = abs((a[1] + a[3]) / 2 - (b[1] + b[3]) / 2) < 1.0
    return 0.0 if same_line else ix * iy


def main():
    pdf = Path(sys.argv[1])
    pages = [int(p) for p in sys.argv[2:]]
    total = 0
    for page in pages:
        ws = words(pdf, page)
        # a figure sits above its caption: restrict the scan to that region, so
        # that body-text superscripts are not counted as label collisions
        anchors = [w for w in ws if w[4].startswith("Figure") and w[1] > 0]
        if anchors:
            cap = min(a[1] for a in anchors)
            ws = [w for w in ws if w[3] <= cap + 2.0]
        hits = []
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                area = overlap(ws[i], ws[j])
                if area > 1.0:
                    hits.append((round(area, 1), ws[i][4], ws[j][4]))
        hits.sort(reverse=True)
        print("  page %-3d words=%-4d overlapping pairs=%d" % (page, len(ws), len(hits)))
        for area, a, b in hits[:8]:
            print("      overlap %8.1f pt^2 : %r / %r" % (area, a, b))
        total += len(hits)
    print("  total overlapping label pairs: %d" % total)
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())