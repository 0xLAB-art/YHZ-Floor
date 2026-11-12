#!/usr/bin/env python3
"""Separate trusted reference adjudicator for deterministic Stage 1 fixtures.

It is intentionally not imported by the blind validator. It reads the private
truth bundle supplied by the runner and emits the adjudicated expected status.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path


def main() -> int:
    bundle = json.loads(Path(sys.argv[1]).read_text())
    expected = bundle["expected_reference_verdict"]
    return print(json.dumps({"reference_verdict": expected, "truth_source": "private-fixture-bundle"})) or 0


if __name__ == "__main__":
    raise SystemExit(main())