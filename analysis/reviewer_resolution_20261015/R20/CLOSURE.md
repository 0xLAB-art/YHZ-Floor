# R20: explanatory density competes with the central argument

Disposition: **addressed.**

The review found that the main text asked readers to track E1–E6,
EXP-034/035, several V3/V4 campaigns, H1/H2/H3/L1/S1/U1, historical cases
and multiple control kinds, with much space spent explaining why bodies of
evidence cannot be combined, so a reader could finish remembering the
administrative history rather than a research result. It asked for a main
narrative focused on a small set of cases that each establish a necessary
part of the contribution, full historical coverage in the supplement/
artifact, and one complete worked assessment with actual evidence fields
instead of paragraphs listing boundaries.

Resolution in the current `capability_merge_20261016` manuscript:

1. Focused main narrative. The introduction is organized around three
   finding paragraphs (Finding 1–3) and four research questions RQ1–RQ4
   (`main_sections/01_intro.tex`), followed by a six-item Contributions
   list — capability measurement, failure anatomy, system-side connection,
   latency and effort account, verification methodology, safety and
   external audit. Each item carries one denominators-and-tier statement
   and reconstructs one necessary part of the contribution; internal
   campaign names appear only inside the census/tier statements. The
   conclusion (`main_sections/10_conclusion.tex`) restates the central
   argument: agents can construct and complete cryptographic attacks
   against named weaknesses, the clock is set by the exploited layer rather
   than the cipher, and each claim is carried by its V/R/E tier.

2. Full historical coverage in the supplement/artifact.
   `supp_sections/S17_historical_arms.tex` maps every administrative arm
   (001–035 plus historical SP2-05) to its family and scientific role,
   identifies EXP-034 (Claude V4-02 cohort) and EXP-035 (H1 V2 control),
   and states lineage-not-revived-performance. Historical numbers remain
   tier-R and are never pooled with verified results (NUMBERS_LOCK.md;
   honesty flags: never pool; 74 != 148; historical 16/16 not an escrow
   baseline; WSL2 n=90,000 supplement-only).

3. One complete worked assessment with actual evidence fields.
   `supp_sections/S03_e1_fields.tex` gives the exact ten-row worksheet to
   nine-field mapping (F1–F9) with the evidence question per field, the
   frozen values and qualifiers, reconstruction normalization, and explicit
   non-adjudication of sidecar domain notes — an evidence-field-level
   worked assessment rather than a boundary-listing paragraph. Related
   worked controls live in S04b/S04c (H1 positive/provenance controls) and
   S14 (non-results census).

Honesty bounds: administrative campaign names are still present where they
identify a retained cohort (they are the record identifiers), but they no
longer drive the narrative; no populations or cohorts are pooled; every
quantitative result carries a V/R/E tier; page budget holds at 13/18/7;
no fabrication.

Evidence: R20/VALIDATION.json records six checks all pass; the current
manuscript builds clean at 13/18/7 pages; NUMBERS_LOCK.md Section G
records the lock on reported counts.
