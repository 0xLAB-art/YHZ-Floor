# Finding: the Amendment-3 null decomposes into three measured layers

**Scope.** Post-hoc audit of the FROZEN Amendment-3 artifacts (`results.jsonl`
freeze commit `a5283b3fbaebe8323637c1dedbe951530ce222c3`). Zero model calls,
zero network, zero changes to the registered verdicts. Audit script:
`audit_null_decomposition.py` (v2) → `AUDIT_NULL_DECOMPOSITION.json`
(schema `amend3-null-decomposition-audit/2`).

## 0. Audit correction disclosure (v1 → v2)

The first pass of this audit reported "all 84 RT blobs strict-b64-invalid" and
suspected broken RT delivery. **That was an audit-regex bug, not a harness
defect**: the extraction regex captured the `DECODE NOTE:` prose line together
with the base64 payload, so the "blob" contained punctuation and decoded to
garbage. v2 parses the blob as the base64 lines *after* the note and verifies
**84/84 RT prompts decode byte-exact to the original artifact files**
(independently reproducing the build-time gate `decode_equality_log.json`,
which recorded `equal: true` per task). RT delivery was correct; the suspicion
is withdrawn. The crash label "(RT path)" from v1 is likewise replaced by the
measured model idioms below.

## 0b. Audit correction disclosure (v2 → v3)

Two defects found by the 2026-11-06 re-audit, both fixed in v3:

1. **Per-arm aggregation bug.** v2's `task_arm_decomposition` table tested
   session dicts for membership in 6-key layer-record lists (`if r in layer1`),
   which is always False — every arm printed `solved=0 / crashed=0 /
   wrong=n`, including eps R0 (which must read 11 any-turn / 8 terminal),
   contradicting v2's own summary block. v3 keys the aggregation by run_id.
2. **Counting rules now stated explicitly.** v2's layers mixed two rules
   without saying so: the crash layer counted a session as "crashed" if ANY
   turn had a nonzero returncode, while the decomposition's purpose is
   terminal-outcome accounting. v3 reports both rules side by side:
   - **any-turn** (mirrors the benchmark's own flag-in-output diagnostic,
     `scripts/flag_in_output.py` in the pinned nyuctf_agents harness, which
     scores a solve whenever the flag appears as a substring in ANY produced
     message): **11** flag-bearing sessions / **120** sessions with ≥1 crash /
     **25** rest;
   - **terminal** (the final submitted program only — the registered oracle
     scores the submitted candidate): **8** flag-bearing / **103** terminal
     crashes (48 on the b64-idiom per the final turn's own stderr, 45 other,
     9 overflow, 1 missing artifact) / **45** rest (34 clean no-flag runs,
     9 timeouts, 2 give-ups).
   The 3-session gap between 11 and 8 is qwen eps-R0 seeds 417–419: each
   solved on turn 1 (rc=0, stdout = flag + narrative) and lost the flag on a
   turn-2 revision that crashed (rc=1, empty stdout). Both sums equal 156.
   The benchmark's PRIMARY metric — an exact-string CheckFlag tool submission
   (`tools.py`) — has no counterpart in this harness; only the substring
   diagnostic is benchmark-native here.

## 1. The decomposition (156 content sessions; both rules sum to 156)

| layer | any-turn | terminal (final submitted) | what it is |
|---|---|---|---|
| 1 — flag-bearing, pin-rejected | **11** | **8** | statement-faithful outputs **rejected by the answer pin** (the 3-session gap: qwen eps-R0 417–419 solved turn 1, turn-2 revision crashed) |
| 2 — crash floor | **120** (≥1 crashed program) | **103** (final program crashed; no CRASH class — crashes masquerade as ORACLE_FAIL) | terminal modes by the final turn's stderr: 48 b64-idiom / 45 other / 9 overflow / 1 missing artifact; event-level attribution: 58 / 49 / 12 / 1 |
| 3 — delivery | — | — | **no defect** (84/84 byte-exact; both arms also hold the artifact file in the working directory) |
| remainder | **25** | **45** (34 clean no-flag runs + 9 timeouts + 2 give-ups) | |

Layer-1 spread: all 11 on `2015q-cry-eps`, all R0, **all three labels**
(gpt-6-luna 3, qwen-3.8-max 4, deepseek-v4.1-flash 4) — not one model's quirk.

## 2. Layer 1 mechanism: the task statement and the answer pin disagree

- Task statement (verbatim, benchmark metadata): *"Note: The flag is the
  entire thing decrypted"*.
- Pinned answer (`oracle/answers.json`): only the token
  `flag{People always make the best exploits.}`.
- Registered oracle (runner): `stdout.strip() == pinned answer` — the **entire
  stdout** must equal the token exactly.
- The benchmark's own reference solver (criterion-5) semantics: *first
  flag-shaped token* in the decoded text.

The 11 programs decoded the real `eps1.1` MPEG bit artifact and printed the
entire decryption — the flag token **plus** the Mr. Robot narrative the
artifact actually contains. That is exactly what the statement asks for and
exactly what the artifact yields; the oracle's whole-stdout rule then rejects
it. Under the reference solver's own first-token semantics these are **11
solves**. So the registered F1 verdict (0 oracle-correct) is an artifact of an
output-contract mismatch, not evidence that no model solved anything.

## 3. Layer 2 mechanism: what the crashes actually are

| mode | event-level (any turn; 120 sessions with ≥1 crash) | terminal (final submitted program; 103) |
|---|---|---|
| `b64decode(...).decode()` applied to a payload that is deliberately not UTF-8 text (model idiom) | 58 | 48 |
| int too large in bit decode (model idiom) | 12 | 9 |
| other (non-empty stderr) | 49 | 45 |
| missing artifact file | 1 | 1 |

All seven task artifacts are printable UTF-8 — **the harness never delivered
binary**. The dominant crash is a model-side idiom: decode one base64 layer,
then `.decode()` the *encrypted/binary payload* as text.

### 3a. The eps R0→RT collapse (11/12 → 0/12) is real and mechanistic

Same artifact bytes in both arms (build-gate verified). R0 embeds the artifact
verbatim (plain bits text); RT embeds the same bytes as base64 with an explicit
DECODE NOTE. Result:

- **R0: 11/12 normalization-rejected solves.**
- **RT: 0/12; all 12 sessions crash identically.** All 21 retained eps-RT
  programs **read the working-dir FILE — whose content is visibly plain
  `0110…` bits — and base64-decode its content anyway.** Because `0` and `1`
  are valid base64 alphabet characters, `b64decode(validate=False)` accepts
  the digits and yields garbage bytes; the subsequent `.decode()` crashes.

The DECODE NOTE — scaffolding meant to *help* — installed a false premise
about the artifact's encoding that **overrode the file's self-evident
content**. This is an authority-over-evidence failure induced by the prompt's
information contract: the paper's central thesis (the prompt owns the number)
reappearing *inside* the external cohort, as the mechanism behind its only
representation contrast.

### 3b. babycrypto near-solves: one layer short

7 sessions' stdout is the **decrypted plaintext with every byte XOR 0xFF**
(e.g. `\x93\x96\x8b…` → `lity algorithm…`). The decryption pipeline ran
correctly to within one final affine layer. The null is robust — a near-solve
is not a solve under any registered normalization — but the cohort was not
"making nothing": it was one transformation away.

## 4. What this changes (and does not change)

**Unchanged.** Registered verdicts F1 (FALSE, all labels), F2 (TRUE), F3
(PASSED) stand as registered: 0 accepted under the registered rule, quorum met,
no oracle leakage (the 18 stdout occurrences of the pin all originate from the
artifact itself — the R0 fixture decodes to byte-identical text, so
memorization remains excluded).

**Sharpened.** The external null is now a *decomposed* null with three named,
measured components rather than a single flat zero:

1. an **output-contract artifact** (11 statement-faithful flag outputs — 8 at
   the final submission — appear under the benchmark's own flag-in-output
   diagnostic);
2. a **crash floor the status taxonomy hides** (103 of the 145 ORACLE_FAIL
   sessions' final programs crashed; 120 sessions crashed at least once; the
   taxonomy needs a CRASH class);
3. a **measured representation effect** (the base64 wrapper), whose mechanism
   is itself an information-contract phenomenon.

**No new wave is registered.** Per the standing no-new-experiments directive,
this is a reading of existing frozen data only. If the authors later want a
registered follow-up (dual-coded oracle + CRASH status class), that is a new
amendment, not an edit of this one.

## 5. Paper-relevant one-liners (for the authors' own use; paper untouched)

- *"Under the benchmark's own flag-in-output diagnostic (solve = the flag
  appears in any produced message), the external cohort contains 11
  flag-bearing sessions — 8 at the final submission — all rejected by a
  whole-stdout exact-match rule stricter than the benchmark's reference
  solver; the benchmark's primary metric, an exact-string check-flag tool,
  has no counterpart in our harness."*
- *"103 of the 145 external ORACLE_FAIL sessions ended in a crash the status
  taxonomy hides (120 crashed at least once)."*
- *"One added layer of base64 encoding — with a helpful decode note — took the
  only solvable external task from 11/12 to 0/12 (8/12 at the final
  submission): every model trusted the note over the file it had just read."*
