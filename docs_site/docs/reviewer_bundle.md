# reviewer_bundle — the curated offline projection

This directory is the **review-facing projection** of the audit: 24,023 payloads whose
SHA-256 values are pinned in [`MANIFEST.json`](https://github.com/0xLAB-art/YHZ-Floor/blob/main/reviewer_bundle/MANIFEST.json), with every source→destination
copy recorded in [`COPY_LINEAGE.json`](https://github.com/0xLAB-art/YHZ-Floor/blob/main/reviewer_bundle/COPY_LINEAGE.json) (byte-preserving packaging — no
trial was added or removed). The full codes+results tree is manifested separately in the
[v1.0.0 release](https://github.com/0xLAB-art/YHZ-Floor/releases/tag/v1.0.0-codes-results).

## Verify without executing anything

```sh
python3 -B offline_checks.py verify     # SHA-256 over all 24,023 payloads
python3 -B offline_checks.py census     # the frozen verdict rows, read-only
```

Expected: `integrity: PASS`, 0 errors. These checks never run an attack program and
never contact a provider.

## Layout

| Path | What it is |
|---|---|
| `offline_checks.py` | the no-execution verifier (`verify`) and census (`census`) |
| `MANIFEST.json` | SHA-256 per payload — the projection's integrity envelope |
| `COPY_LINEAGE.json` | source→destination hashes for every byte-preserving copy |
| `ANONYMITY_SCOPE.json` | the direct-identifier scan result (0 hits; empty author fields) |
| `evidence/fixed_executor/` | the fixed-executor operation records: twelve historical recorded successes (RC4 0.214196 ms, ChaCha20 0.131647 ms, CBC 1981.556789 ms, ECDSA 6.956233 ms executor-clock medians). These are recorded observations; a different later file with the same basename has different clocks and is deliberately **not pooled** with this cohort. |
| `h1r3/h1r3_complete_replay_v1/` | the complete 852-session H1-R3 component: retained programs, fixture state, prompts, outputs, and the sandboxed `execute_replay.py` |
| `source/sp2027/` | the wave trees the manuscript cites (`research_execution/` — the external-boundary waves including the M1 audit; `analysis/` — the ablation and remediation trees) |

## What this projection is — and is not

- **Byte-preserving copies, not fresh execution.** The retained records (preregistrations,
  amendments, `results.jsonl` rows, per-session prompts and outputs) are verbatim copies of
  the frozen campaign files. Executing retained programs checks their outputs; it does not
  regenerate model responses. No experimental evaluation was run while preparing this
  projection.
- **The external-boundary evidence ships as the frozen records**: the Amendment-1 regrade
  lab, the Amendment-3/4/5 admission records, the C1 confirmatory review, and the M1
  published-protocol audit (namespace `external_published_audit_20261110`) — including the
  registered preregistrations, the numbered amendments, the `ERRATUM_accepted_c2` record,
  and `M1_FINAL_RESULTS`. These are the records behind the manuscript's external-boundary
  numbers and the allowance-dependence finding.
- **Constructed cases, bounded claims.** The ablation trees establish bounded policy
  behaviour on constructed cases — not deployed failure prevalence, and not an independent
  replication of any benchmark.
- **Deliberately excluded:** identifying signed RQ3 property certificates, their observation
  records, original provider/archive wrappers, declared-author LaTeX sources, and
  identifying in-toto runner sources remain in the private full candidate. Their exclusion
  preserves the signed originals without redaction or re-signing, so this projection does
  not independently reproduce every property-check and in-toto claim.
- **Synthetic fixture truth and test signing keys** included here are evaluation materials,
  not credentials to anything.
