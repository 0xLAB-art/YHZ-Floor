# Outer Git Object-Database Crawl

Date: 2026-10-15

## Scope correction

The earlier outer crawl excluded `.git/` from the byte inventory. That exclusion was not scientifically safe for this task because the outer Git object database is part of the retained project state and contains historical, deleted, staged, and temporary objects. This report covers the outer repository Git database at:

`/mnt/nvme5/ACTS-Attack/.git`

No Git object, pack, ref, or history was modified. No archived attack script, harness, provider, or experiment was executed.

## Byte accounting

The outer `.git` directory is approximately 22 GiB. `git count-objects -vH` reported:

- loose objects: 5,187 objects, 538.80 MiB;
- indexed pack objects: 2 objects in one normal pack, 2.59 GiB packed;
- garbage temporary packs: 27 files, 18.54 GiB;
- normal pack file: 2,782,457,835 bytes;
- temporary-pack files are named `tmp_pack_*` and have no corresponding index files.

The 27 temporary files all begin with a valid Git pack v2 header and one blob object. Header inspection found two declared blob-size families: 1,590,480,528 bytes and 1,197,905,749 bytes.

## Temporary-pack content classification and reconstruction

The temporary files are not unrelated archive fragments. They are partial-write traces of two complete committed Git blobs. Byte-for-byte streaming showed:

- all 16 fragments in the 1,590,480,528-byte family have the same first 1 MiB as reachable blob `f4673c92f05b2bd00091cdc1f55d591dd38f5e1d`;
- all 11 fragments in the 1,197,905,749-byte family have the same first 1 MiB as reachable blob `74b03ee7833d285fd9085da912620b102da8222c`;
- each fragment's decompressed output is a strict prefix of the corresponding complete blob and has `zlib.eof=False`;
- the complete blobs are stored under `frozen_snapshots/evidence_content_addressed/` and are reachable from outer Git history.

Exact fragment-to-blob grouping:

| Complete blob | Temporary pack prefixes |
|---|---|
| `f4673c92f05b2bd00091cdc1f55d591dd38f5e1d` | `tmp_pack_NgWpHC`, `cfVZTG`, `aaxUyy`, `LFYhI3`, `PAm7ll`, `Xbax9v`, `J1wlbc`, `vWD2sV`, `ceaf2O`, `yXhl81`, `QUpvmK`, `2eX4Lm`, `WVtH6s`, `4Ai39J`, `s4C6xO`, `V2gV1t` |
| `74b03ee7833d285fd9085da912620b102da8222c` | `tmp_pack_NBj8L3`, `lDajVJ`, `QFyBzt`, `yWkvsx`, `oVsNmV`, `575QuG`, `juZEke`, `SwSn05`, `5ZWAg3`, `xpHtrT`, `2aPwhf` |

The complete first archive contains 29,126 tar members, including CSAW material, `development_dataset.json`, `test_dataset.json`, scripts, and a large `test/` tree. The complete second archive contains 9,734 tar members, including `agent/`, `analytics/`, `grading/`, `run_benchmark.py`, and 9,619 benchmark members spanning CTF/crypto/web/pwn/reverse datasets. These are retained benchmark/source datasets and experiment inputs, not automatically independent ACTS attack observations; they must remain in the evidence inventory and be linked to the campaigns that consumed them.

The temporary files are therefore classified as:

`GIT_PARTIAL_WRITE_PREFIX_OF_REACHABLE_COMPLETE_BENCHMARK_BLOB`

They must not be deleted. The prior classification as merely unrelated incomplete garbage was incorrect because it ignored the committed completion and the prefix relationship.

## Complete outer Git history

The complete indexed outer history was enumerated with `git rev-list --objects --all` and `git cat-file --batch-check`. It contained 4,827 reachable objects in the current refs. The largest complete blobs relevant to project evidence include:

- `frozen_snapshots/evidence_content_addressed/ad/...`: 1,590,480,528 bytes;
- `frozen_snapshots/evidence_content_addressed/26/...`: 1,197,905,749 bytes;
- `frozen_snapshots/evidence_content_addressed/b7/...`: 257,359,055 bytes;
- `frozen_snapshots/evidence_content_addressed/d7/...`: 105,463,776 bytes;
- `artifacts/experiment_inventory.json`: 54,170,064 bytes;
- `artifacts/inventory_snapshots/experiment_inventory_v1.json`: 54,169,904 bytes;
- `frozen_snapshots/evidence_content_addressed/36/...`: 43,092,102 bytes;
- `sp2027/agent-eval` transcripts and run records, including multi-megabyte JSONL transcripts.

The two largest complete content-addressed files correspond exactly to the two temporary-pack families. They were included in the non-`.git` outer file crawl, but the relationship to the temporary pack prefixes was not previously established. They must be counted as complete benchmark/data artifacts and deduplicated by content hash, not added as new observations for every temporary prefix.

## Unreachable/dangling object check

Read-only `git fsck --full --no-reflogs` found:

- 0 unreachable commits;
- 0 unreachable trees;
- 0 unreachable blobs;
- 30 dangling blobs;
- 27 garbage temporary packs, represented as the 28 non-object diagnostics in the fsck summary.

The 30 dangling blobs are small (largest 139,734 bytes) and their prefixes classify them as manuscript variants, results-lock JSON, audit notes, and analysis scripts. They do not expose a distinct large raw experiment archive. Because they are dangling, path attribution is unavailable from current Git refs; their object IDs and sizes were retained in the command output, but they are classified as historical/unindexed support artifacts pending any external lineage record.

## Scientific inventory consequence

The +27 GiB project size was not evidence that the nested `ACTS-ATTACK/` checkout itself contained 27 GiB of omitted files. It revealed a second scope boundary:

1. the nested repository is a 5.56 MB separate Git checkout and has been fully crawled;
2. the outer project contains approximately 7.4 GB of non-`.git` files, including the large frozen snapshots and full `sp2027/agent-eval` campaigns;
3. the outer Git database contains approximately 22 GiB, dominated by one normal pack, complete content-addressed frozen evidence, and 27 incomplete temporary pack fragments;
4. the temporary packs are partial writes of two complete, reachable benchmark blobs, so the benchmark data surface is now traced rather than dismissed;
5. the complete outer Git history confirms additional E2/E5 and artifact/capsule evidence already identified in the outer non-`.git` crawl, but does not make copied snapshots independent repetitions;
6. no claim about a new ACTS result family can be made from the benchmark archives alone without linking a benchmark member to a retained run record and oracle outcome.

## Read-status boundary

The complete outer Git object database was structurally inspected. All 27 temporary pack files were streamed through their Git zlib layer to establish prefix relationships; representative complete blobs were streamed through gzip/tar listing to EOF and their member inventories counted. Individual temporary prefixes were not manually interpreted as complete archives because they terminate before zlib EOF. This is a structural and archive-member inventory, not a claim that every benchmark source file was semantically reviewed.

## Status

`PARTIAL DISCOVERY — NAMED EVIDENCE GAPS`

The remaining gap is not an unexamined +27 GiB ACTS experiment tree. It is provenance resolution for duplicated complete frozen archives and dangling/garbage Git objects, followed by a final project-to-manuscript mapping. Raw repository state remains unchanged.
