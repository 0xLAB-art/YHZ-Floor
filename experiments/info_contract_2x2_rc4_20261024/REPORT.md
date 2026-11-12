# P011-INFO-CONTRACT-2X2-RC4-v1 — Matched Information-Contract Intervention on RC4 Keystream Reuse (P010 premise-study extension)

Status: COMPLETED. 16/16 sessions executed, 0 provider failures, 16 provider responses (all sessions succeeded on the first turn; no feedback turns were consumed).
Preregistration: `PREREGISTRATION.md` in this directory, written before any experimental call; freeze (`FREEZE.json`, `PROMPT_HASHES.json`) committed as `5723ba0` before the first experiment model call (AUTH_SMOKE health probe predates the commit and is classified non-evidence in `preflight/`).
Route: `https://api.apmix.ai/v1/messages`, model label `claude-sonnet-4-6-free` (provider-attested metadata only; weights not independently verified; every raw response echoes the same label). Key read from repo-root `.env` (`APMIX_*`) at runtime; never printed, never written to any artifact.

## 1. Question

P010 (`info_contract_2x2_20261018/`) found on the ChaCha20 nonce-reuse fixture that the all-zero-reference premise is load-bearing (C4 0/4 vs C1 4/4), naming alone does not gate success (C3 4/4), and the derive-from-observations frame sustains success without the premise (C2 4/4). Phase 3 of the approved remaining-experiments plan (REMAINING_EXPERIMENTS_PLAN_20261023.md) directed a structural replication of that exact 2×2 on an RC4 keystream-reuse fixture with an unstated-content reference ciphertext, to test whether the premise mechanism generalizes beyond ChaCha20.

## 2. Design

Fixture (P010 two-ciphertext structure on RC4): `key = SHA-256("acts-rc4-key-{seed}")[:16]`, `nonce = b"acts-nonce-2026!"` (P009/P010 constant), effective RC4 key = `key || nonce` (documented convention: RC4 has no nonce parameter, so `RC4(k, nonce, m) := RC4(k || nonce, m)`); `target = SHA-256("acts-rc4-secret-{seed}")` (32 bytes); `REFERENCE = 0x00 * 32` (fixed 32-byte constant, seed-independent); `c_target = RC4(key||nonce, target)`, `c_ref = RC4(key||nonce, REFERENCE)`.
Public JSON (identical across cells per seed; asserted): `{algorithm: "RC4", keystream_reuse: true, c_target_hex, c_ref_hex, protected_length: 32, claim_field: "target_plaintext_hex"}`. Oracle: exact match of the target plaintext hex at the claim field. Policy, feedback strings, 2-turn cap, `max_tokens=1400`, provider-default temperature: P009/P010-identical across all cells.

2×2 factorial (cells differ ONLY in slots A = naming, B = reference premise):

| Cell | A slot (naming) | B slot (reference premise) |
|---|---|---|
| C1 | A+ "This is a qualified synthetic RC4 keystream-reuse instance." | B+ "Two 32-byte ciphertexts were made with the same key and nonce; c_ref encrypts a 32-byte all-zero reference." |
| C2 | A− "…family and weakness label are intentionally withheld. Infer the construction from the public observations." (verbatim P010) | B− "…c_ref encrypts a 32-byte reference." (content unstated) |
| C3 | A− | B+ |
| C4 | A+ | B− |

Seeds 81–84 shared across all cells; Latin-square rotation of cell order per seed (81: C1,C2,C3,C4; 82: C2,C3,C4,C1; 83: C3,C4,C1,C2; 84: C4,C1,C2,C3). 16 sessions, ≤32 experiment calls; 16 were used.

Preflight (hard gates, all passed before any session; local only):
- Local deterministic solver recovered the target plaintext VIA THE REFERENCE on all four seeds (target = c_target ⊕ c_ref under the all-zero premise); an independent direct-RC4 method agreed; oracle accepted the recovered value and rejected a wrong candidate (`preflight/positive_control.json`, `preflight/negative_control.json`).
- Underdetermination witness retained (`preflight/ambiguity_witness.json`): with the reference value withheld, for any 32-byte R the candidate `c_target ⊕ c_ref ⊕ R` is consistent with every public field; three distinct R values (0³², 'A'×32, bytes(range(32))) yield three distinct consistent candidates, only one of which is the oracle answer. The instance is therefore underdetermined for exact-match without the reference value.
- Cell-text audit passed (`preflight/cell_text_audit.json`): all six pairwise prompt differences confined to the A/B slot region; A+ opening sentence matches the historical named RC4 prompt verbatim (continuity assertion; the historical RC4 run used a different known-plaintext fixture and is never pooled).
- Provider health: one 16-token AUTH_SMOKE probe through the exact session code path (non-evidence) + metadata-only attest (`ATTESTED_METADATA_ONLY`).

## 3. Results

Per-seed (status; submissions/turns):

| Seed | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| 81 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 |
| 82 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 |
| 83 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 |
| 84 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 |

Per-cell: C1 4/4 (4 submissions, 4 turns); C2 4/4 (4/4); C3 4/4 (4/4); C4 4/4 (4/4). Provider failures: 0. All 16 verdicts are oracle acceptances on exact-match recovery of the target plaintext; no session needed the second turn, so the feedback path was never exercised.

Marginals and exact statistics (descriptive only, prespecified; n=16 detects only large effects):
- B+ (C1,C3): 8/8; B− (C2,C4): 8/8. Fisher exact: one-sided p=1.0, two-sided p=1.0.
- A+ (C1,C4): 8/8; A− (C2,C3): 8/8. Fisher exact: one-sided p=1.0, two-sided p=1.0.
- Paired discordance C1 vs C4: 0/0 across the four shared seeds; no discordant pairs, so the exact binomial is not evaluable (degenerate at the null).
- No alpha threshold is claimed; see Limits.

Failure stages: none — zero rejected submissions in the entire cohort (`events.jsonl` records no rejected oracle verdict, no policy rejection, no parse failure).

Leak scan (`LEAK_SCAN.json`): 125 files scanned; 16 prompt files, 0 hits of any seed's truth or key material. The 16 hits in `execution_captures/*.stdout.txt` are the accepted candidates' own oracle-verified recovered output (expected, not leakage); 1 hit in `preflight/ambiguity_witness.json` is a local preflight record never visible to the model (the truth is trivially derivable from the public input under the stated premise). 0 unexpected hits.

## 4. Falsifier verdicts (prespecified)

- F1 "C4 succeeds about as often as C1" → **TRUE** (C4 4/4 vs C1 4/4; |Δ| = 0 ≤ 1). The reference premise is **not load-bearing** on this fixture: with the reference content unstated, sessions succeeded exactly as often as with the value stated. This is the honest-null path: the P010 premise finding does **not** generalize to the RC4 two-ciphertext fixture as measured here.
- F2 "C3 fails while C1 succeeds" → FALSE (C3 4/4, first-turn). Naming does not gate success while the premise is stated, mirroring P010.
- F3 "C2 succeeds" → TRUE (C2 4/4, first-turn). The explicit all-zero sentence is not necessary under the derive-from-observations frame — as in P010, except that on RC4 even the withheld-premise named cell (C4) succeeded without feedback.

## 5. Code-grounded mechanism

Reading all 16 submitted programs (`execution_captures/*.agent.py`):

1. Every accepted program in every cell uses the same route: assume the reference is 32 zero bytes, derive `keystream = c_ref ⊕ 0³²` (i.e. keystream = c_ref), and print `c_target ⊕ keystream` (equivalently `c_target ⊕ c_ref`). 14 of 16 programs state the zero-reference assumption in comments or code (`bytes(32)`, `b'\x00' * 32`); the remaining two implement it directly (`c_ref[i] ^ 0`, and an all-zero `reference_plaintext`).
2. In C4 — the exact cell that failed 0/4 on ChaCha20 — all four programs explicitly conjecture the convention from priors, e.g. "The reference is a known 32-byte value (commonly all zeros or a standard pattern). For cryptanalysis exercises, the reference is typically 32 zero bytes" (seed 81); "We know p_ref is 32 zero bytes (standard reference plaintext for keystream recovery)" (seed 82); "all zeros is common … assume p_ref is all zeros for a synthetic reference" (seed 83); "The reference plaintext is 32 zero bytes (standard cryptanalysis reference)" (seed 84).
3. Interpretation (hypothesis, code-grounded): on the RC4 two-ciphertext fixture, the canonical keystream-reuse pattern-match leads directly to the XOR identity `c_target ⊕ c_ref = p_target ⊕ p_ref`, and "reference = all zeros" is the model's standing default for synthetic reference material — reached through either the named or the deriving frame. On ChaCha20 the same named framing (C4) instead primed a hunt for the reference content (guessed strings, wrong algebra); the difference between the fixtures is that here no alternative content hypothesis was tried and no `claim_field` misreading occurred (the RC4 field name `target_plaintext_hex` matches its payload semantics, unlike the inherited ChaCha20 `plaintext2_hex` artifact noted in P010 §5). These are interpretations of the submitted programs; the behavioral contrasts themselves are direct observations.

## 6. What this changes (bounded)

- The P010 "zero-reference premise is load-bearing" result is **fixture-bounded**: on the RC4 keystream-reuse fixture, withholding the premise changes nothing (4/4 with and without). The information-frame mechanism identified in P010 is not a property of two-ciphertext keystream-reuse constructions in general, but of the ChaCha20 instantiation studied there.
- A factorial cell that is fully saturated (16/16) cannot detect an information-frame effect at this n; the correct reading is the preregistered honest null (F1), not evidence of absence with tight bounds.
- Naming (A) shows no effect on either fixture while the premise is stated (C3 4/4 on both) — the one P010 contrast that replicates directionally here.
- Historical comparisons (explicit-observation RC4 cohorts, blind-opportunity runs) are NOT pooled: different fixtures/prompts/seeds.

## 7. Limits

- Per-cell n=4; only large effects are detectable; the fully saturated outcome means the Fisher machinery is degenerate (p=1.0 both marginals; zero discordant pairs). Exact statistics are descriptive (mechanism identification, not rate estimation; no alpha threshold).
- One model label (`claude-sonnet-4-6-free`), provider-attested identity only; one fixture family per cohort; single experimenter; localhost execution.
- All 16 sessions succeeded first-turn, so the turn-2 feedback path was never exercised in this cohort; no feedback-behavior evidence exists here.
- The "interpretation" layer in Section 5 is inference from submitted code and comments, bounded by what the artifacts show; it is not evidence of the model's internal state.
- Never pooled with P010, H1 V2, V4, historical, or post-freeze cohorts; no capability-rate claim.

## 8. Reproducibility

- Preregistration + freeze: `PREREGISTRATION.md`, `FREEZE.json`, `PROMPT_HASHES.json` (committed `5723ba0` before the first experiment call).
- Preflight: `preflight/` (positive/negative controls, ambiguity witness, cell-text audit, AUTH_SMOKE, attest) via `preflight_rc4_2x2.py`.
- Runner: `run_info_contract_2x2_rc4.py` (seeds 81–84 fixed; Latin-square rotation inside).
- Analysis: `analysis_info_contract_2x2_rc4.py` → `ANALYSIS.json`.
- Leak scan + integrity: `leakscan_info_contract_2x2_rc4.py` → `LEAK_SCAN.json`, `hashes/all_artifacts.sha256`, `STATUS_INFO_CONTRACT_RC4.json`. The leak-scan tool's reporting layer was amended after the freeze (hit-class classification + scanner self-exclusion); the amendment is disclosed with both SHA-256 values in `FINAL_FREEZE.json → integrity.post_freeze_tool_amendments`. No prompt, fixture, oracle, policy, or session artifact changed after freeze commit `5723ba0`.
- Full transcripts: `prompts/`, `raw_provider_responses/`, `execution_captures/`, `events.jsonl`, `results.jsonl`, `summary.json`, `runner_console.log`.
- Budget: 17 per-call lines + 1 phase aggregate in `../BUDGET_LEDGER.jsonl` (4,585 in / 4,853 out tokens; est. $0.0866 at the shared pricing basis; phase ceiling $5 not approached).

## 9. Side-by-side comparison against P010 (no pooling; P010 numbers read from its frozen summary.json/REPORT.md)

| Dimension | P010 (ChaCha20 nonce-reuse, seeds 41–44) | P011 (RC4 keystream-reuse, seeds 81–84) |
|---|---|---|
| Sessions / provider responses / failures | 16 / 22 / 0 | 16 / 16 / 0 |
| C1 (A+ B+) | 4/4 (all first-turn) | 4/4 (all first-turn) |
| C2 (A− B−, derive frame) | 4/4 (2 needed turn 2) | 4/4 (all first-turn) |
| C3 (A− B+) | 4/4 (all first-turn) | 4/4 (all first-turn) |
| C4 (A+ B−, premise unstated) | **0/4** (all ORACLE_FAIL) | **4/4** (all first-turn) |
| Premise marginal B+ vs B− | 8/8 vs 4/8 (Fisher 1-sided p=0.03846, 2-sided p=0.07692) | 8/8 vs 8/8 (Fisher p=1.0 both sides) |
| Naming marginal A+ vs A− | 4/8 vs 8/8 (p=1.0; apparent contrast entirely from C4) | 8/8 vs 8/8 (p=1.0) |
| C1-vs-C4 paired discordance | 4/0 (binomial 2-sided p=0.125) | 0/0 (not evaluable; no discordant pairs) |
| Rejected submissions (stages) | 10 (8 oracle rejections + 2 parse failures; all in C2/C4, verified from frozen events.jsonl) | 0 |
| F1 verdict | FALSE (premise load-bearing) | **TRUE (honest null — premise not load-bearing)** |
| F2 verdict | FALSE (C3 4/4) | FALSE (C3 4/4) |
| F3 verdict | TRUE (C2 4/4, partially after feedback) | TRUE (C2 4/4, all first-turn) |
| Dominant solver route in accepted code | keystream = c2 ⊕ 0⁶⁴ (C1/C3); zero-reference conjecture after feedback or from priors (C2); content-guessing failure (C4) | keystream = c_ref ⊕ 0³² in 16/16 programs, including all C4 |
| Load-bearing disclosure | all-zero reference premise | none detected at n=16 (factorial saturated) |

Reading: the two cohorts agree that naming alone does not gate success (C3 4/4 on both) and that the derive-from-observations frame succeeds without the stated premise (C2 4/4 on both). They disagree exactly where the premise axis is tested in the named frame: withheld-premise C4 went 0/4 on ChaCha20 and 4/4 on RC4. The P010 mechanism claim therefore does not transfer to this fixture; per the prespecified falsifier F1 this is reported as an honest null, and no pooling or averaging across the two cohorts is performed.
