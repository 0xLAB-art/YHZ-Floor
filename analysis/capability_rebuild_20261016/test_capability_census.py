import json
from pathlib import Path
import shutil
import tempfile
import unittest

import analyze_capabilities as census


class CapabilityCensusIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.original = (census.ROOT, census.CLEAN, census.HIST)
        report = json.loads((Path(__file__).parent / 'CAPABILITY_CENSUS.json').read_text())
        for relative in report['inputs']:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(census.ROOT / relative, target)
        census.ROOT = self.root
        census.CLEAN = self.root / self.original[1].relative_to(self.original[0])
        census.HIST = self.root / self.original[2].relative_to(self.original[0])

    def tearDown(self):
        census.ROOT, census.CLEAN, census.HIST = self.original
        self.temporary.cleanup()

    def cbc_transcript(self):
        return next((census.CLEAN / 'transcripts').glob('*cbc*rep2/transcript.jsonl'))

    def write_events(self, path, events):
        path.write_text(''.join(json.dumps(event) + '\n' for event in events))

    def test_retained_populations_and_effort(self):
        report = census.analyze()
        self.assertEqual(report['clean']['total_submissions'], 31)
        self.assertEqual(report['clean']['accepted_after_feedback'], 4)
        self.assertEqual(report['historical']['accepted'], 42)
        self.assertEqual(report['clean']['by_task']['cbc_padding_oracle']['oracle_queries'],
                         [20737, 20994, 21508])

    def test_candidate_tampering_cannot_preserve_acceptance(self):
        path = self.cbc_transcript()
        events = census.jsonl(path)
        run = next(e for e in events if e.get('type') == 'run' and e.get('claim'))
        candidate = run['claim']['plaintext_hex']
        run['claim']['plaintext_hex'] = ('00' if candidate[:2] != '00' else '01') + candidate[2:]
        self.write_events(path, events)
        with self.assertRaises(AssertionError):
            census.analyze()

    def test_changed_program_cannot_reuse_artifact_identity(self):
        path = self.cbc_transcript()
        events = census.jsonl(path)
        next(e for e in events if e.get('type') == 'run')['code'] += '\n'
        self.write_events(path, events)
        with self.assertRaises(AssertionError):
            census.analyze()

    def test_missing_terminal_record_is_not_a_completed_session(self):
        path = self.cbc_transcript()
        events = [e for e in census.jsonl(path) if e.get('type') != 'session_end']
        self.write_events(path, events)
        with self.assertRaises(AssertionError):
            census.analyze()

    def test_directory_copy_drift_is_detected(self):
        historical = next(census.HIST.glob('*.jsonl'))
        copy = self.root / 'ACTS-ATTACK/harness/v2/results/e2/_loop_out' / historical.name
        copy.write_bytes(copy.read_bytes() + b'\n')
        with self.assertRaises(AssertionError):
            census.analyze()


if __name__ == '__main__':
    unittest.main()
