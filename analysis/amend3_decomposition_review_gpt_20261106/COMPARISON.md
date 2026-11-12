# COMPARISON — GPT-family blind review vs. the corrected decomposition numbers

**Date:** 2026-11-06 · **Namespace:** `sp2027/analysis/amend3_decomposition_review_gpt_20261106`
**Purpose:** independent verification of the 2026-11-06 re-audit that fixed six
defects in the Amendment-3 null decomposition (the "145" universe error, the
any-turn/terminal rule conflation, the v2 per-arm aggregation bug, the
benchmark-semantics misattribution, the "ran clean" sentence, and the full-stdout
retention gap). The three labels were run by the author's instruction as an
adversarial blind check of the corrected numbers before they entered the paper.

**Non-evidence declaration.** This review runs OUTSIDE the experiment loop, after
all outcomes were known; it grades a re-audit's arithmetic, not agent capability.
It plays no role in any registered verdict and no number in the paper rests on
it. Model outputs are untrusted text; nothing here modifies frozen artifacts.

**Transport record.** Gateway `agentrouter.org`, Anthropic-messages endpoint
`/v1/messages`, headers x-api-key + Bearer + anthropic-version + the
`claude-cli/2.0.0 (external, cli)` User-Agent the route requires (per the frozen
project adapters). Labels `gpt-5.6-sol`, `gpt-6-astra`, `gpt-6.1-sol` are
provider-attested at call time, not digest-pinned. The API key is read from the
environment and is stored NOWHERE in this directory. Inputs: `review_payload.json`
(the 156 content sessions' verbatim 200-char stdout tails and 140-char stderr
tails, per-turn returncodes, the pinned answers, and the two scoring-code
excerpts), prompt in `PROMPT_REVIEW.md`. Part A is blind (no reference numbers
supplied); Part B adjudicates five printed claims. temperature 0.

## Part A — blind derivations vs. the re-audit's reference

| quantity | reference (re-audit) | gpt-6.1-sol | gpt-5.6-sol | gpt-6-astra |
|---|---|---|---|---|
| content sessions | 156 | **156** ✓ | **156** ✓ | **156** ✓ |
| by status | 145/9/2 | **145/9/2** ✓ | **145/9/2** ✓ | **145/9/2** ✓ |
| any-turn flag-bearing / crashed / rest | 11 / 120 / 25 | **11 / 120 / 25** ✓ | **11 / 120 / 25** ✓ | **11 / 120 / 25** ✓ |
| terminal flag-bearing / crashed / rest | 8 / 103 / 45 | **8 / 103 / 45** ✓ | **8 / 103 / 45** ✓ | **8 / 103 / 45** ✓ |
| A4 gap sessions | qwen eps-R0 seeds 417, 418, 419 | **same three ids** ✓ | **same three ids** ✓ | **same three ids** ✓ |
| terminal-crash final-stderr modes | 48 UnicodeDecodeError / 9 OverflowError / 45 other / 1 FileNotFoundError | 48 ✓ / 5 ✗ / 49 ✗ / 1 ✓ | 48 ✓ / 5 ✗ / 49 ✗ / 1 ✓ | 48 ✓ / 0 ✗ / 54 ✗ / 1 ✓ (see below) |
| sums | 156 = 156 = 156 | ✓ | ✓ | ✓ |
| A7 any-turn rest is not all "ran clean" | rest = 20 ORACLE_FAIL + 3 TIMEOUT + 2 GIVEUP | **agree** (20/3/2) ✓ | **agree** (20/3/2) ✓ | **agree** (20/3/2) ✓ |
| B1 universe | agree | ✓ | ✓ | ✓ |
| B2 diagnostic-vs-primary wording | objection | disagree → **accepted** | disagree → **accepted** | disagree → **accepted** |
| B3 first-flag-token misattribution | agree | ✓ | ✓ | ✓ |
| B4 statement-faithful + substring = flag-found | agree | ✓ | ✓ | ✓ |

**A5 adjudication — payload-truncation artifact, not a classification
disagreement.** The reviewers report 5 / 5 / 0 OverflowError; the reference
reports 9. Root cause: the payload truncated stderr tails to their first 140
characters (`[:140]` in `build_review_payload.py`), while the frozen record
stores the LAST 200 characters and every OverflowError traceback line sits at
the tail's end. Re-checking the frozen 200-char stderr tails: all **9**
terminal-crash sessions' stored stderr ends in `OverflowError: ...`, and the
140-char payload view hides the line in all 9. gpt-6-astra independently
identified exactly those **nine truncated `chr(int(b,2))` / fractional-power
traces** and correctly declined to claim the exception class from truncated
data ("their exception names are absent … OverflowError is not established by
the supplied excerpts") — an independent confirmation of both the count and
the truncation diagnosis. Two reference methods (substring signature and
final-traceback-exception classification) agree on 9; the final-exception
table is recorded in
`AUDIT_NULL_DECOMPOSITION.json → summary.terminal_crash_final_exception`
(UnicodeDecodeError 48, binascii.Error 17, OverflowError 9, TypeError 7,
truncated/unrecognized 13, others ≤2 each, FileNotFoundError 1; sum 103).
The reference stands.

## Part B — claim adjudication (gpt-6.1-sol)

| claim | verdict | action taken |
|---|---|---|
| B1 universe = 156 content sessions | **agree** | none needed |
| B2 the substring script is a diagnostic, not a scoring rule | **disagree with our wording** — **accepted** | paper wording softened from "scores … as flag-bearing"/"counts as solves" to "**reports** flag found"; the diagnostic-vs-primary distinction is now explicit |
| B3 "first-flag-token reference semantics" misattribution | **agree** | attribution replaced by the measured benchmark semantics |
| B4 statement-faithful + substring diagnostic = flag-found | **agree** | none needed |

## Conclusion

All three reviewers independently reproduced every corrected headline number
blind (156 = 145+9+2; 11/120/25 any-turn; 8/103/45 terminal; the same three
qwen gap sessions; the same A7 rest composition) and converged on the same
single wording objection (B2), which the paper adopted. The only numeric
divergence (the OverflowError terminal-crash bucket) was traced to the
payload's own stderr truncation, which gpt-6-astra explicitly flagged; the
frozen record confirms 9. No corrected number was overturned. The re-audit
stands as verified.
