#!/usr/bin/env python3
"""Decode-equality hard gate for external_admission_20261024 (FROZEN).

Verifies, BEFORE any generation, that the RT representation is
information-preserving: every base64 artifact block in the RT prompt decodes
to bytes identical to the corresponding R0 artifact file, and the task
statement text is identical between the R0 and RT prompts.

This gate never contacts a model. In the executed phase state (early stop at
task selection) this is a design-readiness check, not experiment evidence.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def parse_rt_blocks(rt_prompt: str) -> list[dict]:
    blocks = []
    for m in re.finditer(r"--- FILE: (.+?) \(base64\) ---\n(.+?)\n(?:---|\Z)", rt_prompt, re.S):
        name = m.group(1)
        body = m.group(2)
        note_and_payload = body.split("\n", 1)
        blocks.append({"file": name, "decode_note": note_and_payload[0],
                       "b64": note_and_payload[1].replace("\n", "")})
    return blocks


def main() -> int:
    index = json.loads((ROOT / "fixtures" / "rt_transform" / "prompt_instantiation_index.json").read_text())
    results = []
    all_ok = True
    for task in sorted({t["task_id"] for t in index}):
        r0 = (ROOT / "fixtures" / "rt_transform" / task / "prompt_R0.txt").read_text()
        rt = (ROOT / "fixtures" / "rt_transform" / task / "prompt_RT.txt").read_text()
        # 1. statement identity between representations
        stmt_r0 = r0.split("TASK STATEMENT (verbatim from the benchmark metadata):\n")[1].split("\n\nPROVIDED ARTIFACTS:")[0]
        stmt_rt = rt.split("TASK STATEMENT (verbatim from the benchmark metadata):\n")[1].split("\n\nPROVIDED ARTIFACTS:")[0]
        statement_identical = stmt_r0 == stmt_rt
        # 2. decode-equality of every RT artifact block against the R0 fixture bytes
        checks = []
        for block in parse_rt_blocks(rt):
            decoded = base64.b64decode(block["b64"])
            original = (ROOT / "fixtures" / "tasks" / task / block["file"]).read_bytes()
            has_note = block["decode_note"].startswith("DECODE NOTE:")
            checks.append({"file": block["file"], "decode_note_present": has_note,
                           "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
                           "original_sha256": hashlib.sha256(original).hexdigest(),
                           "equal": decoded == original})
        ok = statement_identical and all(c["equal"] and c["decode_note_present"] for c in checks)
        all_ok &= ok
        results.append({"task_id": task, "statement_identical": statement_identical,
                        "artifact_checks": checks, "gate": "PASS" if ok else "FAIL"})
    log = {"schema": "external-admission-decode-equality/1",
           "gate": "PASS" if all_ok else "FAIL",
           "hard_gate_requirement": "decode(RT artifact) == R0 artifact bytes AND statement identity, before any generation",
           "tasks": results,
           "boundary": "Design-readiness record only: the phase stopped at task selection and no generation was ever executed."}
    (ROOT / "fixtures" / "decode_equality_log.json").write_text(json.dumps(log, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gate": log["gate"],
                      "per_task": [{r["task_id"]: r["gate"]} for r in results]}, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
