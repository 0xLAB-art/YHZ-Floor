import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAPER = ROOT / 'sp2027/paper/split_rebuild_evidence_promotion'
previous = ROOT / 'sp2027/analysis/capability_rebuild_20261016/validate_revision.py'
spec = importlib.util.spec_from_file_location('capability_revision_validation', previous)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
captured = {}
saved_write = Path.write_text


def capture_write(path, text, *args, **kwargs):
    captured[str(path)] = text
    return len(text)


try:
    Path.write_text = capture_write
    with contextlib.redirect_stdout(io.StringIO()):
        module.main()
finally:
    Path.write_text = saved_write

result = json.loads(captured[str(previous.parent / 'VALIDATION.json')])
intro = (PAPER / 'main_sections/01_intro.tex').read_text()
results = (PAPER / 'main_sections/05_results.tex').read_text()
synthesis = (PAPER / 'main_sections/06_synthesis.tex').read_text()
needles = ['Agents complete recoveries', 'Construction traces connect',
           'Historical transcripts extend', 'The exposed interface determines',
           'An agent-produced candidate closes', 'Delivery and timing records',
           'Operation timing and agent timing', 'Process calibration defines',
           'Execution linkage closes']
positions = [results.find(needle) for needle in needles]
checks = result['checks']
checks['narrative:results_follow_declared_path'] = all(p >= 0 for p in positions) and positions == sorted(positions)
checks['narrative:connected_experiment_table_referenced'] = '\\ref{tab:acts-boundary-map}' in intro and '\\label{tab:acts-boundary-map}' in results
checks['narrative:four_research_questions_answered'] = len(re.findall(r'\\item \\textbf\{RQ[1-4]:\}', intro)) == 4 and all('\\textbf{RQ' + str(i) + ':}' in synthesis for i in range(1, 5))
checks['narrative:supporting_argument_map_present'] = (HERE / 'EXPERIMENT_ARGUMENT_MAP.md').is_file()
result['all_pass'] = all(checks.values())
result['revision'] = 'Connected argument from retained experiments, 16 October 2026'
result['narrative_check_scope'] = 'Structure/reference checks only; not certification of novelty, scientific generality or acceptance.'
result['visual_inspection'] = 'Recorded separately in REVISION_REPORT.md.'
(HERE / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'checks': len(checks), 'all_pass': result['all_pass'],
                  'test_count': result['test_count'], 'pages': result['pages'],
                  'failures': [k for k, v in checks.items() if not v]}, indent=2))
if not result['all_pass']:
    raise SystemExit(1)
