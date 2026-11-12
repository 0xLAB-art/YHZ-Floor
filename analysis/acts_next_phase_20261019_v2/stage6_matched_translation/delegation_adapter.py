#!/usr/bin/env python3
"""Delegation adapter: the external program that applies the ACTS policy.

This is the *only* part of the in-toto delegated arm that is specific to ACTS.
It is deliberately tiny; what it calls is the frozen ACTS aggregator, whose
source is hash-pinned in the Stage 1 and HEB-2 freeze manifests.  The point of
the measurement is that the upstream model supplies the signature, authority and
threshold machinery, while the *policy* has to be supplied from outside.

Usage:  delegation_adapter.py <certificate.json> <bundle> <policy>
Exit:   0 iff the ACTS contract returns ATTRIBUTED_SUCCESS, 1 otherwise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

STAGE1_ROOT = Path(__file__).resolve().parents[1] / "stage1_e2a"
sys.path.insert(0, str(STAGE1_ROOT))

from e2a.aggregator import DECISION_SUCCESS, Aggregator  # noqa: E402


def main() -> int:
    certificate_path, bundle_path, policy_path = sys.argv[1:4]
    certificate = json.loads(Path(certificate_path).read_text())
    bundle = {"case_id": certificate.get("case_id"), "certificate": certificate}
    aggregator = Aggregator(Path(bundle_path), Path(policy_path), None)
    decision = aggregator.evaluate(bundle)
    print(json.dumps({"decision": decision["decision"], "reason": decision["reason"]},
                     sort_keys=True))
    return 0 if decision["decision"] == DECISION_SUCCESS else 1


if __name__ == "__main__":
    raise SystemExit(main())