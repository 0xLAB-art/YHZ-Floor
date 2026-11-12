# REGRADE — explicit empty state

**The offline triple regrade was not run: there are no retained programs to
regrade.** Zero sessions were executed (`sessions/EMPTY_STATE.md`), so no
candidate program exists under any admission rule.

The regrade policy snapshots are **hash-referenced** from
`external_admission_20261024/policies/` per the phase instruction, recomputed
this phase with `sha256sum` and matching that namespace's `FREEZE.json`:

- (a) declared permissive rule — `rule_a_permissive_v3.py`
  sha256 `372bab44bc12ff6a377671516217f268e55132cda9d0304405d1c8619602df6f`
- (b) OUR counterfactual stress rule (legacy {json, sys, base64}) —
  `rule_b_stress_legacy.py`
  sha256 `257b7805a847729c29ebf2960b6d00d7a73845721459fbd3fd972b36c93a2891`
- (c) rule (b) + output-preserving unused-import cleanup —
  `rule_c_cleanup.py`
  sha256 `7419e861a4d1abeb5f9d7623ab2b4c4d79ef4647b7ea186639379771313a4373`

No policy file was copied or modified; the hashes pin the exact bytes that
would have governed the regrade had the grid run. Falsifier F3 (cleanup fails
output preservation) is NOT EVALUABLE for the same reason.
