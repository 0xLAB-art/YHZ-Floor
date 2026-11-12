import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from audit import HERE, REPLAY, load


class TraceTests(unittest.TestCase):
    def test_runtime_identity_and_nonuse(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            dest = Path(temporary)
            program = dest / 'test.py'
            public = dest / 'input.json'
            public.write_text('{}')
            program.write_text('import hashlib as unused\nfrom typing import Tuple as T\nfrom collections import Counter as C\nimport math as shadow\ndef f(shadow):\n    return shadow\ndef g() -> T[int, int]:\n    return 1, 2\nprint(C([1, 1])[1] + f(2))\n')
            command = load(REPLAY, 'test_sandbox').sandbox_command(program, public)
            command[-2:] = ['-c', (HERE / 'trace_wrapper.py').read_text(), '/case/candidate.py', '/case/public_instance.json']
            process = subprocess.run(command, capture_output=True, timeout=22)
            self.assertEqual(process.returncode, 0, process.stderr)
            uses = json.loads(process.stderr.rsplit(b'IMPORT_USE_AUDIT:', 1)[1])
            self.assertEqual({u[0] for u in uses}, {'T', 'C'})
            self.assertEqual(process.stdout, b'4\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
