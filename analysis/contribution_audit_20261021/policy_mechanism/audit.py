import argparse
import ast
import collections
import concurrent.futures
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / 'h1r3_20261019'
REPLAY = HERE.parents[1] / 'readiness_revision_20261021/execute_replay.py'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + '\n')


def transform(source, allowed):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, [], [], ['syntax']
    nodes = list(ast.walk(tree))
    names = {n.id for n in nodes if isinstance(n, ast.Name)}
    dynamic = sorted({n.id for n in nodes if isinstance(n, ast.Name) and n.id in {
        'eval', 'exec', 'compile', 'globals', 'locals', 'vars', 'dir', 'getattr',
        'setattr', 'delattr', '__import__', 'inspect', 'importlib'}})
    if any(isinstance(n, ast.Attribute) and (n.attr.startswith('__') or n.attr in {'modules', '_getframe'}) for n in nodes):
        dynamic.append('reflection-attribute')
    strings = [n.value for n in nodes if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    imports, edits = [], []
    lines = source.splitlines(keepends=True)
    for node in nodes:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        entries = []
        for alias in node.names:
            module = alias.name if isinstance(node, ast.Import) else node.module or ''
            bound = alias.asname or (alias.name.split('.')[0] if isinstance(node, ast.Import) else alias.name)
            string_mention = any(re.search(r'\b' + re.escape(bound) + r'\b', s) for s in strings)
            eligible_module = module.split('.')[0] in {'hashlib', 'typing', 'collections', 'math', 'itertools', 'functools', 'struct', 'binascii', 'operator', 'statistics', 'string', 'decimal', 'fractions', 're'}
            reasons = []
            if bound in names:
                reasons.append('name-reference-any-scope')
            if string_mention:
                reasons.append('string-reference-uncertain')
            if dynamic:
                reasons.append('dynamic-access-uncertain')
            if node not in tree.body:
                reasons.append('nested-import-uncertain')
            if alias.name == '*' or getattr(node, 'level', 0):
                reasons.append('wildcard-or-relative')
            if not eligible_module:
                reasons.append('module-side-effects-not-qualified')
            entries.append({'module': module, 'binding': bound, 'alias': alias.asname,
                            'line': node.lineno, 'disallowed_legacy': module.split('.')[0] not in allowed,
                            'classification': 'referenced_preserve' if bound in names else ('uncertain_preserve' if reasons else 'conservatively_unused'),
                            'reasons': reasons})
        imports.extend(entries)
        full_line = node.col_offset == 0 and not lines[node.end_lineno - 1][node.end_col_offset:].strip().strip('\n').startswith(';')
        if full_line and all(e['classification'] == 'conservatively_unused' for e in entries) and any(e['disallowed_legacy'] for e in entries):
            old = ''.join(lines[node.lineno - 1:node.end_lineno])
            if ast.get_source_segment(source, node).strip() != old.strip() and not old.strip().startswith(ast.get_source_segment(source, node).strip() + ' #'):
                continue
            edits.append({'start_line': node.lineno, 'end_line': node.end_lineno, 'before': old, 'after': '\n' * (node.end_lineno - node.lineno + 1), 'bindings': [e['binding'] for e in entries]})
    for edit in reversed(edits):
        lines[edit['start_line'] - 1:edit['end_line']] = [edit['after']]
    result = ''.join(lines)
    ast.parse(result)
    return result, edits, imports, dynamic


def execute(program, public, dest, sandbox):
    dest.mkdir(parents=True)
    command = sandbox.sandbox_command(program, public)
    write(dest / 'command.json', command)
    try:
        process = subprocess.run(command, capture_output=True, timeout=22, env={'PATH': '/usr/bin:/bin'}, check=False)
        stdout, stderr = process.stdout, process.stderr
        result = {'returncode': process.returncode, 'status': 'EXECUTED' if process.returncode == 0 else 'EXECUTION_FAILED'}
        if b'bwrap:' in stderr or b'prlimit:' in stderr:
            result['status'] = 'SANDBOX_ERROR'
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        result = {'status': 'EXECUTION_TIMEOUT'}
    (dest / 'stdout.txt').write_bytes(stdout)
    (dest / 'stderr.txt').write_bytes(stderr)
    result['stdout_sha256'], result['stderr_sha256'] = sha(dest / 'stdout.txt'), sha(dest / 'stderr.txt')
    try:
        lines = [s.strip() for s in stdout.decode().splitlines() if s.strip()]
        candidate = json.loads(lines[-1])
        if result['status'] != 'EXECUTED' or not isinstance(candidate, dict):
            raise ValueError()
        write(dest / 'candidate_output.json', candidate)
        result['candidate'] = candidate
        result['single_json_object_stdout'] = len(lines) == 1
    except (ValueError, IndexError):
        if result['status'] == 'EXECUTED':
            result['status'] = 'OUTPUT_SCHEMA_INVALID'
    write(dest / 'execution.json', result)
    return result


def check(row, case, execution, reference, contract):
    payload = json.loads((case / 'public_instance.json').read_text())
    private = json.loads((case / 'private_state.json').read_text())
    bundle = json.loads((case / 'reference_bundle.json').read_text())
    public = reference.decode_public(row['family'], payload)
    recon = reference.reconstruct_xor(public) if row['family'] == 'XOR_Keystream_Reuse' else reference.reconstruct_ecdsa(public)
    candidate = execution.get('candidate', {})
    if row['kind'] == 'c0':
        predicate = not recon['sufficient'] and candidate.get('status') == 'UNDERDETERMINED'
        schema = isinstance(candidate.get('reason'), str) and candidate.get('status') == 'UNDERDETERMINED'
        sufficiency = not recon['sufficient']
    elif row['family'] == 'XOR_Keystream_Reuse':
        predicate = candidate.get('plaintext') == private['hidden']['plaintext_target']
        sufficiency = recon['sufficient'] and recon['plaintext'] == private['hidden']['plaintext_target']
        schema, _ = contract.check_output_schema(row['family'], False, candidate, public['target'][2])
    else:
        predicate = candidate.get('d') == private['hidden']['d'] and (not bundle['require_k'] or candidate.get('k') == private['hidden']['k'])
        sufficiency = recon['sufficient'] and recon['d'] == private['hidden']['d']
        schema, _ = contract.check_output_schema(row['family'], bundle['require_k'], candidate, None)
    return {'cryptographic_predicate': bool(predicate), 'reference_reconstruction_valid': bool(sufficiency),
            'schema_ok': schema, 'scope': 'cryptographic/output checks only; no derivative attribution certificate acceptance'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(HERE):
        raise ValueError('output outside assignment')
    output.mkdir(parents=True, exist_ok=False)
    contract = load(ROOT / 'h1r3_contract.py', 'audit_contract')
    reference = load(ROOT / 'h1r3_reference.py', 'audit_reference')
    sandbox = load(REPLAY, 'audit_sandbox')
    rows = [json.loads(s) for s in (ROOT / 'runs/confirmatory/results.jsonl').read_text().splitlines()]
    assert len(rows) == len({r['session_id'] for r in rows}) == 852
    assert collections.Counter(r['kind'] for r in rows) == {'primary': 768, 'noise': 64, 'c0': 20}
    paths = [ROOT / f for f in ('h1r3_contract.py', 'h1r3_core.py', 'h1r3_reference.py', 'H1R3_PREREGISTRATION.md', 'H1R3_AMENDMENT_01.md', 'runs/confirmatory/results.jsonl')] + [REPLAY]
    for row in rows:
        case = ROOT / 'runs/confirmatory/sessions' / row['session_id']
        paths.extend(case / name for name in ('candidate.py', 'public_instance.json', 'private_state.json', 'reference_bundle.json', 'prompt.txt', 'session_result.json'))
        paths.extend(p for p in (case / 'candidate_output.json', case / 'executor_stdout.txt', case / 'executor_stderr.txt') if p.exists())
    before = {str(p): sha(p) for p in paths}
    write(output / 'input_manifest.json', before)
    ledger = []
    tasks = []
    for row in rows:
        case = ROOT / 'runs/confirmatory/sessions' / row['session_id']
        source = (case / 'candidate.py').read_text()
        prompt = (case / 'prompt.txt').read_text()
        listed = re.search(r'^Allowed imports: (.*)\.$', prompt, re.M).group(1).split(', ')
        assert set(listed) == contract.POLICIES['v3']
        v3, legacy = contract.qualify_source(source, 'v3'), contract.qualify_source(source, 'legacy')
        changed, edits, imports, uncertainties = transform(source, contract.POLICIES['legacy'])
        rec = {k: row[k] for k in ('session_id', 'kind', 'arm', 'level', 'family', 'seed', 'replicate_index')}
        rec.update({'source_sha256': sha(case / 'candidate.py'), 'source_path': str(case / 'candidate.py'),
                    'source_hash_matches_record': sha(case / 'candidate.py') == row['source_sha256'],
                    'prompt_sha256': sha(case / 'prompt.txt'), 'prompt_hash_matches_record': sha(case / 'prompt.txt') == row['prompt_sha256'],
                    'prompt_allowed_modules': listed, 'historical_execution_status': row['execution_status'],
                    'historical_predicate': row['reference']['cryptographic_predicate'],
                    'v3': v3, 'legacy': legacy, 'imports': imports, 'uncertainties': uncertainties,
                    'edits': edits, 'derivative_legacy': contract.qualify_source(changed, 'legacy'),
                    'legacy_disallowed_but_prompt_allowed': [e for e in imports if e['disallowed_legacy'] and e['module'].split('.')[0] in listed]})
        dest = output / 'cases' / row['session_id']
        dest.mkdir(parents=True)
        if v3['qualified']:
            tasks.append((len(ledger), 'original', case / 'candidate.py', case, row, dest / 'original'))
        else:
            rec['original'] = {'status': 'SOURCE_PARSE_REJECTED' if v3['status'] == 'SOURCE_PARSE_REJECTED' else 'SOURCE_POLICY_REJECTED', 'cryptographic_predicate': False}
        if edits:
            (dest / 'derivative.py').write_text(changed)
            write(dest / 'edits.json', edits)
            rec['derivative_sha256'] = sha(dest / 'derivative.py')
            assert contract.qualify_source(changed, 'v3')['qualified']
            tasks.append((len(ledger), 'derivative', dest / 'derivative.py', case, row, dest / 'derivative'))
        ledger.append(rec)
    def run(task):
        idx, variant, program, case, row, dest = task
        result = execute(program, case / 'public_instance.json', dest, sandbox)
        result.update(check(row, case, result, reference, contract))
        retained = case / 'candidate_output.json'
        result['matches_retained_output'] = result.get('candidate') == (json.loads(retained.read_text()) if retained.exists() else None)
        result['artifact_dir'] = str(dest)
        write(dest / 'result.json', result)
        return idx, variant, result
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for idx, variant, result in pool.map(run, tasks):
            ledger[idx][variant] = result
    for rec in ledger:
        rec['legacy_rejected_correct'] = not rec['legacy']['qualified'] and rec['original']['cryptographic_predicate']
        rec['unused_removal_rescues_legacy_qualification'] = not rec['legacy']['qualified'] and rec['derivative_legacy']['qualified']
        rec['legacy_class'] = ('qualified' if rec['legacy']['qualified'] else 'syntax' if rec['legacy']['status'] == 'SOURCE_PARSE_REJECTED' else 'unused_only_removable' if rec['unused_removal_rescues_legacy_qualification'] else 'referenced_import_present' if any(e['disallowed_legacy'] and e['classification'] == 'referenced_preserve' for e in rec['imports']) else 'uncertain_or_other_reject')
        if 'derivative' in rec:
            rec['derivative_same_output_as_original'] = rec['derivative'].get('candidate') == rec['original'].get('candidate')
        write(output / 'cases' / rec['session_id'] / 'case.json', rec)
    (output / 'CASE_LEDGER.jsonl').write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in ledger))
    strata = []
    for keys in sorted({(r['kind'], r['arm'], r['level'], r['family']) for r in ledger}):
        group = [r for r in ledger if (r['kind'], r['arm'], r['level'], r['family']) == keys]
        strata.append(dict(zip(('kind', 'arm', 'level', 'family'), keys)) | {
            'n': len(group), 'legacy_classes': dict(collections.Counter(r['legacy_class'] for r in group)),
            'v3_import_rejects': sum(any(v['rule'].startswith('disallowed-import') for v in r['v3']['violations']) for r in group),
            'fresh_correct': sum(r['original']['cryptographic_predicate'] for r in group),
            'legacy_rejected_correct': sum(r['legacy_rejected_correct'] for r in group),
            'derivatives': sum('derivative' in r for r in group),
            'rescued_legacy_qualification': sum(r['unused_removal_rescues_legacy_qualification'] for r in group),
            'rescued_legacy_correct': sum(r['unused_removal_rescues_legacy_qualification'] and r.get('derivative', {}).get('cryptographic_predicate', False) for r in group)})
    immutable = before == {str(p): sha(p) for p in paths}
    summary = {'sessions': len(rows), 'populations': dict(collections.Counter(r['kind'] for r in ledger)),
               'original_statuses': dict(collections.Counter(r['original']['status'] for r in ledger)),
               'legacy_classes': dict(collections.Counter(r['legacy_class'] for r in ledger)),
               'derivatives_executed': sum('derivative' in r for r in ledger),
               'derivative_output_changes': sum(not r['derivative_same_output_as_original'] for r in ledger if 'derivative' in r),
               'source_hash_mismatches': sum(not r['source_hash_matches_record'] for r in ledger),
               'prompt_hash_mismatches': sum(not r['prompt_hash_matches_record'] for r in ledger),
               'predicate_disagreements_with_retained': sum(r['original']['cryptographic_predicate'] != r['historical_predicate'] for r in ledger),
               'sandbox_errors': sum(r[v]['status'] in {'SANDBOX_ERROR', 'EXECUTION_TIMEOUT'} for r in ledger for v in ('original', 'derivative') if v in r),
               'input_files_unchanged': immutable, 'strata': strata}
    write(output / 'SUMMARY.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'strata'}, indent=2))
    assert immutable and not summary['sandbox_errors'] and not summary['source_hash_mismatches'] and not summary['prompt_hash_mismatches'] and not summary['derivative_output_changes'] and not summary['predicate_disagreements_with_retained']


if __name__ == '__main__':
    main()
