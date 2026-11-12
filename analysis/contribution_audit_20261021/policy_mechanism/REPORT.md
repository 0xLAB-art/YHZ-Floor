# Source-policy mechanism audit — 2026-10-21

The actual v3 representation outcomes do not reduce to source-import rejection: **zero of 852 sources were rejected for imports under v3**. The three pre-output failures are one syntax error and two runtime errors. Cryptographic checks freshly reproduce 738/768 primary completions, 63/64 R4 noise completions, and 20/20 C0 correct abstentions. These are separate populations and predicates.

The narrower legacy policy is a **counterfactual policy**, not the task contract stated in these prompts. Its 205 import rejects all concern modules explicitly permitted by the frozen prompt; the additional reject is syntax. Calling these 205 programs task-contract violations would be incorrect. Applying legacy policy to unchanged generated artifacts measures local policy sensitivity, not generation under a legacy prompt.

| Population | N | Legacy qualified | Unused-only removable reject | Referenced import remains | Syntax | Legacy rejected, cryptographically correct |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 768 | 584 | 99 | 84 | 1 | 168 |
| R4 noise | 64 | 47 | 4 | 13 | 0 | 16 |
| C0 abstention | 20 | 15 | 1 | 4 | 0 | 5 |

128 derivatives remove only eligible, whole, top-level import statements. Every derivative produces the identical parsed JSON output as its unmodified fresh execution. 104 now qualify under legacy; 98 are correct (primary 94, noise 3, C0 1), while six remain incorrect (primary 5, noise 1). The other 24 derivatives still contain referenced imports and remain legacy-rejected. No program logic was repaired, and none of the 31 original incorrect outcomes was improved.

| Primary arm (all levels, descriptive only) | N | Original legacy-qualified and correct | After conservative removal, legacy-qualified and correct | Actual v3 correct |
|---|---:|---:|---:|---:|
| R0 | 256 | 207 | 214 | 250 |
| R1 | 256 | 238 | 250 | 254 |
| R2 | 256 | 125 | 200 | 234 |

These arm totals are not the preregistered L3 estimand. `FULL_CENSUS.json` separates every population/arm/level/family, and `CASE_LEDGER.jsonl` preserves seed and replicate index for matched analyses. The large counterfactual policy effect is partly an unused-import artifact but does not disappear after conservative cleanup; residual rejection includes source that actually uses permitted helper modules. This does not establish those imports are necessary to all possible solutions.

Runtime tracing separately observed a LOAD opcode with imported-object identity in **100 of the 101 sources with legacy-disallowed static references** (typing, collections, math). Their instrumented outputs exactly match the fresh uninstrumented outputs. One noise source, `confirmatory-0328-ecd-L3-10013-R4-r2-f3641337`, has static references but no observed use on this input; its imports remain conservatively preserved. Reached loads include evaluated typing annotations, which are real runtime dependencies even though they do not perform cryptanalysis. `import_use_trace_v2/RESULTS.json` records binding, originating module, line, opcode, and evidence directory.

The original contract's `unused_imports` is not a semantic classifier. It collects module roots and imported members, then subtracts AST Name spellings. Thus `from typing import Tuple` can report `typing` unused even while evaluating `Tuple[int, int]`; `from collections import defaultdict` likewise reports the root unused while calling its member. The transform follows bound names (including aliases), preserves any reference in any scope, string mentions, reflective/dynamic access, nested imports, wildcard/relative imports, mixed used/unused statements, and modules outside a fixed standard-library subset. Whole-statement deletion is recorded as exact before/after lines and old/new SHA-256. It deliberately under-removes. No general semantic equivalence claim follows from AST analysis: only identical observed outputs on the retained inputs are established. Import initialization side effects and unobserved branches remain a limitation.

Execution and provenance: 851 syntax-valid originals plus 128 derivatives were freshly executed using `readiness_revision_20261021/execute_replay.py::sandbox_command`. Only the runtime, program, and public observation are mounted; private state is not exposed to the child. Original `h1r3_reference.py` reconstruction functions and frozen contract schema checks run in the parent, independently of candidate execution. Public reconstruction is compared with private truth. These are cryptographic checks; derivative attribution certificates are not synthesized or claimed accepted. Source/prompt hashes match all retained records; input hashes remain unchanged. All 849 successful original executions emitted one nonblank JSON line; all fresh cryptographic outcomes match the retained predicates. No provider calls occurred.

Reproduce from this directory, using a new output directory for each fresh run:

```
python3 -B -m unittest -v test_transform test_trace > .omo/evidence/tests-final.log 2>&1
python3 -B audit.py --output .omo/evidence/run01 --workers 6 > .omo/evidence/run01.log 2>&1
python3 -B trace_imports.py --run .omo/evidence/run01 --name import_use_trace_v2 --workers 6 > .omo/evidence/trace-run02.log 2>&1
python3 -B finalize.py > .omo/evidence/finalize.log 2>&1
```

The invocations above were actually executed; `run01` already exists and is intentionally protected from overwrite. Change the output and trace names for another run and adjust finalize's selected run if needed. `audit.py` is the runnable full-census/derivative audit. `finalize.py` enriches the complete case ledger and writes stratified census and validation. Every case has command, stdout/stderr hashes, parsed output where present, independent predicate, and exact edit lineage. The one syntax-invalid source has a qualification record and is not represented as executed.

| Criterion / exact scenario | Binary observable | Captured artifact |
|---|---|---|
| Conservative transform and trace identity fixtures | 15 tests pass, exit 0 | `.omo/evidence/tests-final.log` |
| Complete frozen census + isolated originals/derivatives | 852 unique rows, no sandbox errors, 128/128 derivative output equality, exit 0 | `.omo/evidence/run01.log`, `run01/CASE_LEDGER.jsonl`, `run01/SUMMARY.json` |
| Distinguish static from observed import use | 101 traced cases, 100 observed-use cases, 0 output disagreements, exit 0 | `.omo/evidence/trace-run02.log`, `run01/import_use_trace_v2/RESULTS.json` |
| Preserve raw inputs and every population | manifest hashes unchanged, full strata emitted, validation PASS | `run01/input_manifest.json`, `run01/FULL_CENSUS.json`, `run01/VALIDATION.json` |

All `run01/...` shorthand paths above are under `.omo/evidence/`. Input source-policy, prompt, preregistration, program, reference, and output hashes are in the input manifest. Artifact hashes are in `.omo/evidence/MANIFEST.json`.

Instrumentation correction: the first `import_use_trace` attempt observed no opcodes because this Python 3.12 build requires enabling opcode tracing on the caller frame before `sys.settrace`. That trace is retained but invalid for use classification. The corrected `import_use_trace_v2` reruns the entire 101-case scenario and passes a sandboxed alias/annotation/unused/shadowed-binding fixture. No original or derivative execution result depends on the first trace.

Allowed claims: local legacy policy sensitivity; bounded observed unused-import removability; actual-v3 absence of import rejects; explicit cryptographic failure preservation; observed runtime import dependencies. Disallowed claims: universally harmless imports; all legacy rejects are unused imports; all referenced imports are mathematically necessary; local policy sensitivity establishes a new attack, broad model capability, or a causal representation effect; a derivative with correct output has an accepted attribution certificate.
