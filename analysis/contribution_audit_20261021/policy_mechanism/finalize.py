import collections
import json
import sys
from pathlib import Path
from audit import HERE, sha, write


def main():
    run = (HERE / '.omo/evidence/run01').resolve()
    rows = [json.loads(s) for s in (run / 'CASE_LEDGER.jsonl').read_text().splitlines()]
    traces = {r['session_id']: r for r in json.loads((run / 'import_use_trace_v2/RESULTS.json').read_text())}
    for r in rows:
        r['original_legacy_admitted'] = r['legacy']['qualified']
        r['derivative_legacy_admitted'] = r['derivative_legacy']['qualified']
        r['current_outcome_correct'] = r['original']['cryptographic_predicate']
        r['transformation_applied'] = bool(r['edits'])
        r['transform_eligibility'] = 'eligible_full_import_statements_removed' if r['edits'] else 'no_eligible_full_import_statement'
        r['transform_reason'] = 'Remove only top-level whole imports whose every binding lacks any syntax/name/string/dynamic access concern; retain all mixed, used, nested, unknown-side-effect imports.'
        r['fresh_output_equality'] = r.get('derivative_same_output_as_original')
        r['fresh_output_equality_scope'] = 'parsed JSON equality for executed derivative; null means no derivative executed'
        r['runtime_import_use'] = traces.get(r['session_id'])
        write(run / 'cases' / r['session_id'] / 'case.json', r)
    (run / 'CASE_LEDGER.jsonl').write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows))
    census = []
    for key in sorted({(r['kind'], r['arm'], r['level'], r['family']) for r in rows}):
        group = [r for r in rows if tuple(r[k] for k in ('kind', 'arm', 'level', 'family')) == key]
        census.append(dict(zip(('kind', 'arm', 'level', 'family'), key)) | {
            'n': len(group), 'current_correct': sum(r['current_outcome_correct'] for r in group),
            'original_legacy_admitted': sum(r['original_legacy_admitted'] for r in group),
            'derivative_legacy_admitted': sum(r['derivative_legacy_admitted'] for r in group),
            'original_legacy_admitted_correct': sum(r['original_legacy_admitted'] and r['current_outcome_correct'] for r in group),
            'derivative_legacy_admitted_correct': sum(r['derivative_legacy_admitted'] and r['current_outcome_correct'] for r in group),
            'legacy_classes': dict(collections.Counter(r['legacy_class'] for r in group)),
            'observed_import_use_cases': sum(bool((r['runtime_import_use'] or {}).get('observed_loaded_import_bindings')) for r in group)})
    write(run / 'FULL_CENSUS.json', census)
    summary = json.loads((run / 'SUMMARY.json').read_text())
    tests = (HERE / '.omo/evidence/tests-final.log').read_text()
    assert 'Ran 15 tests' in tests and '\nOK\n' in tests
    assert len(rows) == 852 and sum(r['transformation_applied'] for r in rows) == 128
    assert sum(bool(t['observed_loaded_import_bindings']) for t in traces.values()) == 100
    assert all(t['same_output_as_uninstrumented'] and t['returncode'] == 0 for t in traces.values())
    assert all(r['fresh_output_equality'] is True for r in rows if r['transformation_applied'])
    inputs = json.loads((run / 'input_manifest.json').read_text())
    assert all(sha(Path(p)) == digest for p, digest in inputs.items())
    validation = {'status': 'PASS', 'rows': 852, 'transformed_rows': 128, 'tests': 15,
                  'observed_runtime_import_use_cases': 100, 'static_reference_only_cases': 1,
                  'input_file_count': len(inputs), 'input_files_unchanged': True,
                  'expected_empty_files': 'Successful stderr.txt files may be empty; result.json records their SHA-256 and return code.',
                  'evidence': {'tests': str(HERE / '.omo/evidence/tests-final.log'), 'census': str(run / 'FULL_CENSUS.json'), 'ledger': str(run / 'CASE_LEDGER.jsonl')}}
    write(run / 'VALIDATION.json', validation)
    report = '''# Source-policy mechanism audit — 2026-10-21

The actual v3 representation outcomes do not reduce to source-import rejection: **zero of 852 sources were rejected for imports under v3**. The three pre-output failures are one syntax error and two runtime errors. Cryptographic checks freshly reproduce 738/768 primary completions, 63/64 R4 noise completions, and 20/20 C0 correct abstentions. These are separate populations and predicates.

The narrower legacy policy is a **counterfactual policy**, not the task contract stated in these prompts. Its 205 import rejects all concern modules explicitly permitted by the frozen prompt; the additional reject is syntax. Calling these 205 programs task-contract violations would be incorrect. Applying legacy policy to unchanged generated artifacts measures local policy sensitivity, not generation under a legacy prompt.

| Population | N | Legacy qualified | Unused-only removable reject | Referenced import remains | Syntax | Legacy rejected, cryptographically correct |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 768 | 584 | 99 | 84 | 1 | 168 |
| R4 noise | 64 | 47 | 4 | 13 | 0 | 16 |
| C0 abstention | 20 | 15 | 1 | 4 | 0 | 5 |

128 derivatives remove only eligible, whole, top-level import statements. Every derivative produces the identical parsed JSON output as its unmodified fresh execution. 104 now qualify under legacy; 98 are correct (primary 94, noise 3, C0 1), while six remain incorrect (primary 5, noise 1). The other 24 derivatives still contain referenced imports and remain legacy-rejected. No program logic was repaired, and none of the 31 original incorrect outcomes was improved.

| Primary arm (all levels, descriptive only) | N | Original legacy-qualified and correct | After conservative removal, legacy-qualified and correct | Actual v3 correct |
|---|---:|---:|---:|---:|
| R0 | 256 | 207 | 214 | 250 |
| R1 | 256 | 238 | 250 | 254 |
| R2 | 256 | 125 | 200 | 234 |

These arm totals are not the preregistered L3 estimand. `FULL_CENSUS.json` separates every population/arm/level/family, and `CASE_LEDGER.jsonl` preserves seed and replicate index for matched analyses. The large counterfactual policy effect is partly an unused-import artifact but does not disappear after conservative cleanup; residual rejection includes source that actually uses permitted helper modules. This does not establish those imports are necessary to all possible solutions.

Runtime tracing separately observed a LOAD opcode with imported-object identity in **100 of the 101 sources with legacy-disallowed static references** (typing, collections, math). Their instrumented outputs exactly match the fresh uninstrumented outputs. One noise source, `confirmatory-0328-ecd-L3-10013-R4-r2-f3641337`, has static references but no observed use on this input; its imports remain conservatively preserved. Reached loads include evaluated typing annotations, which are real runtime dependencies even though they do not perform cryptanalysis. `import_use_trace_v2/RESULTS.json` records binding, originating module, line, opcode, and evidence directory.

The original contract's `unused_imports` is not a semantic classifier. It collects module roots and imported members, then subtracts AST Name spellings. Thus `from typing import Tuple` can report `typing` unused even while evaluating `Tuple[int, int]`; `from collections import defaultdict` likewise reports the root unused while calling its member. The transform follows bound names (including aliases), preserves any reference in any scope, string mentions, reflective/dynamic access, nested imports, wildcard/relative imports, mixed used/unused statements, and modules outside a fixed standard-library subset. Whole-statement deletion is recorded as exact before/after lines and old/new SHA-256. It deliberately under-removes. No general semantic equivalence claim follows from AST analysis: only identical observed outputs on the retained inputs are established. Import initialization side effects and unobserved branches remain a limitation.

Execution and provenance: 851 syntax-valid originals plus 128 derivatives were freshly executed using `readiness_revision_20261021/execute_replay.py::sandbox_command`. Only the runtime, program, and public observation are mounted; private state is not exposed to the child. Original `h1r3_reference.py` reconstruction functions and frozen contract schema checks run in the parent, independently of candidate execution. Public reconstruction is compared with private truth. These are cryptographic checks; derivative attribution certificates are not synthesized or claimed accepted. Source/prompt hashes match all retained records; input hashes remain unchanged. All 849 successful original executions emitted one nonblank JSON line; all fresh cryptographic outcomes match the retained predicates. No provider calls occurred.

Reproduce from this directory, using a new output directory for each fresh run:

```
python3 -B -m unittest -v test_transform test_trace > .omo/evidence/tests-final.log 2>&1
python3 -B audit.py --output .omo/evidence/run01 --workers 6 > .omo/evidence/run01.log 2>&1
python3 -B trace_imports.py --run .omo/evidence/run01 --name import_use_trace_v2 --workers 6 > .omo/evidence/trace-run02.log 2>&1
python3 -B finalize.py > .omo/evidence/finalize.log 2>&1
```

The invocations above were actually executed; `run01` already exists and is intentionally protected from overwrite. Change the output and trace names for another run and adjust finalize's selected run if needed. `audit.py` is the runnable full-census/derivative audit. `finalize.py` enriches the complete case ledger and writes stratified census and validation. Every case has command, stdout/stderr hashes, parsed output where present, independent predicate, and exact edit lineage. The one syntax-invalid source has a qualification record and is not represented as executed.

| Criterion / exact scenario | Binary observable | Captured artifact |
|---|---|---|
| Conservative transform and trace identity fixtures | 15 tests pass, exit 0 | `.omo/evidence/tests-final.log` |
| Complete frozen census + isolated originals/derivatives | 852 unique rows, no sandbox errors, 128/128 derivative output equality, exit 0 | `.omo/evidence/run01.log`, `run01/CASE_LEDGER.jsonl`, `run01/SUMMARY.json` |
| Distinguish static from observed import use | 101 traced cases, 100 observed-use cases, 0 output disagreements, exit 0 | `.omo/evidence/trace-run02.log`, `run01/import_use_trace_v2/RESULTS.json` |
| Preserve raw inputs and every population | manifest hashes unchanged, full strata emitted, validation PASS | `run01/input_manifest.json`, `run01/FULL_CENSUS.json`, `run01/VALIDATION.json` |

All `run01/...` shorthand paths above are under `.omo/evidence/`. Input source-policy, prompt, preregistration, program, reference, and output hashes are in the input manifest. Artifact hashes are in `.omo/evidence/MANIFEST.json`.

Instrumentation correction: the first `import_use_trace` attempt observed no opcodes because this Python 3.12 build requires enabling opcode tracing on the caller frame before `sys.settrace`. That trace is retained but invalid for use classification. The corrected `import_use_trace_v2` reruns the entire 101-case scenario and passes a sandboxed alias/annotation/unused/shadowed-binding fixture. No original or derivative execution result depends on the first trace.

Allowed claims: local legacy policy sensitivity; bounded observed unused-import removability; actual-v3 absence of import rejects; explicit cryptographic failure preservation; observed runtime import dependencies. Disallowed claims: universally harmless imports; all legacy rejects are unused imports; all referenced imports are mathematically necessary; local policy sensitivity establishes a new attack, broad model capability, or a causal representation effect; a derivative with correct output has an accepted attribution certificate.
'''
    (HERE / 'REPORT.md').write_text(report)
    files = {str(p.relative_to(HERE)): sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name != 'MANIFEST.json' and p.name != 'finalize.log'}
    write(HERE / '.omo/evidence/MANIFEST.json', files)
    print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    main()
