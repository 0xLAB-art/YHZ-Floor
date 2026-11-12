#!/usr/bin/env python3
"""Stage 3 loopback evidence-ingress gateway.

The Stage 1 attribution pipeline has no network ingress: a certificate bundle
is constructed in-process and handed straight to the aggregator.  This gateway
supplies the missing boundary.  It accepts an untrusted claim bundle over real
HTTP on the loopback interface and hands it to the **frozen** E2A aggregator
for evaluation.

The gateway performs no verification of its own.  It transports bytes, records
what it received, and returns the aggregator's verdict.
"""
from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

STAGE1_ROOT = Path(__file__).resolve().parents[1] / "stage1_e2a"
sys.path.insert(0, str(STAGE1_ROOT))

from e2a.aggregator import Aggregator  # noqa: E402


class _Handler(BaseHTTPRequestHandler):
    """Accepts a claim bundle and returns the aggregator's decision."""

    def log_message(self, *args: Any) -> None:
        return

    def _json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"ok": True, "role": "stage3-evidence-ingress"})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/claim":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        record: dict[str, Any] = {
            "path": self.path,
            "content_length": length,
            "raw_sha256": __import__("hashlib").sha256(raw).hexdigest(),
        }
        try:
            bundle = json.loads(raw)
        except ValueError:
            record["parse_status"] = "NON_JSON"
            self.server.submissions.append(record)
            self._json(400, {"error": "submission is not valid JSON"})
            return
        record["parse_status"] = "OK"
        decision = self.server.aggregator.evaluate(bundle)
        record["decision"] = decision["decision"]
        record["reason"] = decision["reason"]
        record["reason_family"] = decision["reason_family"]
        self.server.submissions.append(record)
        self._json(200, {"decision": decision})


class IngressGateway:
    """A loopback HTTP ingress in front of the frozen E2A aggregator."""

    def __init__(self, bundle_path: Path, policy_path: Path, ledger_path: Path):
        self.submissions: list[dict[str, Any]] = []
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self._server.aggregator = Aggregator(bundle_path, policy_path, ledger_path)
        self._server.submissions = self.submissions
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def port(self) -> int:
        return self._server.server_address[1]

    def __enter__(self) -> "IngressGateway":
        self._thread.start()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)