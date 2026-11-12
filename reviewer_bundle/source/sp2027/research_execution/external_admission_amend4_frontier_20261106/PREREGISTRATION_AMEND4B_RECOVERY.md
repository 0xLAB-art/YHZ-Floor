# PREREGISTRATION — Amendment 4b: floor-recovery wave (8400)

**Protocol:** PHASE2-EXTERNAL-ADMISSION-AMEND4B-RECOVERY-v1 · **Namespace:** same `external_admission_amend4_frontier_20261106` · **Registered:** 2026-11-06, BEFORE the Amendment-4 primary pass completes and BEFORE any recovery call.

## 1. Motivation (disclosed)

The primary pass (4200-token floor, registered) is producing floor-exhausted
sessions: every AGENT_GIVEUP session examined shows `stop_reason=length`,
empty text, and `output_tokens == 4200` exactly, on both turns — the P023/P026
hidden-deliberation mechanism on the computationally harder tasks (the XOR
tasks and crack_me), while eps and lowe complete within 4200. This mirrors
the project's registered precedents: P026 (floor 4200→8000 dose-response) and
P024 (registered re-run of a floor-limited design at the doubled floor).

## 2. Registered selection rule (deterministic; no outcome cherry-picking)

A session enters the recovery wave iff **all** of:
1. its primary-pass terminal status is `AGENT_GIVEUP`; and
2. every recorded turn has `stop_reason == 'length'` with empty text
   (the floor-exhaustion signature — no format-mismatch or refusal giveups
   are eligible); and
3. its (label, task, representation, seed) slot produced no accepted
   program in the primary pass.

The set is whatever the primary pass produces under this rule; the rule was
fixed before the primary pass finished and before any recovery call.

## 3. Recovery design (everything byte-identical except the floor)

- Same label, task, representation, seed; same frozen prompts, artifacts,
  oracle answers, sandbox, execution, parser, feedback string, transport,
  route-default temperature (prereg amendments 1–2).
- **`max_tokens = 8400`** per call (the P024-registered doubled floor;
  uniform across labels, tasks, representations, turns).
- ≤2 turns, identical feedback flow; fresh model calls (new sessions,
  run ids suffixed `__rec8400`), **never overwriting** primary rows; both
  primary and recovery rows are retained and reported side by side.
- Both oracle codings (C1 primary, C2 second admissible normalization) and
  the CRASH class apply unchanged.

## 4. Registered readings

- **Floor-sensitivity (dose-response):** exhaustion rate at 4200 vs 8400 on
  the same (label, task, representation, seed) cells — the external-task
  anchor for the P026 external counterpart.
- **Recovered capability:** among recovered sessions, C1/C2 acceptance and
  the admission regrade (declared vs stress) on the recovered programs,
  computed under both codings — reported beside, never pooled with, the
  primary-pass verdicts.
- **Budget:** the recovery wave carries its own output-token ledger lines
  (`classification: recovery call`) under the same namespace; ceiling
  2,500,000 output tokens for the wave, enforced live.

## 5. Boundary

The primary pass's registered verdicts (F1/F2/F3 under both codings, at
floor 4200) are quoted unchanged. The recovery wave measures the floor
owner's share and recovers capability signal on the exhausted cells; it is
not an amendment of the primary design and no number mixes the two floors.
