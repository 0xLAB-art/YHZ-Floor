# R10: A1 sample-count support

Disposition: **addressed**. Current main text/table and both artifact-detail rows no longer say WSL2 retained90,000 valid samples. VMware explicitly reports n_valid=90,000; WSL2 describes ten trials and10,000 rounds with phase aggregates, not a comparable trimmed-valid-sample census. Retained z/ASR observations and the noncausal environment/build boundary remain.

The trace checks current primary JSON and both reachable Git revisions of the named WSL2 path. Neither version supplies n_valid. Four checks pass, with file/blob hashes and commit identities. This is support for removing the repeated count, not proof of an invented alternative count. The nested harness correction note identifies the later discovery-summary error without rewriting raw JSON or frozen historical reports.

The20-check preservation/reporting regression and13/5/18 page builds pass. No multiplication of block, round, key and trial units was substituted for missing observation metadata.
