#!/usr/bin/env python3
"""Offline, post-hoc re-adjudication of recorded action-parse failures.

Registered outcome is NOT changed. ``results.jsonl`` stays the registered
record, and this script never rewrites it, ``summary.json``, ``run_info.json``
or any capture under ``sessions/``. It answers one narrower question:

    when the frozen extractor returned ``None`` on a recorded turn, did the
    recorded provider response nevertheless contain an executable program,
    and would that program have been accepted by the same oracle pipeline?

Motivation (frozen record): in the 2026-10-24 extension cohort, seeds 70, 71,
72 and 74 recorded ``stage="parse"``, ``error_class="encoding"``,
``submitted=false`` on the interactive arm's second turn — i.e. the arm
obtained no second submission at all. ``classify_rejection`` maps *every*
parse-stage failure to ``"encoding"``, so the recorded class does not
distinguish "response was undecodable" from "response contained a program but
no JSON action object". Reading the stored raw responses shows the second case:
a fenced ```python block with no ``{"code": ...}`` envelope.

Everything here is local and deterministic: no provider call is made, the code
comes from the stored response, and execution reuses the frozen pipeline
(``policy_check`` + ``run_program``) unchanged. The re-adjudicated number is
labelled *post hoc* everywhere; it is not a pre-registered result and is not a
substitute for re-running the arm.

Writes only under ``readjudication/``.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "readjudication"
CAPS = OUT / "execution_captures"

FENCE = re.compile(r"```(?:json|python|py)?[ \t]*\r?\n(.*?)```", re.DOTALL)


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "h2_pairs_extension_runner", HERE / "run_h2_pairs_extension.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    # Redirect every capture write away from the registered session tree.
    mod.SESS = OUT
    return mod


def recover_code(mod, text):
    """Frozen extractor first, then fenced-block recovery.

    Returns (code, route) or (None, reason).
    """
    action = mod.extract_action(text)
    if action:
        return action["code"], "frozen_extractor"
    for block in FENCE.findall(text):
        body = block.strip()
        if not body:
            continue
        # a fenced json envelope that the frozen extractor refused for some
        # other reason (e.g. nested under a key) still counts as JSON-shaped
        if body.startswith("{"):
            try:
                obj = json.loads(body)
            except ValueError:
                obj = None
            if isinstance(obj, dict) and isinstance(obj.get("code"), str):
                return obj["code"], "fenced_json"
        return body, "fenced_python"
    return None, "no_executable_code"


def main():
    OUT.mkdir(exist_ok=True)
    CAPS.mkdir(exist_ok=True)
    mod = load_runner()

    rows = [json.loads(line) for line in
            (HERE / "results.jsonl").read_text().splitlines() if line.strip()]
    targets = []
    for row in rows:
        for rec in row.get("turn_records") or []:
            if rec.get("stage") == "parse" and not rec.get("submitted"):
                targets.append((row, rec["turn"]))

    records = []
    for row, turn in sorted(targets, key=lambda t: (t[0]["seed"], t[0]["arm"], t[1])):
        raw_path = (HERE / "sessions" / "raw_provider_responses"
                    / f"{row['run_id']}__turn{turn}.json")
        out = {"registered_run_id": row["run_id"], "seed": row["seed"],
               "arm": row["arm"], "turn": turn,
               "registered_stage": "parse", "registered_error_class": "encoding",
               "raw_response_present": raw_path.is_file()}
        if not raw_path.is_file():
            out.update({"recovered": False, "reason": "raw_response_missing"})
            records.append(out)
            continue
        body = json.loads(raw_path.read_text())
        text = "".join(part.get("text", "") for part in body.get("content") or []
                       if isinstance(part, dict) and part.get("type") == "text")
        code, route = recover_code(mod, text)
        if code is None:
            out.update({"recovered": False, "reason": route,
                        "response_chars": len(text)})
            records.append(out)
            continue

        public, _secret = mod.instance(row["seed"])
        allowed, policy = mod.policy_check(code)
        rid = f"readjudication__{row['arm']}__seed_{row['seed']}__turn{turn}"
        if not allowed:
            out.update({"recovered": True, "route": route, "policy": policy,
                        "accepted": False, "post_hoc_verdict": "policy_rejected"})
            records.append(out)
            continue
        facts = mod.run_program(code, row["seed"], public, rid, turn)
        candidate = None
        if facts["stage"] == "output" and facts["out"]:
            try:
                candidate = json.loads(facts["out"].splitlines()[-1])
            except (ValueError, IndexError):
                candidate = None
        truth = _secret["plaintext"]
        accepted = (facts["stage"] == "output" and facts["proc_rc"] == 0
                    and mod.verdict(candidate, truth))
        out.update({"recovered": True, "route": route,
                    "execution_stage": facts["stage"],
                    "returncode": facts["proc_rc"], "queries": facts["queries"],
                    "oracle_usage_present": facts["usage_present"],
                    "candidate_hex": (candidate or {}).get("plaintext_hex"),
                    "accepted": accepted,
                    "post_hoc_verdict": "accepted" if accepted else "rejected",
                    "error_class": None if accepted else mod.classify_rejection(
                        facts["stage"], code, facts["proc_rc"], candidate,
                        facts["out"], facts["err"], facts["queries"], truth,
                        {"full_padded_second_block_hex": _secret["padded"][16:32].hex(),
                         "decrypted_first_block_hex": _secret["d_c0"].hex(),
                         "prefix_hex_witness": _secret["prefix"].hex()})})
        records.append(out)

    (OUT / "results.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in records))

    recovered = [r for r in records if r.get("recovered")]
    accepted = [r for r in records if r.get("accepted")]
    summary = {
        "schema": "h2-parse-failure-readjudication/1.0",
        "post_hoc": True,
        "registered_source": "results.jsonl (unchanged)",
        "parse_failure_turns": len(records),
        "recovered_code_turns": len(recovered),
        "post_hoc_accepted_turns": len(accepted),
        "accepted_seeds": sorted({r["seed"] for r in accepted}),
        "routes": {route: sum(1 for r in records if r.get("route") == route)
                   for route in sorted({r.get("route") for r in records if r.get("route")})},
        "note": ("Post-hoc only. The registered arm outcome stands; this "
                 "diagnoses whether a recorded format failure hid an "
                 "executable, acceptable submission."),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    lines = ["# Post-hoc re-adjudication of recorded action-parse failures", "",
             "Registered outcomes are unchanged (`results.jsonl` untouched).", "",
             "| seed | arm | turn | recovered | verdict | queries |",
             "|---|---|---|---|---|---|"]
    for r in records:
        lines.append("| {seed} | {arm} | {turn} | {rec} | {v} | {q} |".format(
            seed=r["seed"], arm=r["arm"], turn=r["turn"],
            rec="yes" if r.get("recovered") else "no", v=r.get("post_hoc_verdict", r.get("reason", "")),
            q=r.get("queries", "")))
    lines += ["", f"Recovered {len(recovered)}/{len(records)}; post-hoc accepted "
                  f"{len(accepted)} (seeds {summary['accepted_seeds']}).", ""]
    (OUT / "REPORT.md").write_text("\n".join(lines))

    print(json.dumps(summary, indent=2, sort_keys=True))
    for r in records:
        print(json.dumps({k: r.get(k) for k in
                          ("seed", "arm", "turn", "route", "recovered",
                           "post_hoc_verdict", "queries", "execution_stage")},
                         sort_keys=True))


if __name__ == "__main__":
    main()
