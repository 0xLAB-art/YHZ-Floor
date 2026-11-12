# Capability-centered S&P revision, 16 October 2026

The active S&P manuscript now asks what AI agents can execute against cryptographic systems, under which task conditions, and with what observed construction behavior and practical limits. The original `main.tex` supplies the research direction and historical experiment families; it was not edited by this revision. Its pre-existing Git diff is not attributed to this work.

## Delivered manuscript

- Combined submission: `sp2027/paper/split_rebuild_evidence_promotion/submission.pdf`, **18 pages**.
- Standalone main: `main_content.pdf`, **13 pages including its references**; main narrative reaches page 13. The combined references and appendices share pagination within the 18-page submission.
- Separately titled supplement: `supplement.pdf`, **6 pages including its separate references**. Its pagination must not be added to the standalone main to infer combined submission length.
- Active source: `main_content.tex`, all nine main-section sources, supporting appendices and the three bibliography variants in the same paper directory.

Title: **ACTS-Attack: Demonstrated Capabilities and Boundaries in Agent-Executed Cryptographic Attacks**.

## Substantive changes

1. Abstract, introduction, research questions, contributions, synthesis and conclusion now center on cryptographic attack execution. The public-release audit supplies supporting context after the capability results.
2. The design section explains supplied information, required access, recovery equations and exact verifier relations for RC4, ChaCha20, CBC and ECDSA. The main protocol states task instances, backend-label limits, process/request/session budgets, stopping and retry distinctions.
3. New offline analysis reads twelve prospective records and their transcripts. The checked task split is **0/3 RC4, 2/3 ChaCha20, 3/3 CBC, 3/3 ECDSA**. The older discovery summary's swapped ChaCha20/ECDSA counts are not propagated.
4. The analysis binds **31 generated programs** to artifact digests. **Four sessions succeed on the first submission; four more succeed after feedback.** All three CBC sessions contain earlier execution failures, six in total, followed by accepted plaintext. Their cumulative query counts are **20,737, 20,994 and 21,508**.
5. A complete CBC worked trajectory connects an initial 257-query failure, execution feedback, a second generated program, the cumulative 20,737-query count, a 64-byte claim and its accepted digest relation. The supplement names the corresponding full-run suffix.
6. All five prospective accepted plaintext claims are independently hashed against their recorded expected digests, including permitted CBC unpadding. ECDSA retains three oracle observations of both private-key match and challenge-signature validity. Missing reserved scalars/challenge material are not invented to claim independent signature reconstruction.
7. The **74-session historical population** is explicit in the main narrative: **42 accepted, two rejected and 30 without verdicts**. Each acceptance links to a run claim whose recomputed digest matches its recorded expected digest. All 74 V2/V3 copy pairs are identical; they are counted once. This population is not pooled with the distinct 54-record legacy campaign or prospective twelve.
8. The stream-task information condition is explicit. The retained generator uses an all-zero second message; the brief does not disclose that condition. Generated RC4 programs make plaintext guesses. This supports an input/interface qualification, not a causal prompt-effect claim or ranking of intrinsic cryptographic difficulty.
9. Original TLS policy, side-channel, wire-edit and escrow results retain their positive findings and their units. The main paper distinguishes a local policy contrast, modified-victim exact recovery, separate partial recovery, a wire transformation, and a candidate/commitment match from independently established agent discovery or general primitive compromise.
10. Related work now includes primary-checked AICrypto, CTF-ABACUS and CryptanalysisBench. ACTS author metadata is normalized from primary Crossref records. Unused entries are removed from active bibliography variants; no missing citation keys remain. This is not an independent full-field literature review or verification of every older bibliographic field.

## Preservation and provenance

The seven original protected evidence groups and ten frozen-input hashes match their prior baseline. Raw records, ignored/untracked sessions, historical locks and the original review snapshot are not rewritten. No model-provider experiment, submitted attack program, disclosure message, commit or reset is performed.

The original claim disposition is in `ORIGINAL_CLAIM_DISPOSITION.md`; it explains why historical summaries, prompt-edit entries, estimates and safety ratings cannot be silently promoted into a new agent-capability denominator. Full earlier release-audit and replay prose remains as archived artifact detail. The source map points to those records and current analysis.

`BEFORE.json` retains exact pre-edit source text from bounded in-session reads, plus protected manifests. An initial oversized snapshot command produced truncated output; that invalid generated file was replaced with a valid bounded snapshot. Its root-manuscript hash is explicitly validation-time, not presented as a separately retained start-of-turn hash.

The older R1--R18 closure receipts refer to earlier source versions. They are not current manuscript hash certificates. Current checks are recorded in this directory's `VALIDATION.json`.

## Observed validation

`validate_revision.py` reports **31/31 checks passing**, including **28 tests**: 11 claim-checker tests, six wall-reporting tests, six eligibility tests and five new capability-integrity tests. The latter alter temporary copies to check candidate tampering, changed program identity, missing terminal records and copied-directory drift; primary evidence is untouched.

The capability census reproduces **179 pinned input files**. The earlier eight-proposition replay reproduces its four supported / three contradicted / one unresolved outcomes over 35 files without overwriting its saved receipt. The corrected E3 reporter reproduces its 32,000-trial wall analysis.

All three PDFs were built with two `pdflatex` passes. Logs have no undefined references/citations, overfull boxes, missing-character notices or unresolved rerun requests. Main text is within 13 pages and the combined PDF is 18 pages. Citation-key coverage and normal ACTS metadata pass in all three bibliography variants.

Rendered inspection covered the title, task/equation table, construction results, appendix trace table, final page and the main/reference/appendix boundary. Final retained renders are `QA_page03.png`, `QA_page13.png` and `QA_page18.png`. Tables and equation notes are readable with no inspected overlap or clipping. Figures 2/3 were not restyled or resized by this revision; their small labels remain the previously identified R14 presentation issue.

## Scientific and delivery work still open

- The prospective result remains one mutable backend with three sessions per task. No matched human, cross-model, no-feedback or no-model construction arm identifies comparative or causal effects.
- The stream-task brief condition needs a separate, controlled future study before causal information-effect claims. Current observations and their limitations are preserved.
- The eight successful prospective durations lack raw harness endpoint pairs. Full historical runtime identity, some raw side-channel samples and enforced escrow isolation remain unavailable.
- A complete accessible anonymous reviewer package (R19) is not certified by a workspace replay. Maintainer notification and author-owned declarations are not completed by drafting a plan.
- The capability framing and new worked examples substantially address explanatory density; they do not guarantee novelty, reviewer approval or S&P acceptance. R14's small figure labels and residual artifact/author checks remain explicit.

## Reproduction

From `/mnt/nvme5/ACTS-Attack`:

```bash
python sp2027/analysis/capability_rebuild_20261016/analyze_capabilities.py --verify sp2027/analysis/capability_rebuild_20261016/CAPABILITY_CENSUS.json
python sp2027/analysis/capability_rebuild_20261016/validate_revision.py
```

The second command refreshes only this revision's validation receipt and runs tests. It intercepts the earlier replay's output write so historical receipts remain intact. PDF rebuilding uses `pdflatex -interaction=nonstopmode -halt-on-error` twice for each of `main_content.tex`, `supplement.tex` and `submission.tex` from the paper directory. No unavailable LSP or build dependency is installed.
