import json
import socket
import subprocess
import tempfile
import unittest
from pathlib import Path

import execute_replay


class ExecutionSandboxTests(unittest.TestCase):
    def test_only_public_input_is_visible_and_readonly(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            secret = root / "unmounted_secret.txt"
            secret.write_text("outside-the-sandbox")
            public = root / "public.json"
            public.write_text(json.dumps({"visible": True}))
            code = root / "probe.py"
            code.write_text(
                "import json,os,sys\n"
                "readable=json.load(open(sys.argv[1]))['visible']\n"
                "try:\n open(sys.argv[1],'w'); writable=True\n"
                "except OSError:\n writable=False\n"
                f"print(json.dumps({{'public':readable,'writable':writable,'secret_visible':os.path.exists({str(secret)!r})}}))\n"
            )
            result = subprocess.run(execute_replay.sandbox_command(code, public), capture_output=True, timeout=20, check=True)
            self.assertEqual(json.loads(result.stdout), {"public": True, "writable": False, "secret_visible": False})

    def test_host_loopback_listener_is_not_reachable(self):
        with tempfile.TemporaryDirectory() as temporary, socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            port = listener.getsockname()[1]
            root = Path(temporary)
            public = root / "public.json"
            public.write_text("{}")
            code = root / "probe.py"
            code.write_text(
                "import json,socket\n"
                f"try:\n socket.create_connection(('127.0.0.1',{port}),timeout=1); reachable=True\n"
                "except OSError:\n reachable=False\n"
                "print(json.dumps({'host_reachable':reachable}))\n"
            )
            result = subprocess.run(execute_replay.sandbox_command(code, public), capture_output=True, timeout=20, check=True)
            self.assertFalse(json.loads(result.stdout)["host_reachable"])


if __name__ == "__main__":
    unittest.main()
