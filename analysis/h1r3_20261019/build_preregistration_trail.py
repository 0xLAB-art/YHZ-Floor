#!/usr/bin/env python3
"""Derive the H1-R3 preregistration trail from the retained records.

The manuscript calls H1-R3 a preregistered study.  This script produces the
evidence a reviewer needs to evaluate that claim rather than accept it: the
freeze timestamp and the digests the freeze recorded, the timestamps of the
provider requests and responses that bracket the campaign, and the digests of
the two amendments that followed the freeze.

It reads only retained records and writes only a small derived summary.  It
makes no provider call, re-runs no session, and contacts no target.

Usage:  python3 -B build_preregistration_trail.py [--root <dir>] [--out <file>]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iso(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=HERE,
                    help="the H1-R3 analysis directory")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    root = args.root.resolve()
    out = args.out or (root / "H1R3_PREREGISTRATION_TRAIL.json")

    freeze = json.loads((root / "H1R3_FREEZE.json").read_text())
    amend1 = json.loads((root / "H1R3_FREEZE_AMENDMENT_01.json").read_text())
    amend2 = json.loads((root / "H1R3_FREEZE_AMENDMENT_02.json").read_text())

    requests, responses, sessions = [], [], 0
    for meta in sorted((root / "runs/confirmatory/sessions").glob("*/provider_metadata.json")):
        d = json.loads(meta.read_text())
        requests.append(d["request_started"])
        responses.append(d["response_finished"])
        sessions += 1
    if not requests:
        print("no retained provider metadata found", flush=True)
        return 2

    freeze_ts = dt.datetime.fromisoformat(freeze["frozen_utc"]).timestamp()
    amend1_ts = dt.datetime.fromisoformat(amend1["utc"]).timestamp()
    amend2_ts = dt.datetime.fromisoformat(
        amend2.get("utc") or amend2["frozen_utc"]).timestamp()
    first_request = min(requests)
    last_response = max(responses)

    # The current digest of every file the freeze and the amendments cover.
    covered = sorted(set(freeze["implementation_sha256"]) | set(amend1["all_analysis_hashes"]))
    current = {}
    for rel in covered:
        p = root / rel
        if p.is_file():
            current[rel] = sha256(p)

    # Which recorded digest applies to each file at each stage.
    pre = freeze["implementation_sha256"]
    post = amend1["all_analysis_hashes"]
    changed_by_amendment = sorted(
        rel for rel in pre
        if rel in post and pre[rel] != post[rel])

    trail = {
        "schema": "h1r3-preregistration-trail/1",
        "study": "H1-R3",
        "boundary": (
            "Derived from the retained freeze and amendment manifests and the "
            "per-session provider metadata. The 852 session directories are not "
            "part of the published package, so the request and response "
            "timestamps cannot be re-derived from the package alone; the "
            "digests below can, because the files they cover are shipped "
            "byte for byte."
        ),
        "sessions": sessions,
        "freeze": {
            "frozen_utc": freeze["frozen_utc"],
            "status": freeze["status"],
            "schedule_sessions": freeze["schedule_sessions"],
            "schedule_sha256": freeze["schedule_sha256"],
            "implementation_sha256": freeze["implementation_sha256"],
        },
        "campaign_window": {
            "earliest_request_started_utc": iso(first_request),
            "latest_response_finished_utc": iso(last_response),
            "seconds_from_freeze_to_first_request": round(first_request - freeze_ts, 3),
            "seconds_from_freeze_to_last_response": round(last_response - freeze_ts, 3),
        },
        "amendments": [
            {
                "id": "H1R3_FREEZE_AMENDMENT_01",
                "utc": amend1["utc"],
                "status": amend1["status"],
                "confirmatory_results_inspected_before_amendment":
                    amend1["confirmatory_results_inspected_before_amendment"],
                "amended_files": amend1["amended_files"],
                "scope_note": (
                    "Made after the campaign started and before any confirmatory "
                    "outcome was read or analysed; the hypothesis, estimand, "
                    "margin and allocation were unchanged."
                ),
            },
            {
                "id": "H1R3_FREEZE_AMENDMENT_02",
                "utc": amend2.get("utc") or amend2["frozen_utc"],
                "status": amend2["status"],
                "purpose": amend2["purpose"],
                "scope": amend2["scope"],
            },
        ],
        "ordering_checks": {
            "freeze_precedes_first_request": freeze_ts < first_request,
            "freeze_precedes_amendment_01": freeze_ts < amend1_ts,
            "amendment_01_precedes_last_response": amend1_ts < last_response,
            "amendment_02_at_same_time_as_01": amend2_ts == amend1_ts,
        },
        "files_changed_by_amendment_01": changed_by_amendment,
        "current_sha256": current,
        "digest_stages": {
            "pre_amendment": {r: pre[r] for r in changed_by_amendment if r in pre},
            "post_amendment": {r: post.get(r) for r in changed_by_amendment},
        },
    }
    out.write_text(json.dumps(trail, indent=2, sort_keys=True) + "\n")
    print("wrote %s" % out)
    print("  sessions=%d freeze=%s first_request=%s (+%.1fs) checks=%s"
          % (sessions, freeze["frozen_utc"], iso(first_request),
             first_request - freeze_ts,
             all(trail["ordering_checks"].values())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())