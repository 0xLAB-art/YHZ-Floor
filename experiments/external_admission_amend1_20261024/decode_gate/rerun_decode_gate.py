#!/usr/bin/env python3
"""Amendment-1 hard gate: re-run the decode-equality check on all 4 qualified
tasks with the FROZEN machinery of the basis namespace.

Every input is hash-asserted against the basis FREEZE.json /
PROMPT_HASHES.json values before use:
  - fixtures/rt_transform/<task>/prompt_R0.txt, prompt_RT.txt (frozen prompts),
  - fixtures/tasks/<task>/{source.py,output.txt} (frozen fixtures),
  - fixtures/rt_transform/verify_decode_equality.py (gate logic module; its
    parse_rt_blocks is executed verbatim — never re-implemented).

The gate never contacts a model. Its output log is written HERE (this
namespace) and hashed into this namespace's FREEZE.json BEFORE the freeze
commit and before any experiment model call. Gate FAIL => status no_go.
"""
import base64
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
BASIS = NS.parent / "external_admission_20261024"

BASIS_FREEZE = json.loads((BASIS / "FREEZE.json").read_text())["files"]
BASIS_PROMPTS = {p["path"]: p["sha256"] for p in
                 json.loads((BASIS / "PROMPT_HASHES.json").read_text())["instantiated_prompts"]}

TASKS = [
    "htb_cyber_apocalypse_2024__Makeshift",
    "htb_cyber_apocalypse_2024__Dynastic",
    "htb_cyber_apocalypse_2024__Primary_Knowledge",
    "htb_cyber_apocalypse_2024__Partial_Tenacity",
]


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def assert_frozen(rel: str, expected: str) -> None:
    got = sha_file(BASIS / rel)
    if got != expected:
        sys.exit(f"FROZEN BASIS HASH MISMATCH: {rel}: {got} != {expected}")


def main() -> int:
    # Hash-assert every frozen input before executing any gate logic.
    for task in TASKS:
        assert_frozen(f"fixtures/tasks/{task}/source.py", BASIS_FREEZE[f"fixtures/tasks/{task}/source.py"]["sha256"])
        assert_frozen(f"fixtures/tasks/{task}/output.txt", BASIS_FREEZE[f"fixtures/tasks/{task}/output.txt"]["sha256"])
        for rep in ("R0", "RT"):
            rel = f"fixtures/rt_transform/{task}/prompt_{rep}.txt"
            assert_frozen(rel, BASIS_PROMPTS[rel])
    assert_frozen("fixtures/rt_transform/verify_decode_equality.py",
                  BASIS_FREEZE["fixtures/rt_transform/verify_decode_equality.py"]["sha256"])

    # Execute the frozen gate logic module verbatim (parse_rt_blocks).
    sys.path.insert(0, str(BASIS / "fixtures" / "rt_transform"))
    import verify_decode_equality as frozen_gate  # noqa: E402

    results, all_ok = [], True
    for task in sorted(TASKS):
        r0 = (BASIS / "fixtures" / "rt_transform" / task / "prompt_R0.txt").read_text()
        rt = (BASIS / "fixtures" / "rt_transform" / task / "prompt_RT.txt").read_text()
        stmt_r0 = r0.split("TASK STATEMENT (verbatim from the benchmark metadata):\n")[1].split("\n\nPROVIDED ARTIFACTS:")[0]
        stmt_rt = rt.split("TASK STATEMENT (verbatim from the benchmark metadata):\n")[1].split("\n\nPROVIDED ARTIFACTS:")[0]
        statement_identical = stmt_r0 == stmt_rt
        checks = []
        for block in frozen_gate.parse_rt_blocks(rt):
            decoded = base64.b64decode(block["b64"])
            original = (BASIS / "fixtures" / "tasks" / task / block["file"]).read_bytes()
            checks.append({"file": block["file"],
                           "decode_note_present": block["decode_note"].startswith("DECODE NOTE:"),
                           "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
                           "original_sha256": hashlib.sha256(original).hexdigest(),
                           "equal": decoded == original})
        ok = statement_identical and all(c["equal"] and c["decode_note_present"] for c in checks)
        all_ok &= ok
        results.append({"task_id": task, "statement_identical": statement_identical,
                        "artifact_checks": checks, "gate": "PASS" if ok else "FAIL"})
    log = {"schema": "external-admission-amend1-decode-equality/1",
           "namespace": "external_admission_amend1_20261024",
           "gate": "PASS" if all_ok else "FAIL",
           "hard_gate_requirement": "decode(RT artifact) == R0 artifact bytes AND statement identity, re-verified before any Amendment-1 experiment model call",
           "machinery": "frozen basis namespace external_admission_20261024 (all inputs hash-asserted at runtime); parse_rt_blocks executed verbatim from verify_decode_equality.py",
           "tasks": results,
           "boundary": "Hard design gate for Amendment 1; must PASS before the freeze commit and any experiment model call."}
    out = HERE / "decode_equality_log_amend1.json"
    out.write_text(json.dumps(log, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gate": log["gate"], "log": str(out),
                      "per_task": [{r["task_id"]: r["gate"]} for r in results]}, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
