"""Apply the figure revision to a paper tree.

Idempotent: each edit is attempted and skipped if its target is absent, so it
can be run on the live tree and on the superseded one.

Usage:  python3 apply_figure_revision.py <paper-dir>
"""

import re
import shutil
import sys
from pathlib import Path

TREE = Path(sys.argv[1])
FIG = TREE / "figures"

# 1. the figure sources
SRC = Path('/mnt/nvme5/ACTS-Attack/sp2027/paper/capability_revision_20261020/figures')
for name in ('fig_harness_readable.tex', 'fig_policy_effects.tex', 'fig_primary_effects.tex'):
    shutil.copy2(SRC / name, FIG / name)
    print('  figures/%s' % name)

CAP = ('\\caption{Preregistered representation contrasts: the paired difference in verified '
       'completion for each arm against R0, pooled over the two task families, at each '
       'observation level. Points are the paired differences and bars their 95\\% intervals; '
       'filled markers are the primary level (L3, $n=128$ pairs per contrast) and open markers '
       'the secondary levels. The shaded band is the predeclared $\\pm10$ percentage point '
       'margin, and the only pooled contrast whose interval leaves it is the secondary L2 '
       '$R2-R0$ cell, which the frozen rule records as inconclusive. The result is specific to '
       'this model route, contract, task level, and pair of families.}')
POLICY_FIG = ('\n\n\\begin{figure}[t]\n\\centering\n\\input{figures/fig_policy_effects}\n'
              '\\caption{Evaluator-policy sensitivity. Applying the prior import policy to the same '
              'generated programs would reject 46 of 256 R0, 16 of 256 R1 and 122 of 256 R2 sessions '
              '(18.0\\%, 6.2\\%, 47.7\\%); the darker part of each bar is the rejections of programs '
              'that would still have succeeded under the repaired policy. The attack code is identical '
              'across the arms, so the difference is a property of the qualification rule, not of the '
              'agent.}\\label{fig:policy-effect}\n\\end{figure}')

# 2. the results section
p = TREE / 'main_sections' / '04_capability.tex'
s = p.read_text()
m = re.search(r'\\caption\{Primary paired effects of representation.*?\\label\{fig:primary-effects\}', s, re.S)
if m:
    s = s.replace(m.group(0), CAP + '\\label{fig:primary-effects}')
    print('  04_capability: contrast caption updated')
else:
    print('  04_capability: contrast caption already current')
s2 = re.sub(r'Figure~\\ref\{fig:primary-effects\}\s+shows\s+these primary contrasts\.',
             'Figure~\\ref{fig:primary-effects} shows\nthe six preregistered pooled contrasts against the margin.', s)
if s2 != s:
    s = s2
    print('  04_capability: reference sentence updated')
if 'fig:policy-effect' not in s:
    t = re.search(r'1 source-qualification failure over 852\s*\n?sessions\.', s)
    if t:
        s = s[:t.end()] + POLICY_FIG + s[t.end():]
        print('  04_capability: policy figure inserted')
    else:
        print('  04_capability: policy paragraph not found -- skipped')
p.write_text(s)

# 3. the design section
q = TREE / 'main_sections' / '03_design.tex'
d = q.read_text()
d2 = re.sub(r'Figure~\\ref\{fig:arch\}\s+shows the three-plane capture-first architecture\.',
            'Figure~\\ref{fig:arch} shows the capture-first harness and the trust boundary that\n'
            'separates the agent-facing path from the evaluation side.', d)
if d2 != d:
    q.write_text(d2)
    print('  03_design: harness sentence updated')
else:
    print('  03_design: harness sentence already current')