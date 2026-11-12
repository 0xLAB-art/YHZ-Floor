import argparse
import concurrent.futures
import json
import subprocess
from pathlib import Path
from audit import HERE, REPLAY, ROOT, load, sha, write

WRAPPER = (HERE / 'trace_wrapper.py').read_text()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--name', default='import_use_trace')
    args = parser.parse_args()
    run = args.run.resolve()
    assert run.is_relative_to(HERE)
    assert Path(args.name).name == args.name
    output = run / args.name
    output.mkdir()
    (output / 'wrapper.py').write_text(WRAPPER)
    sandbox = load(REPLAY, 'trace_sandbox')
    rows = [json.loads(s) for s in (run / 'CASE_LEDGER.jsonl').read_text().splitlines()]
    selected = [r for r in rows if any(i['classification'] == 'referenced_preserve' and i['disallowed_legacy'] for i in r['imports'])]
    def execute(row):
        case = ROOT / 'runs/confirmatory/sessions' / row['session_id']
        dest = output / row['session_id']
        dest.mkdir()
        command = sandbox.sandbox_command(case / 'candidate.py', case / 'public_instance.json')
        command[-2:] = ['-c', WRAPPER, '/case/candidate.py', '/case/public_instance.json']
        write(dest / 'command.json', command)
        process = subprocess.run(command, capture_output=True, timeout=22, env={'PATH': '/usr/bin:/bin'}, check=False)
        (dest / 'stdout.txt').write_bytes(process.stdout)
        (dest / 'stderr.txt').write_bytes(process.stderr)
        marker = b'IMPORT_USE_AUDIT:'
        uses = json.loads(process.stderr.rsplit(marker, 1)[1]) if marker in process.stderr else []
        candidate = json.loads(process.stdout.decode().splitlines()[-1]) if process.returncode == 0 else None
        result = {k: row[k] for k in ('session_id', 'kind', 'arm', 'level', 'family')}
        result.update({'returncode': process.returncode, 'observed_loaded_import_bindings': uses,
                       'source_sha256': sha(case / 'candidate.py'),
                       'same_output_as_uninstrumented': candidate == row['original'].get('candidate'),
                       'scope': 'actual LOAD opcode reached with imported-object identity; observation is not branch coverage proof',
                       'artifact_dir': str(dest)})
        write(dest / 'result.json', result)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(execute, selected))
    write(output / 'RESULTS.json', results)
    summary = {'cases': len(results), 'with_observed_import_use': sum(bool(r['observed_loaded_import_bindings']) for r in results),
               'nonzero_returncodes': sum(r['returncode'] != 0 for r in results),
               'output_disagreements': sum(not r['same_output_as_uninstrumented'] for r in results)}
    write(output / 'SUMMARY.json', summary)
    print(json.dumps(summary, indent=2))
    assert not summary['nonzero_returncodes'] and not summary['output_disagreements']


if __name__ == '__main__':
    main()
