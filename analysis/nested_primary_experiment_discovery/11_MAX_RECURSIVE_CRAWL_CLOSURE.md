# Maximum recursive crawl closure

Audit date: 2026-10-15. Scope: /mnt/nvme5/ACTS-Attack/ACTS-ATTACK. This is a read-only crawl. No attack harness, target, provider, LLM, or experiment was executed.

## What was previously under-specified

The earlier complete statement covered the 465-file non-Git working tree. It did not explicitly close the nested .git object store, compiled Python caches, dangling Git objects, or every historical ref. Those surfaces are now separately crawled and reconciled here.

## Full filesystem crawl

| Surface | Result |
|---|---:|
| regular files under ACTS-ATTACK, including .git | 805 |
| total bytes read | 5,564,098 |
| read errors | 0 |
| non-Git working-tree files | 465 |
| .git regular files | 340 |
| text/JSON-like files read as text | 444 |
| binary/structured non-text files | 361 |
| Python bytecode files | 52 |

Every regular filesystem file was opened, read to EOF, byte-counted, and SHA-256 processed. This is a byte-level crawl; it does not mean that every repetitive trace line was manually interpreted.

## Structured and compiled-file review

- All 17 JSON files parsed successfully; zero JSON parse failures.
- All 946 nonblank JSONL records parsed successfully; zero bad JSONL lines.
- All 3 TSV files were read successfully.
- All 52 .pyc files were unmarshalled as Python code-object metadata without executing their code. Their code-object names and result/oracle/session/key/verdict/model-related constants were inspected.
- All 4 PEM/key/configuration artifacts were read for metadata and hashed. Secret/private material is not reproduced in this report.
- All no-extension files and Dockerfiles were read and classified as text/configuration.

The compiled artifacts are not independent result observations. They are provenance-bearing caches. They contain references to additional E5, service-oracle, model-session, verdict, and qualification paths; those corresponding source/result paths are present in the 465-file working-tree inventory.

## Git object and historical crawl

The nested Git database was not treated as a black box:

- 336 loose/packed Git objects were streamed through cat-file batch mode.
- Object integrity checks completed with zero SHA-1 mismatches.
- Object types: 29 commits, 61 trees, 246 blobs.
- All refs, including original refs, remote refs, tags, and HEAD, were enumerated.
- 23 reachable/original historical commits were tree-listed.
- The dangling commit 9ead8be018c6a8b85312179da17bd98d7d26dc90 and dangling blob 89d8bf0017c00401e628e55ca4641241b8fda826 were identified and inspected at object level.
- Historical tree paths: 233 unique paths; 178 result-like/data/harness paths.
- Historical-only paths absent from the current working tree: 0 result-like paths and 0 total paths.

Therefore, the Git database contains history and migration/provenance evidence, but this crawl found no historical result file that is absent from the current filesystem inventory. The dangling objects remain named evidence and are not silently discarded; they do not currently establish an additional experiment.

## Critical paths explicitly closed

The recursive crawl includes:

- all ignored harness/v2/results JSONL sessions;
- all untracked harness/v3/results JSONL sessions;
- all untracked data/c2t1_toolchain_diversity_repro.json;
- all tracked results, results_rerun, C2b smoke/PQ/H1B results, and harness rerun results;
- all harness/v4 source and bytecode files;
- all targets source, Dockerfiles, oracle copies, E5 escrow/victim files, and bytecode;
- all keys, certificates, OpenSSL configuration, caches, logs, traces, manifests, and no-extension files;
- all nested .git refs, logs, index, packed refs, objects, historical commits, trees, and blobs.

## Remaining scientific limitation

This closes filesystem and repository-path discovery. It does not convert compiled caches, Git objects, copied sessions, provider-error sessions, or historical summaries into independent physical experiments. The evidence ledger must continue to distinguish raw observations, copies, controls, historical records, uncompleted campaigns, and provenance-only artifacts.

## Closure status

MAXIMUM RECURSIVE FILESYSTEM AND GIT CRAWL COMPLETE — NO UNCRAWLED REGULAR FILES IDENTIFIED
