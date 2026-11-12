#!/usr/bin/env python3
"""Decode-equality hard gate — Amendment 3 (DRAFT 2026-11-05).

BEFORE any generation, verifies that the RT representation is
information-preserving:

  1. the task statement text is identical between prompt_R0 and prompt_RT;
  2. every base64 artifact block in prompt_RT decodes byte-identically to the
     fixture artifact bytes in fixtures/tasks/<task_id>/;
  3. the artifact name sets are identical across R0 and RT.

Writes fixtures/decode_equality_log.json; exit 0 only if every task passes.
Offline, $0, zero model calls.
"""

import base64
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RT_ROOT = HERE / "rt_transform"
TASKS_ROOT = HERE / "tasks"
MANIFEST = ROOT / "PROMPT_HASHES.json"
LOG = HERE / "decode_equality_log.json"

HEADER = re.compile(r"^--- FILE: (\S+) \((verbatim|base64)\) ---$", re.M)


def split_prompt(text):
    marker = "\n\nPROVIDED ARTIFACTS:\n"
    head, rest = text.split(marker, 1)
    statement = head.split("TASK STATEMENT (verbatim from the benchmark metadata):\n", 1)[1]
    tail_marker = "\n\nWrite complete Python 3 source"
    body, _ = rest.split(tail_marker, 1)
    blocks, matches = {}, list(HEADER.finditer(body))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        name, encoding = match.group(1), match.group(2)
        chunk = body[match.end():end].strip("\n")
        blocks[name] = (encoding, chunk)
    return statement, blocks


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    index = manifest["instantiated_prompts"]
    tasks = sorted({entry["task_id"] for entry in index})
    results, all_ok = [], True
    for task in tasks:
        r0_text = (RT_ROOT / task / "prompt_R0.txt").read_text(encoding="utf-8")
        rt_text = (RT_ROOT / task / "prompt_RT.txt").read_text(encoding="utf-8")
        stmt_r0, blocks_r0 = split_prompt(r0_text)
        stmt_rt, blocks_rt = split_prompt(rt_text)

        statement_identical = stmt_r0 == stmt_rt
        names_identical = set(blocks_r0) == set(blocks_rt)
        checks = []
        for name in sorted(blocks_rt):
            encoding, chunk = blocks_rt[name]
            note_ok = chunk.startswith("DECODE NOTE:")
            payload = chunk.split("\n", 1)[1].replace("\n", "") if note_ok else chunk
            decoded = base64.b64decode(payload)
            original = (TASKS_ROOT / task / name).read_bytes()
            checks.append({
                "file": name,
                "encoding": encoding,
                "decode_note_present": note_ok,
                "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
                "original_sha256": hashlib.sha256(original).hexdigest(),
                "equal": decoded == original,
            })
        r0_verbatim = all(blocks_r0[name][0] == "verbatim" for name in blocks_r0)
        ok = (statement_identical and names_identical and r0_verbatim
              and all(c["equal"] and c["decode_note_present"] for c in checks))
        all_ok &= ok
        results.append({
            "task_id": task,
            "statement_identical": statement_identical,
            "artifact_names_identical": names_identical,
            "r0_verbatim": r0_verbatim,
            "artifact_checks": checks,
            "gate": "PASS" if ok else "FAIL",
        })

    log = {
        "schema": "external-admission-amend3-decode-equality/1-draft",
        "gate": "PASS" if all_ok else "FAIL",
        "hard_gate_requirement": (
            "decode(RT artifact) == R0 fixture bytes, statement identity, and "
            "identical artifact-name sets, before any generation"),
        "tasks": results,
        "boundary": "Design-readiness record only; no generation was executed.",
    }
    LOG.write_text(json.dumps(log, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"gate": log["gate"],
                      "per_task": {r["task_id"]: r["gate"] for r in results}}, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
