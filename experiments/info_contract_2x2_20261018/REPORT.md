# P010-INFO-CONTRACT-2X2-CHACHA20-v1 — Matched Information-Contract Intervention (ChaCha20 Nonce-Reuse)

Status: COMPLETED. 16/16 sessions executed, 0 provider failures, 22 provider responses.
Preregistration: `PREREGISTRATION.md` in this directory, written before any experimental call (preflight wire probes recorded separately under `preflight/`).
Route: `https://api.apmix.ai/v1/messages`, model label `claude-sonnet-4-6-free` (provider-attested metadata only; weights not independently verified). Key never logged.

## 1. Question

The synthesis identified one missing causal-tier intervention (S12): an arm changing ONLY
the prompt-level information frame — (a) whether the zero-reference premise is stated,
(b) whether the family/weakness is named — while preserving observations, target, seeds,
budget, interface, provider, predicate, and turn flow. The earlier reduced-prompt
(blind-opportunity) runs changed several dimensions at once and could not isolate the
load-bearing sentence. This experiment provides the matched 2x2 decomposition.

## 2. Design

Fixture (P009 semantics, unchanged): ChaCha20, same key/nonce for two 64-byte ciphertexts;
`c2 = ChaCha20(key, nonce, 0x00 * 64)`; `public = {algorithm, nonce_reuse, c1_hex, c2_hex, protected_length, claim_field:"plaintext2_hex"}`.
Oracle predicate (unchanged): candidate JSON value at `plaintext2_hex` must equal the hex of P1
(the plaintext of c1) — exact match. Feedback strings, policy allowlist, 2-turn cap,
max_tokens=1400, and provider-default temperature are P009-identical across all cells.

2x2 factorial (cells differ ONLY in slots A and B):

| Cell | A slot (naming) | B slot (reference premise) |
|---|---|---|
| C1 | A+ "This is a qualified synthetic ChaCha20 nonce-reuse instance." | B+ "Two 64-byte ciphertexts were made with the same key and nonce; c2 encrypts a 64-byte all-zero reference." |
| C2 | A− "The public JSON contains a qualified synthetic cryptographic recovery instance, but the family and weakness label are intentionally withheld. Infer the construction from the public observations." | B− "…c2 encrypts a 64-byte reference." (content unstated) |
| C3 | A− | B+ |
| C4 | A+ | B− |

C1 reproduces the historical default prompt byte-for-byte (verified in the preflight cell-text
audit). C2 is the historical blind wording plus one neutral sentence ("c2 encrypts a 64-byte
reference"), because the historical blind prompt omitted the B slot entirely; the historical
blind run (seeds 7–8, 0/2) is retained as out-of-design corroboration and is NOT pooled here.

Seeds 41–44 shared across all cells; Latin-square rotation of cell order per seed
(41: C1,C2,C3,C4; 42: C2,C3,C4,C1; 43: C3,C4,C1,C2; 44: C4,C1,C2,C3). 16 sessions, ≤32 calls.

Preflight (before any session): local deterministic solver recovered P1 for all four seeds
via two independent methods (XOR identity c1⊕c2=c1 when B+ true, and direct decrypt), oracle
accepts recovered; wrong candidate rejected; cell-text audit passed (C1 == historical default
byte-for-byte; pairwise diffs confined to the A/B slots); provider wire probe + attest
recorded separately, not part of the dataset.

## 3. Results

Per-seed (status; submissions/turns):

| Seed | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| 41 | SUCCESS 1/1 | SUCCESS 2/2 | SUCCESS 1/1 | ORACLE_FAIL 2/2 |
| 42 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 | ORACLE_FAIL 2/2 |
| 43 | SUCCESS 1/1 | SUCCESS 1/1 | SUCCESS 1/1 | ORACLE_FAIL 2/2 |
| 44 | SUCCESS 1/1 | SUCCESS 2/2 | SUCCESS 1/1 | ORACLE_FAIL 2/2 |

Per-cell: C1 4/4 accepted (4 submissions, 4 turns); C2 4/4 (6 subs, 6 turns); C3 4/4
(4 subs, 4 turns); C4 0/4 (8 subs, 8 turns). Provider failures: 0.
All accepted verdicts are oracle acceptances on exact-match recovery of P1.

Marginals and exact statistics (descriptive only, prespecified; n=16 detects only large effects):
- R+ (C1,C3): 8/8; R− (C2,C4): 4/8. Fisher exact: one-sided p=0.03846, two-sided p=0.07692.
- N+ (C1,C4): 4/8; N− (C2,C3): 8/8. Fisher one-sided p=1.0 (the apparent naming contrast is
  entirely the C4 (R−,N+) cell; within R+, C1 and C3 are both 4/4).
- Paired discordance C1 vs C4: 4/0 across the four shared seeds; exact binomial two-sided p=0.125.
- No alpha threshold is claimed; see Limits.

Failure stages (from retained events; consistent with ANALYSIS.json):
- C2: 1 oracle rejection (seed 41, turn 1) + 1 execution/parse failure (seed 44, turn 1; KeyError —
  the program tried to read `plaintext2_hex` from the public input, which does not contain it).
- C4: 7 oracle rejections + 1 execution/parse failure (seed 44, turn 1; IndexError — the guessed
  reference was shorter than 64 bytes under `p2[i]` indexing).

Leak scan (`LEAK_SCAN.json`): 149 files scanned; 22 prompt files, 0 hits of any seed's truth or
key material — prompts are leak-free. The 12 hits in `execution_captures/*.stdout.txt` are the
accepted candidates' own recovered output (the oracle-verified answer printed by the program);
they are expected recovered-output occurrences and are NOT leakage. C4 (0 accepted) has no stdout
hits, and no rejected submission's stdout contains the truth.

## 4. Falsifier verdicts (prespecified)

- F1 "C4 succeeds approximately as often as C1" → FALSE (C4 0/4 vs C1 4/4). The reference
  premise is not neutral for the named framing; its removal is associated with total failure in
  this cell.
- F2 "C3 fails while C1 succeeds" → FALSE (C3 4/4, first-turn). Naming (A) alone does not gate
  success while the zero-reference premise is stated.
- F3 "C2 succeeds" → TRUE (C2 4/4). The explicit all-zero sentence is not necessary for success:
  under the fully withheld framing the model still succeeds — via the zero-reference convention,
  partially after feedback.

## 5. Code-grounded mechanism

Reading all 20 submitted programs (16 sessions; 22 submissions incl. rejections):

1. When the zero-reference premise is stated (C1, C3 — regardless of naming), every accepted
   program uses it directly: `p2 = bytes(64)`, `keystream = c2 ⊕ p2`, `p1 = c1 ⊕ keystream`
   (or the direct reduction `p1 = c1 ⊕ c2`, with comments citing the all-zero premise).
   All 8 sessions succeed on the first turn.
2. When the premise is withheld but the framing says "infer the construction from the public
   observations" (C2), the model conjectures the zero-reference convention from cryptanalysis
   priors: explicit comments such as "Common reference: all zeros… Most likely for cryptanalysis
   exercises: 64 zero bytes" appear in first-turn programs that solve directly (seeds 42, 43).
   The two C2 sessions that failed first (wrong textual-reference guess, seed 41; KeyError bug
   hoping the input supplied the answer, seed 44) succeeded on turn 2 by collapsing to printing
   `c1 ⊕ c2` directly — which is correct precisely because P2 is all zeros.
3. When the framing names the family but states the reference exists with unstated content
   (C4), behavior flips: first-turn programs attempt to GUESS the reference content
   (`b'A'*64`, or sentence-like strings), which fails under exact-match; turn-2 programs do not
   recover the convention — two print `c1` (algebra error `c2 ⊕ (c1 ⊕ c2)`), one prints the
   zero reference candidate instead of P1 after otherwise correct reasoning about
   `claim_field:"plaintext2_hex"` (seed 43), one retries a different content guess.
   Accepted count 0/4; all four failures are construction-level, not provider-level.
4. Interpretation (hypothesis, code-grounded): the naming sentence "qualified synthetic
   ChaCha20 nonce-reuse instance" primes the canonical nonce-reuse pattern-match, whose classic
   form requires a KNOWN plaintext — so the model hunts for the reference content instead of
   deriving it from the observation structure; the "infer from the public observations"
   instruction primes derivation from scratch, where the zero-reference convention is the
   natural hypothesis. The field name `plaintext2_hex` (holding P1's hex on acceptance) is an
   inherited P009 naming artifact, identical across cells; it produced exactly one visible
   reasoning flip (C4 seed 43, turn 2). These are interpretations of the submitted programs;
   the behavioral contrasts themselves are direct observations.

## 6. What this changes (bounded)

- The zero-reference premise is the load-bearing disclosure: stating it yields immediate,
  robust construction (8/8 first-turn across naming conditions).
- Its omission is NOT a simple gate: under a "derive-it" framing, success persists (4/4) via
  the zero-reference convention, at higher submission cost (6 vs 4 submissions).
- A partially framed disclosure — naming the family while positing an unstated reference —
  was the worst condition (0/4), indicating that evaluator prompts can actively mislead by
  framing a gap without supplying its resolution. This sharpens the project's central finding:
  beyond opportunity and capability, the exact information frame of the task controls which
  programs the agent attempts; "withholding" and "framing a gap" are different interventions.
- Historical comparisons (blind-opportunity seeds 7–8, 0/2 under a fully withheld prompt with
  no B slot) are NOT pooled: different seeds, different exact wording. They remain a separate
  bounded observation.

## 7. Limits

- Per-cell n=4; only large effects are detectable; exact statistics are descriptive
  (preregistered as mechanism identification, not rate estimation; no alpha threshold).
- One model label (`claude-sonnet-4-6-free`), provider-attested identity only; one fixture
  family, one local execution contract, single experimenter.
- The "interpretation" layer in Section 5 is inference from submitted code and comments,
  bounded by what the artifacts show; it is not evidence of the model's internal state.
- No pooling with H1 V2, V4, historical, or post-freeze cohorts; no capability-rate claim.
- The `plaintext2_hex` field-name artifact is inherited (held constant across cells).

## 8. Reproducibility

- Preregistration: `PREREGISTRATION.md` (committed before calls).
- Runner: `../run_info_contract_2x2_chacha20.py` (env `ACTS_SEEDS`, default 41–44).
- Analysis: `../analysis_info_contract_2x2.py` → `ANALYSIS.json`.
- Leak scan + integrity: `../leakscan_info_contract_2x2.py` → `LEAK_SCAN.json`,
  `hashes/all_artifacts.sha256`, `STATUS_INFO_CONTRACT.json`.
- Full transcripts: `prompts/`, `raw_provider_responses/`, `execution_captures/`,
  `events.jsonl`, `results.jsonl`, `summary.json`, `runner_console.log`.
- Preflight: `preflight/` (positive/negative controls, cell-text audit, wire probes, attest).
