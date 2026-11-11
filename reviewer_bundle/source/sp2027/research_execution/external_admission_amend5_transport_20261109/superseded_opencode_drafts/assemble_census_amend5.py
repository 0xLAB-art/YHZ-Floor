#!/usr/bin/env python3
"""Assemble the Amendment-5 completeness census: load the interrupted
census stream (21/24 rows recorded before the process was killed), run the
3 missing probes (crack_me RT x 3 labels), and write
COMPLETENESS_CENSUS_AMEND5.json with the full 24-row register and the PASS
(pair, label) map. Non-evidence; budget identical to the census (cap 12000,
effort field omitted)."""
from __future__ import annotations

import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STREAM = HERE / "COMPLETENESS_CENSUS_stream.jsonl"
PROMPT_HASHES = HERE / "PROMPT_HASHES.json"
OUT = HERE / "COMPLETENESS_CENSUS_AMEND5.json"
CAP = 12_000
LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]
FROZEN_BLOCKED_PAIRS = [
    ["2015q-cry-eps_part2", "R0"],
    ["2015q-cry-eps_part2", "RT"],
    ["2017q-cry-almost_xor", "RT"],
    ["2018q-cry-babycrypto", "R0"],
    ["2018q-cry-babycrypto", "RT"],
    ["2018q-cry-lowe", "RT"],
]

from responses_client import AgentRouterResponsesClient, ProviderFailure  # noqa: E402


def classify(r: dict) -> str:
    text = r["text"]
    status = r["metadata"].get("finish_reason")
    if status == "completed" and text.strip() and "\"code\"" in text:
        return "PASS_VISIBLE_JSON"
    if status == "incomplete" and not text.strip():
        return "COMPLETION_RUMINATION_OVERFLOW"
    if not text.strip():
        return "COMPLETED_EMPTY_TEXT"
    return "COMPLETED_NO_JSON"


def main() -> int:
    rows = [json.loads(l) for l in STREAM.read_text().splitlines()
            if l.strip()]
    have = {(r.get("task_id"), r.get("representation"), r.get("label"))
            for r in rows}
    manifest = json.loads(PROMPT_HASHES.read_text())
    prompts = {(e["task_id"], e["representation"]): e
               for e in manifest["instantiated_prompts"]}
    needed = []
    for task, rep in sorted(prompts):
        if [task, rep] in FROZEN_BLOCKED_PAIRS:
            continue
        for label in LABELS:
            if (task, rep, label) not in have:
                needed.append((task, rep, label))

    key = None
    env_path = Path("/mnt/nvme5/ACTS-Attack/.env")
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("AGENTROUTER_API_KEY="):
            key = line.split("=", 1)[1].strip()
    if not key:
        raise SystemExit("AGENTROUTER_API_KEY not set")

    for task, rep, label in needed:
        entry = prompts[(task, rep)]
        prompt = (HERE / entry["path"]).read_text()
        t0 = time.time()
        client = AgentRouterResponsesClient(key, label, "https://agentrouter.org",
                                            effort=None)
        try:
            r = client.call(prompt, CAP)
            row = {"label": label, "task_id": task, "representation": rep,
                   "outcome": classify(r), "status":
                       r["metadata"].get("finish_reason"),
                   "text_chars": len(r["text"]),
                   "reasoning_tokens":
                       r["metadata"]["usage"].get("reasoning_tokens"),
                   "output_tokens":
                       r["metadata"]["usage"].get("output_tokens"),
                   "elapsed_s": round(time.time() - t0, 1), "cap": CAP}
        except ProviderFailure as exc:
            row = {"label": label, "task_id": task, "representation": rep,
                   "outcome": "PROVIDER_FAILURE", "category": exc.category,
                   "detail": exc.detail[:200],
                   "elapsed_s": round(time.time() - t0, 1), "cap": CAP}
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
        STREAM.open("a").write(json.dumps(row, sort_keys=True) + "\n")

    pass_rows = [r for r in rows if r.get("outcome") == "PASS_VISIBLE_JSON"]
    raise_system_none = None
    out = {
        "schema": "external-admission-amend5-completeness-census/1",
        "generated_date": time.strftime("%Y-%m-%d"),
        "evidence": False,
        "registered_cap": CAP,
        "effort_field": "omitted (backend measured to ignore it)",
        "frozen_blocked_pairs": FROZEN_BLOCKED_PAIRS,
        "frozen_blocked_note": (
            "HTTP 400 content-blocked verified on /v1/messages (2026-11-07),"
            " /v1/responses (2026-11-09), and under the funded account"
            " (2026-11-09) — label-independent"),
        "assembly_note": ("two-phase assembly: the first 21 census rows ran "
                          "in the interrupted process (stream preserved), "
                          "the remaining rows ran in this assembler under "
                          "the identical budget; one trans quota-403 during "
                          "the interrupted phase resubmitted cleanly here "
                          "if it was a needed row"),
        "pass_combinations": [[r["task_id"], r["representation"], r["label"]]
                              for r in pass_rows],
        "grid_sessions": len(pass_rows) * 4,
        "rows": rows,
        "boundary": (
            "PASS entries define the registered plan; rumination-overflow "
            "and blocked entries are measured transport/reasoning-budget "
            "boundaries recorded as two-sided exclusions with rows — never "
            "zeros, never agent behavior"),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    by_task = {}
    for r in rows:
        by_task.setdefault((r["task_id"], r["representation"]), {})[
            r["label"]] = r["outcome"]
    print(json.dumps({"pass_combinations": len(pass_rows),
                      "grid_sessions": out["grid_sessions"],
                      "by_pair_label": {f"{t}|{r}": v
                                        for (t, r), v in sorted(by_task.items())}},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
