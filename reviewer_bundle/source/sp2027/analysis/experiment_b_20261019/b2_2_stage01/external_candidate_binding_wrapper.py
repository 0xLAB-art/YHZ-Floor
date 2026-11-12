#!/usr/bin/env python3
"""B2-2 external candidate-to-execution binding wrapper.

This is deliberately outside the frozen Stage01 validator/reference verifier.
It does not modify or monkey-patch either component. It checks only the
additional semantic field used by the B2-2 constructed cases:

    execution_trace.candidate_sha256 == certificate.agent_artifact.sha256

The wrapper separately verifies certificate-declared outer evidence hashes so
that a semantic mismatch is not confused with stale/corrupt evidence bytes.
If the trace has no candidate_sha256 field, the result is INCONCLUSIVE rather
than an assumed rejection: the original Stage01 schema did not require it.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(status: str, reason: str, **extra) -> int:
    out = {"system": "external-candidate-binding-wrapper",
           "status": status, "reason": reason}
    out.update(extra)
    print(json.dumps(out, sort_keys=True))
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        return emit("INCONCLUSIVE", "usage: wrapper certificate.json")
    cert_path = Path(sys.argv[1])
    try:
        cert = json.loads(cert_path.read_text())
        evidence = {item["kind"]: item for item in cert["evidence"]}
        trace_item = evidence["execution_trace"]
        trace_path = Path(trace_item["path"])
        candidate_path = Path(cert["agent_artifact"]["path"])
        declared_candidate_sha = cert["agent_artifact"]["sha256"]
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        return emit("INCONCLUSIVE", f"malformed:{type(exc).__name__}")

    # Outer evidence integrity is evaluated before semantic binding.
    actual_trace_sha = sha(trace_path) if trace_path.is_file() else None
    if actual_trace_sha != trace_item.get("sha256"):
        return emit("REJECT", "stale-or-corrupt-evidence-sha",
                    evidence_kind="execution_trace",
                    declared_sha256=trace_item.get("sha256"),
                    actual_sha256=actual_trace_sha)
    actual_candidate_sha = sha(candidate_path) if candidate_path.is_file() else None
    if actual_candidate_sha != declared_candidate_sha:
        return emit("REJECT", "candidate-pointer-hash",
                    declared_sha256=declared_candidate_sha,
                    actual_sha256=actual_candidate_sha)

    try:
        trace = json.loads(trace_path.read_text())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return emit("INCONCLUSIVE", f"trace-parse:{type(exc).__name__}")

    trace_candidate_sha = trace.get("candidate_sha256")
    if trace_candidate_sha is None:
        return emit("INCONCLUSIVE", "trace-has-no-candidate-hash")
    if trace_candidate_sha != declared_candidate_sha:
        return emit("REJECT", "semantic-candidate-execution-mismatch",
                    trace_candidate_sha256=trace_candidate_sha,
                    certificate_candidate_sha256=declared_candidate_sha)
    return emit("ACCEPT", "candidate-execution-bound",
                trace_candidate_sha256=trace_candidate_sha,
                certificate_candidate_sha256=declared_candidate_sha)


if __name__ == "__main__":
    raise SystemExit(main())
