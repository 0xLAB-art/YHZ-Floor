#!/usr/bin/env python3
"""Criterion-5 outcome record — Amendment 3 (DRAFT 2026-11-05).

Joins the census worklist (all 16 offline candidates) with the executed
reference-solve log, applies the pre-registered criterion-5 gate (offline,
stdlib-only, admissible under the declared arm, within the fixed 1600-token
program budget), and writes:

  criterion5_outcomes.json     machine-readable per-candidate disposition
  CRITERION5_VERIFICATION.md   the human table + reasons

No model call, no session, $0.  Deterministic: same inputs -> byte-identical
outputs.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSUS = HERE.parent / "census_nyu_crypto.json"
RUN_LOG = HERE / "reference_solve_run.jsonl"
OUT_JSON = HERE.parent / "criterion5_outcomes.json"
OUT_MD = HERE.parent / "CRITERION5_VERIFICATION.md"

# disposition overrides; everything else follows from the run log
FAILURES = {
    "test/2018/CSAW-Quals/crypto/collusion": (
        "FAIL_CRITERION_5",
        "the declared artifacts' message body is a 31-byte GCM payload "
        "(15-byte plaintext; the release's generator encrypts the literal "
        "'mission payload'), while the pinned answer is a 48-byte string — "
        "the answer cannot be the decrypted message, and no derivation rule "
        "from the declared files produces it (recorded as a selection "
        "outcome, not a claim about the benchmark)"),
    "development/2013/CSAW-Finals/crypto/stfu": (
        "FAIL_CRITERION_5",
        "the decoded artifact (LFSR keystream reproduced from the release "
        "header) is a 25,300-byte printable visual rendering of the answer; "
        "reading it requires a human viewer, and no admissible programmatic "
        "derivation was found within the registered budget"),
}

NOT_REACHED_REASON = (
    "not reached: the pre-registered verification schedule stopped once the "
    "quorum was exceeded; no eligibility claim is made")

BUDGET_EXCLUDED = {
    "2019q-cry-des2bites": (
        "the reference solve reproduces the pinned answer byte-exactly under "
        "the declared arm, but the pure-stdlib DES implementation it needs is "
        "8191 source chars (~2047+ tokens at a conservative 4 chars/token), "
        "above the registered 1600-token program budget; excluded "
        "conservatively from grid membership"),
}


def main():
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    runs = {}
    for line in RUN_LOG.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        runs[record["task_id"]] = record

    qualified, excluded, failed, not_reached = [], [], [], []
    for row in census["records"]:
        if row.get("disposition") != "OFFLINE_CANDIDATE":
            continue
        path = row["path_rel"]
        task_id = row.get("manifest_id")
        name = row["name"]
        if path in FAILURES:
            status, reason = FAILURES[path]
            failed.append({"task_id": task_id, "name": name, "path_rel": path,
                           "status": status, "reason": reason})
            continue
        run = runs.get(task_id)
        if run is None:
            not_reached.append({"task_id": task_id, "name": name,
                                "path_rel": path, "status": "NOT_REACHED",
                                "reason": NOT_REACHED_REASON})
            continue
        entry = {
            "task_id": task_id,
            "name": name,
            "path_rel": path,
            "status": run["verdict"],
            "solver": run["solver"],
            "solver_sha256": run["solver_sha256"],
            "solver_chars": run["solver_chars"],
            "est_tokens_chars_div4": run["est_tokens_chars_div4"],
            "within_1600_token_budget_estimate":
                run["within_1600_token_budget_estimate"],
            "declared_arm": run["declared_arm"]["status"],
            "stress_arm": run["stress_arm"]["status"],
            "answer_bytes_in_solver_source":
                run["answer_bytes_in_solver_source"],
            "output_equals_pinned_answer": run["verdict"] == "MATCH",
        }
        if task_id in BUDGET_EXCLUDED:
            entry["status"] = "VERIFIED_BUDGET_EXCLUDED"
            entry["reason"] = BUDGET_EXCLUDED[task_id]
            excluded.append(entry)
        elif (entry["output_equals_pinned_answer"]
              and entry["declared_arm"] == "QUALIFIED"
              and entry["within_1600_token_budget_estimate"]
              and not entry["answer_bytes_in_solver_source"]):
            qualified.append(entry)
        else:
            entry["status"] = "FAIL_CRITERION_5"
            failed.append(entry)

    qualified.sort(key=lambda e: e["task_id"])
    payload = {
        "schema": "external-admission-amend3-criterion5/1-draft",
        "date": "2026-11-05",
        "protocol": "PHASE2-EXTERNAL-ADMISSION-AMEND3-v1",
        "pinned_archive": census["pinned_archive"],
        "pinned_archive_sha256": census["pinned_archive_sha256"],
        "rule": ("criterion 5 = an offline stdlib-only reference solve that "
                 "reproduces the pinned answer byte-exactly, is admissible "
                 "under the declared arm (v4 module, policy v3), carries no "
                 "pinned-answer bytes in its source, and fits the fixed "
                 "1600-token per-session program budget"),
        "quorum": {"required": 6, "qualified": len(qualified),
                   "status": "MET" if len(qualified) >= 6 else "NOT_MET"},
        "grid_membership": [e["task_id"] for e in qualified],
        "qualified": qualified,
        "verified_but_budget_excluded": excluded,
        "criterion5_failures": failed,
        "not_reached": not_reached,
        "counts": {
            "offline_candidates": sum(
                1 for r in census["records"]
                if r.get("disposition") == "OFFLINE_CANDIDATE"),
            "qualified": len(qualified),
            "budget_excluded": len(excluded),
            "failures": len(failed),
            "not_reached": len(not_reached),
        },
        "boundary": ("This record is a task-selection artifact. It makes no "
                     "claim about the quality of any benchmark; every "
                     "non-qualifying disposition is a statement about our "
                     "contract's ability to derive the pinned answer from the "
                     "declared handout files within the registered budget."),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Criterion-5 verification — NYU CTF Bench crypto candidates (DRAFT 2026-11-05)",
        "",
        f"Pinned archive `{payload['pinned_archive']}` (sha256 "
        f"`{payload['pinned_archive_sha256']}`), complete census in "
        "`census_nyu/census_nyu_crypto.json`. This file records the "
        "pre-registered criterion-5 gate: an offline stdlib-only reference "
        "solve reproducing the pinned answer byte-exactly, admissible under "
        "the declared arm, with no pinned-answer bytes in the solver source, "
        "within the fixed 1600-token program budget.",
        "",
        f"**Quorum: {payload['quorum']['qualified']} qualified ≥ "
        f"{payload['quorum']['required']} required — {payload['quorum']['status']}.**",
        "",
        "| task | id | chars | est tokens | declared arm | disposition |",
        "|---|---|---|---|---|---|",
    ]
    for entry in qualified:
        lines.append(
            f"| {entry['name']} | `{entry['task_id']}` | {entry['solver_chars']} "
            f"| ≤{entry['est_tokens_chars_div4']} | {entry['declared_arm']} "
            f"| **QUALIFIED** |")
    for entry in excluded:
        lines.append(
            f"| {entry['name']} | `{entry['task_id']}` | {entry['solver_chars']} "
            f"| ≤{entry['est_tokens_chars_div4']} | {entry['declared_arm']} "
            f"| verified, budget-excluded |")
    for entry in failed:
        lines.append(
            f"| {entry['name']} | `{entry['task_id']}` | — | — | — "
            f"| {entry['status']} |")
    for entry in not_reached:
        lines.append(
            f"| {entry['name']} | `{entry['task_id']}` | — | — | — "
            f"| not reached |")
    lines += ["", "## Reasons", ""]
    for entry in excluded:
        lines.append(f"- **{entry['name']}** — {entry['reason']}")
    for entry in failed:
        lines.append(f"- **{entry['name']}** — {entry['reason']}")
    lines += [
        "",
        f"Not reached ({len(not_reached)}): " + ", ".join(
            e["name"] for e in not_reached) + " — " + NOT_REACHED_REASON + ".",
        "",
        "Boundary: " + payload["boundary"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(payload["counts"], indent=2))
    print(json.dumps(payload["quorum"], indent=2))
    print("grid:", ", ".join(payload["grid_membership"]))


if __name__ == "__main__":
    main()
