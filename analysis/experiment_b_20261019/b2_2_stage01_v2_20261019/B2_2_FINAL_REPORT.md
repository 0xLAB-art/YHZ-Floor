# B2-2 Independent Reproducibility and Binding Audit v2

**Status:** completed offline in a new versioned directory; no provider/model/network calls.

## Scientific determination

- The frozen Stage01 validator and reference verifier reproduce the clean, A1, and A1b controls. These are reproducibility controls, not new findings.
- The original components accept the candidate/execution semantic mismatch when all outer evidence hashes are internally consistent.
- The external wrapper rejects that mismatch and accepts the matching positive control. This validates the wrapper check only; it does not repair Stage01.
- The established V3-full/IAR-B/IAR-C results were consumed read-only and were not rerun or adapted.
- Operational exploitability in the actual ACTS campaign is **not demonstrated**.
- Novelty is **not established** by B2-2.

## Case outcomes

| Case | Frozen validator | Independent reference | External binding wrapper | Outer hashes |
|---|---|---|---|---|
| `clean_control` | `ACCEPT` / public-evidence-consistent | `ACCEPTED` / predicate=True / integrity=True | `INCONCLUSIVE` / trace-has-no-candidate-hash | PASS |
| `a1_reproduction` | `ACCEPT` / public-evidence-consistent | `ACCEPTED` / predicate=True / integrity=True | `INCONCLUSIVE` / trace-has-no-candidate-hash | PASS |
| `a1b_reproduction` | `REJECT` / execution-session-binding | `REJECTED` / predicate=True / integrity=False | `INCONCLUSIVE` / trace-has-no-candidate-hash | PASS |
| `candidate_binding_mismatch` | `ACCEPT` / public-evidence-consistent | `ACCEPTED` / predicate=True / integrity=True | `REJECT` / semantic-candidate-execution-mismatch | PASS |
| `candidate_binding_match_control` | `ACCEPT` / public-evidence-consistent | `ACCEPTED` / predicate=True / integrity=True | `ACCEPT` / candidate-execution-bound | PASS |

### Interpretation of the binding cases

- `candidate_binding_mismatch`: frozen validator `ACCEPT`, reference `ACCEPTED`, outer hashes `PASS`, wrapper `REJECT semantic-candidate-execution-mismatch`. This is a genuine semantic mismatch result, not stale-hash rejection.
- `candidate_binding_match_control`: frozen validator `ACCEPT`, reference `ACCEPTED`, outer hashes `PASS`, wrapper `ACCEPT`. No false rejection was observed for the matching positive control.
- Clean and A1/A1b traces have no candidate hash. The wrapper correctly reports `INCONCLUSIVE`, not rejection; adding a field is not retroactively treated as a frozen-schema requirement.

## Frozen component integrity

- Validator SHA-256: `f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a`
- Reference verifier SHA-256: `15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b`
- External wrapper SHA-256: `2589c98c89fe965846995bf2d8ef6f400481715768fb89f22c165a22fd0f3c64`
- Protected manuscript/result-lock hashes unchanged: **True**
- Provider calls: 0; network calls: 0; spend: USD 0.00.

## V3-full authenticated-provenance baseline

The V3-full baseline is reported from established IAR-B/IAR-C artifacts, read-only. It was not rerun and no Stage01-to-V3 adapter was introduced.
- `/mnt/nvme5/ACTS-Attack/sp2027/analysis/experiment_b_20261019/iar_b/runs/20261019_112227/results.json` — exists=True, SHA-256 `032c93bedb65fec8cadd80d1ec2b0af5e6bb1e30ac4e30e6d105eb14eebcdf15`, mode: read-only established result; not rerun
- `/mnt/nvme5/ACTS-Attack/sp2027/analysis/experiment_b_20261019/iar_b_heldout/runs/20261019_114849/results.json` — exists=True, SHA-256 `be08433db0da8ded6bed2c5edc1730b11b204b828660c3775c0340c2b818f640`, mode: read-only established result; not rerun
- `/mnt/nvme5/ACTS-Attack/sp2027/analysis/experiment_b_20261019/iar_c/runs/20261019_121621/results.json` — exists=True, SHA-256 `7ad02c14f9328d82ccdfe3cdfbe7b0d0d88143b6f8393222701c7872187de785`, mode: read-only established result; not rerun

The preserved baseline reports V3-full results on its own `heb1-signed/1` contract: IAR-B dev 0 level-6 false promotions, IAR-B held-out 0, and IAR-C preserved 0; it accepted honest within-evidence claims without false rejection in the preserved comparisons. These results are established baseline evidence, not a B2-2 rerun.

## Read-only reachability assessment

The five actual contract-sound campaign runners were scanned with AST/text checks. No external certificate/bundle/evidence ingestion interface was detected; certificate construction is internal to the runners. Determination: **NOT_REACHABLE_IN_CURRENT_PIPELINE**. This is a source-reachability conclusion, not live exploitability proof.

| Runner | SHA-256 | External certificate input detected |
|---|---|---|
| `run_contract_sound_stage01.py` | `982978d1db85159f012f458a4d44a381e0c52e9622bbbcaf7841a2d9566ce158` | `False` |
| `run_contract_sound_stage01_hardened.py` | `f46395a309cddbd683aa74b045f0cc6a32295e790114694563310e2f7daa15a6` | `False` |
| `run_contract_sound_agent_pilot.py` | `144984fcfd778a0948f85002a8827c0411ddd92167c0e9a258173bd8d070587a` | `False` |
| `run_contract_sound_agent_pilot_free_v2.py` | `7c81945d3e6d26bc75f9ddb66eb47f875f86b10d02bbfea5b5bc03ead62b53b0` | `False` |
| `run_contract_sound_agent_replacement_v1.py` | `76f5b530a0a805e8dcbe3a44e23ae75fae1038103a5fc4a1d79e6bd9e850ad8d` | `False` |

## Gate results

| Gate | Result | Evidence |
|---|---|---|
| Frozen Stage01 controls preserved | PASS | Original files invoked by subprocess; component hashes recorded |
| Clean/A1/A1b reproduction | PASS | Raw stdout/stderr and return codes retained per case |
| Semantic mismatch separated from SHA corruption | PASS | Outer evidence and candidate hashes all match in mismatch case |
| Matching positive control / false rejection check | PASS | Wrapper ACCEPT on matching candidate hash |
| Original Stage01 semantic binding enforcement | FAIL/ABSENT | Mismatch accepted by original validator and reference |
| V3-full comparison | PASS as read-only baseline | Existing IAR-B/IAR-C results consumed, no rerun |
| Current campaign reachability | PASS | No external certificate-composition interface found |
| Protected files unchanged | PASS | Before/after hashes equal expected values |

## Limitations and next action

B2-2 reconfirms the known acceptance boundary and validates a separately identified wrapper. It does not establish a new attack path, does not prove operational exploitability, and does not demonstrate superiority over V3-full because V3-full was evaluated on a different authenticated input contract. The next discriminating experiment requires an actually reachable authorized submission gateway that accepts externally composed evidence and invokes the frozen campaign verifier; absent that interface, more synthetic Stage01 relabeling is redundant.
