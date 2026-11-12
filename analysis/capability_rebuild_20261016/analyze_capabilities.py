import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLEAN = ROOT / 'sp2027/agent-eval/runs_r1_clean_capture_first_v4_claude46_20261014_02'
HIST = ROOT / 'ACTS-ATTACK/harness/v3/results/e2/_loop_out'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def analyze():
    inputs = {}

    def retain(path):
        inputs[str(path.relative_to(ROOT))] = digest(path)

    clean = []
    for path in sorted(CLEAN.glob('q*.json')):
        retain(path)
        record = json.loads(path.read_text())
        transcript = CLEAN / 'transcripts' / record['run_id'] / 'transcript.jsonl'
        retain(transcript)
        events = jsonl(transcript)
        runs = [e for e in events if e.get('type') == 'run']
        turns = [e for e in events if e.get('type') == 'llm_turn']
        endings = [e for e in events if e.get('type') == 'session_end']
        assert len(endings) == 1
        accepted = [e for e in runs if (e.get('verdict') or {}).get('verdict') == 'success']
        assert bool(accepted) == record['oracle']['verdict']['success']
        assert len(runs) == record['session']['attempts']
        assert len(turns) == record['session']['turns']
        assert endings[0]['queries'] == record['session']['queries']
        assert (endings[0].get('verdict') or {}) == (runs[-1].get('verdict') or {})
        submitted = {hashlib.sha256(e['code'].encode()).hexdigest() for e in runs}
        artifact_hashes = {a['sha256'] for a in record['artifacts']}
        assert submitted <= artifact_hashes
        successes = []
        for event in accepted:
            verdict = event['verdict']
            claim = event['claim']
            if 'oracle_queries_observed' in verdict:
                assert verdict['oracle_queries_observed'] == record['session']['queries']
            if 'expected_sha256' in verdict:
                field = 'plaintext2_hex' if 'plaintext2_hex' in claim else 'plaintext_hex'
                candidate = bytes.fromhex(claim[field])
                if len(candidate) == 80:
                    assert candidate[-16:] == bytes([16]) * 16
                    candidate = candidate[:-16]
                assert hashlib.sha256(candidate).hexdigest() == verdict['expected_sha256']
                relation = 'candidate_digest_matches_reserved_plaintext_digest'
            else:
                assert verdict['key_matches'] and verdict['signature_valid']
                relation = 'retained_oracle_checks_key_match_and_challenge_signature'
            successes.append({'attempt': event['attempt'], 'relation': relation,
                              'code_sha256': hashlib.sha256(event['code'].encode()).hexdigest()})
        clean.append({'run_id': record['run_id'], 'task': record['task_card']['task_id'],
                      'status': record['session']['status'], 'attempts': len(runs),
                      'model_turns': len(turns), 'oracle_queries': record['session']['queries'],
                      'first_submission_accepted': bool(accepted and accepted[0]['attempt'] == 1),
                      'nonzero_exit_submissions': sum(e['exit'] != 0 for e in runs),
                      'accepted_relations': successes,
                      'oracle_implementation_sha256': record['oracle']['implementation_sha256']})
    assert len(clean) == len({r['run_id'] for r in clean}) == 12
    clean_tasks = {}
    for task in sorted({r['task'] for r in clean}):
        rows = [r for r in clean if r['task'] == task]
        clean_tasks[task] = {'sessions': len(rows), 'accepted': sum(bool(r['accepted_relations']) for r in rows),
                             'first_submission_accepted': sum(r['first_submission_accepted'] for r in rows),
                             'attempts': [r['attempts'] for r in rows],
                             'oracle_queries': sorted(r['oracle_queries'] for r in rows),
                             'nonzero_exit_submissions': sum(r['nonzero_exit_submissions'] for r in rows)}
    historical = []
    for path in sorted(HIST.glob('*.jsonl')):
        retain(path)
        copy = ROOT / 'ACTS-ATTACK/harness/v2/results/e2/_loop_out' / path.name
        retain(copy)
        assert digest(path) == digest(copy)
        events = jsonl(path)
        ends = [e for e in events if e.get('type') == 'session_end']
        assert len(ends) == 1
        end = ends[0]
        verdict = end.get('verdict') or {}
        success = verdict.get('verdict') == 'success'
        if success:
            assert verdict.get('match') is True
            runs = [e for e in events if e.get('type') == 'run' and e.get('verdict') == verdict]
            assert runs and runs[-1].get('claim')
            claim = runs[-1]['claim']
            fields = [f for f in ('plaintext_hex', 'plaintext2_hex', 'secret_hex') if f in claim]
            assert len(fields) == 1
            assert hashlib.sha256(bytes.fromhex(claim[fields[0]])).hexdigest() == verdict['expected_sha256']
        historical.append({'path': str(path.relative_to(ROOT)), 'condition': end['condition'],
                           'model_label': end['model'], 'rep': end['rep'],
                           'verdict': verdict.get('verdict', 'no_verdict'),
                           'accepted_run_claim_present': success,
                           'llm_turns': sum(e.get('type') == 'llm_turn' for e in events)})
    hist_tasks = defaultdict(Counter)
    for row in historical:
        hist_tasks[row['condition']][row['verdict']] += 1
    for path in [ROOT / 'main.tex', ROOT / 'ACTS-ATTACK/results/ACTS_RESULTS_FINAL.json',
                 ROOT / 'ACTS-ATTACK/data/cv7_spread_result.json',
                 ROOT / 'ACTS-ATTACK/data/full_key_recovery.json',
                 ROOT / 'ACTS-ATTACK/harness/v3/oracle.py',
                 ROOT / 'ACTS-ATTACK/harness/v3/prompts.py',
                 ROOT / 'sp2027/pre-registration/cards/rc4_keystream_reuse.json']:
        retain(path)
    oracle_hash = digest(ROOT / 'ACTS-ATTACK/harness/v3/oracle.py')
    assert all(r['oracle_implementation_sha256'] == oracle_hash for r in clean)
    assert len(historical) == 74
    return {'scope': 'Fixed retained populations; descriptive counts, no new provider experiment or executed agent code.',
            'clean': {'sessions': clean, 'by_task': clean_tasks,
                      'total_submissions': sum(r['attempts'] for r in clean),
                      'first_submission_accepted': sum(r['first_submission_accepted'] for r in clean),
                      'accepted_after_feedback': sum(bool(r['accepted_relations']) and not r['first_submission_accepted'] for r in clean)},
            'historical': {'sessions': historical, 'by_task': dict(hist_tasks),
                           'accepted': sum(r['verdict'] == 'success' for r in historical),
                           'copies_are_not_additional_sessions': True,
                           'not_pooled_with_legacy_54_or_clean_12': True},
            'inputs': inputs}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        retained = json.loads(args.verify.read_text())
        if result != retained:
            raise ValueError('Capability census or pinned inputs differ from the retained report')
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'clean': result['clean']['by_task'],
                      'first_submission_accepted': result['clean']['first_submission_accepted'],
                      'accepted_after_feedback': result['clean']['accepted_after_feedback'],
                      'historical': result['historical']['by_task'], 'pinned_inputs': len(result['inputs'])}, indent=2))
