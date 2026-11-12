#!/usr/bin/env python3
"""Reserved-secret oracle, in a separate process.

The card's ``oracle_spec`` for this target is ``static_claim``: the SECRET is
reserved in the oracle process, the service container discloses it only under
the exploited misuse, and success is ``claimed secret_hex == reserved secret``.

This process holds the reserved secret, shares no memory with the harness, and
answers one grading request per connection.  It never learns the attacker's
program or the service's token key.
"""
from __future__ import annotations

import json
import os
import socket
import socketserver
import sys
from pathlib import Path

SOCKET_PATH = Path(sys.argv[1])
RESERVED_SECRET_HEX = os.environ["RESERVED_SECRET_HEX"]


class _Handler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        raw = self.request.recv(65536)
        try:
            request = json.loads(raw)
        except ValueError:
            self.request.sendall(json.dumps({"success": False, "failure_reason": "bad_request"}).encode())
            return
        claimed = request.get("secret_hex")
        success = isinstance(claimed, str) and claimed.lower() == RESERVED_SECRET_HEX.lower()
        verdict = {
            "success": success,
            "observed_value": claimed,
            "expected_relation": "==",
            "failure_reason": None if success else "claim_does_not_match_reserved_secret",
            "oracle_queries": 1,
        }
        self.request.sendall(json.dumps(verdict).encode())


def main() -> int:
    if SOCKET_PATH.exists():
        SOCKET_PATH.unlink()
    server = socketserver.UnixStreamServer(str(SOCKET_PATH), _Handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())