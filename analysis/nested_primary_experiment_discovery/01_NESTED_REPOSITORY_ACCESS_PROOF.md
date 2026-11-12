# Nested repository access proof

Audit date: 2026-10-15 (Africa/Cairo). Audit mode: read-only. No archived attack harness, provider, or experiment was executed.

## Gate result

`PARTIAL DISCOVERY — NAMED EVIDENCE GAPS` for the project-wide claim, with the nested checkout itself file-inventoried. The nested checkout is readable and distinct from the outer repository. This corrected pass covers the entire nested tree, not only its named result directories:

```
pwd -P
/mnt/nvme5/ACTS-Attack

outer Git root   /mnt/nvme5/ACTS-Attack
nested Git root  /mnt/nvme5/ACTS-Attack/ACTS-ATTACK
```

Required directories exist and were readable: `data/`, `harness/`, `results/`, `results_rerun/`, and `targets/`. The nested checkout is dirty and contains untracked `harness/v3/`, `harness/v4/`, and `data/c2t1_toolchain_diversity_repro.json`; those states were preserved.

## Measured full-tree surface

Scope warning: this file proves access to the nested primary checkout only. The outer ACTS-Attack project contains additional evidence surfaces. See 12_OUTER_PROJECT_EVIDENCE_DISCOVERY.md; do not interpret the nested 805-file closure as project-wide closure.

| Surface | Files | Bytes | Review treatment |
|---|---:|---:|---|
| nested repository total, including `.git/` | 805 | 5,564,098 | recursive inventory |
| nested working tree excluding `.git/` | 465 | 4,515,595 | exhaustive file manifest and SHA-256 |
| `.git/` metadata/object store | 340 | 1,048,503 | counted separately; not scientific result evidence |
| `data/` | 9 | 105,935 | full structured reads |
| `harness/` | 423 | 4,239,945 | exhaustive file manifest; all JSON/JSONL/TSV parsed; text/logs read or targeted; bytecode metadata only |
| `results/` | 1 | 6,390 | full structured read |
| `results_rerun/` | 2 | 7,691 | full structured reads |
| `targets/` | 27 | 135,494 | exhaustive inventory and source reads; not executed |

The 465-file working-tree count includes root documentation/configuration and every file under `data/`, `harness/`, `results/`, `results_rerun/`, and `targets/`. It includes the previously omitted `harness/results_c2b_smoke/` surface. The required-directory subtotal is not a partition of the total because root files are additional.

The exhaustive manifest classifies 329 files as result/evidence-bearing, 65 as harness/target code, 52 as binary-cache metadata, 11 as supporting code/configuration, 5 as environment/credential artifacts, and 3 as repository documentation.

## Explicit Git-state reconciliation for retained data and results

Git state was measured separately from filesystem presence. Important retained records are not ordinary tracked files:

| Exact surface | Filesystem files | tracked | untracked, nonignored | ignored |
|---|---:|---:|---:|---:|
| \`data/\` | 9 | 8 | 1 | 0 |
| \`results/\` | 1 | 1 | 0 | 0 |
| \`results_rerun/\` | 2 | 2 | 0 | 0 |
| \`harness/results_c2b_smoke/\` | 23 | 23 | 0 | 0 |
| \`harness/results_c2b_pq/\` | 97 | 97 | 0 | 0 |
| \`harness/results_c2b_h1b/\` | 13 | 13 | 0 | 0 |
| \`harness/v2/results/\` | 74 | 0 | 0 | 74 |
| \`harness/v3/results/\` | 74 | 0 | 74 | 0 |
| \`harness/rerun/results_rerun/\` | 31 | 31 | 0 | 0 |

The critical non-Git evidence is \`data/c2t1_toolchain_diversity_repro.json\` (untracked, nonignored), all 74 files under \`harness/v2/results/e2/_loop_out/\` (ignored), and all 74 files under \`harness/v3/results/e2/_loop_out/\` (untracked, nonignored). The v2 and v3 session contents are byte-identical on the 74-file hash comparison, but their Git states and directory lineage remain distinct provenance facts. The manifest records \`git_state\` for every one of the 465 non-Git files. Git tracking status is not used as a scientific validity criterion.

The current status reconciliation adds 99 nonignored untracked paths and 133 ignored paths. Of 232 tracked paths marked modified, 231 are content-identical to nested `HEAD` and differ only by mode; `README.md` is the one content-different tracked file. The untracked `harness/v4/` directory contains three wrappers and no results. See `18_COMMITTED_UNCOMMITTED_WORKTREE_RECONCILIATION.md`.

## Provenance anchors

- Nested HEAD: `8760f37a83f9d80e830f8f9cd750785c8c97069f9`, 2026-10-06, `Fail closed on explicit qualification schedules`.
- Nested branch: `main...origin/main [ahead 8]`; the working tree is materially modified.
- README SHA-256: `d0be0470ef3b7029f4b313703c95f464180a17ebd4ebf142630e91f7bf04400b`.
- `data/c2b_hybrid_required_control.json` SHA-256: `826686ac374ea999745080f72b45a08d0f54575de08aed65b5c6f846947774f5`.
- `results_rerun/operation_records.jsonl` SHA-256: `3f56aa3aa04af6cfa42ab96a9e69eede9b656e13fb06b5e72053e49ea88521d7`.

## Read scope and non-execution boundary

The corrected pass parsed every non-Git JSON, JSONL, and TSV file in the 465-file working tree, enumerated and SHA-256 hashed every non-Git file, and classified every path. Text source/log/trace files were read as text or targeted by content search; repetitive trace families were counted and structurally reconciled. Binary artifacts were metadata-only. No harness, target, attack script, provider, or LLM was executed. This establishes full file-level inventory coverage and structured-result coverage; it does not claim that every repetitive trace byte was manually interpreted line-by-line.

## Maximum recursive closure

The follow-up maximum crawl read all 805 regular files under the nested repository, including .git, totaling 5,564,098 bytes, with zero read errors. It streamed and integrity-checked all 336 Git objects, inspected all 23 historical commits plus original/remote/tag/dangling refs, and found zero historical-only paths absent from the current working-tree inventory. It also unmarshalled all 52 Python bytecode files for metadata without executing them. See 11_MAX_RECURSIVE_CRAWL_CLOSURE.md.
