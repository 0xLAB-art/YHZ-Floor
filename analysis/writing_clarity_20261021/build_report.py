from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PAPER = ROOT / 'sp2027/paper/capability_revision_20261020'
NUMBER = r'(?<![A-Za-z_])\d+(?:\.\d+)*(?![A-Za-z_])'
ROLES = [
    ('An agent can recover', 'Abstract: problem, method, evidence, and scope'),
    ('What does a reported', 'Opening: distinguish the questions behind success'),
    ('ACTS-Attack studies these', 'Method rationale: independent checks of recovered values'),
    ('Admission alone', 'Evidence: local fixed-program admission effect'),
    ('The construction studies', 'Evidence: operation feasibility and agent construction'),
    ('Execution attribution raises', 'Transition: correctness leaves execution questions open'),
    ('Prior ACTS', 'Context: relation to earlier cryptographic evaluations'),
    ('The experiments address', 'Scope: complementary populations'),
    ('The design uses', 'Design: roles of the experimental populations'),
    ('Interactive tasks', 'Setup: information and execution interfaces'),
    ('The secondary ECDSA', 'Evidence and limitation: parameter error and unresolved association'),
    ('The earlier import filter', 'Design and accounting: source rejection versus cryptographic failure'),
    ('For instance', 'Definition: the fixed-program admission estimand'),
    ('The per-arm rates', 'Mechanism: representation-associated imports'),
    ('Conservative unused-import', 'Control: output-preserving cleanup'),
    ('The trajectories help', 'Interpretation: task-specific recovery conditions'),
    ('Attempt~4 tests', 'Evidence and scope: held-out alphabet transfer'),
    ('A separately registered arm', 'Diagnostic: recorded endpoints and XOR scorer qualification'),
    ('The target\'s final check', 'Motivation: the target event defines the consequence'),
    ('An accepted result must', 'Transition: checked object and execution history'),
    ('The execution architecture', 'Limitation: acquisition and verifier identity'),
    ('The public-release audit', 'Question and method: public reconstruction'),
    ('The published-outcome field', 'Interpretation: field-specific rubric requirements'),
    ('Available records may', 'Motivation and design: authenticity plus consistency'),
    ('A configured in-toto', 'Implementation evidence: configured policy agreement'),
    ('The studies show', 'Synthesis: interpreting different success events'),
    ('We quantify how', 'Contribution: measured effects and concrete failure mechanisms'),
    ('ACTS-Attack examines', 'Conclusion: the empirical account and its scope'),
]


def prose_blocks(text):
    for block in re.split(r'\n\s*\n', text):
        if '\\begin{abstract}' in block:
            block = block.split('\\begin{abstract}', 1)[1].split('\\end{abstract}', 1)[0]
        elif any(x in block for x in ['\\begin{table', '\\begin{figure', '\\begin{tabular', '\\[', '\\end{document}', '\\begin{document}']):
            continue
        block = re.sub(r'^\\(?:sub)*section\*?\{[^}]*\}(?:\\label\{[^}]*\})?\s*', '', block.strip())
        block = re.sub(r'^\\paragraph\{[^}]*\}(?:\\label\{[^}]*\})?\s*', '', block)
        if block and re.search(r'[A-Za-z]{4}', block) and not block.startswith(('\\end', '\\midrule', '\\toprule', '\\bottomrule', '\\item', '\\caption', '\\input', '\\label', '\\centering', '\\begin')):
            yield block


def role(block):
    return next((label for prefix, label in ROLES if block.startswith(prefix)), 'Explanation, evidence, or scope within the named subsection')


baseline = json.loads((OUT/'baseline.json').read_text())
checks, patches, outline, revised = [], [], ['# Reverse outline\n'], ['# Revised paragraphs and their roles\n']
for entry in baseline:
    relative = entry['path']
    before = (OUT/'before'/Path(relative).name).read_text()
    after = (PAPER/relative).read_text()
    if hashlib.sha256(before.encode()).hexdigest() != entry['sha256']:
        raise RuntimeError('Baseline changed: '+relative)
    a, b = Counter(re.findall(NUMBER, before)), Counter(re.findall(NUMBER, after))
    commands = {}
    for command in ['label', 'cite', 'ref']:
        pattern = r'\\'+command+r'\{([^}]+)\}'
        old, new = Counter(re.findall(pattern, before)), Counter(re.findall(pattern, after))
        commands[command] = dict(removed=dict(old-new), added=dict(new-old))
    equations_equal = re.findall(r'\\\[(.*?)\\\]', before, re.S) == re.findall(r'\\\[(.*?)\\\]', after, re.S)
    checks.append(dict(path=relative, changed=before!=after, before_sha256=entry['sha256'],
                       after_sha256=hashlib.sha256(after.encode()).hexdigest(),
                       removed_numbers=dict(a-b), added_numbers=dict(b-a), commands=commands,
                       displayed_equations_identical=equations_equal))
    patches.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='before/'+relative, tofile='after/'+relative))
    old_blocks = set(prose_blocks(before))
    outline.append('\n## '+relative+'\n')
    revised.append('\n## '+relative+'\n')
    for number, block in enumerate(prose_blocks(after), 1):
        line = ' '.join(block.split())
        topic = re.split(r'(?<=[.!?])\s+', line, maxsplit=1)[0]
        outline.append(f'- P{number} [{role(block)}]: {topic}\n')
        if block not in old_blocks:
            revised.append(f'\n### P{number}: {role(block)}\n\n```latex\n{block}\n```\n')

(OUT/'writing_revision.patch').write_text(''.join(patches))
(OUT/'surface_checks.json').write_text(json.dumps(checks, indent=2)+'\n')
(OUT/'REVERSE_OUTLINE.md').write_text(''.join(outline))
(OUT/'REVISED_PARAGRAPHS.md').write_text(''.join(revised))
summary = dict(active_files=len(checks), changed_files=sum(x['changed'] for x in checks),
               numeric_token_multisets_preserved=all(not x['removed_numbers'] and not x['added_numbers'] for x in checks),
               citation_arguments_preserved=all(not any(x['commands']['cite'].values()) for x in checks),
               labels_preserved=all(not any(x['commands']['label'].values()) for x in checks),
               displayed_equations_preserved=all(x['displayed_equations_identical'] for x in checks),
               added_cross_reference='sec:h1 in the Checkpoint 009 diagnostic',
               experiments_executed=False, evidence_rescored=False,
               detector_workspace='Opened empty; no scan or score obtained')
(OUT/'SUMMARY.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
