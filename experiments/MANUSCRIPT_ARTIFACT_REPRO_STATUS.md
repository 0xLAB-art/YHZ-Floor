# Manuscript and artifact reproducibility status

The authoritative manuscript is `sp2027/paper/main.tex`; its current PDF is
`sp2027/paper/main.pdf`. The latest two-pass build is 16 letter pages, with
hashes recorded in `RESEARCH_STATE.json`, and the rendered Discussion page was
visually inspected after the novelty comparison.

Runnable evidence lanes retained in separate namespaces:

1. `P009-H1-v2`: corrected response-only H1 matrix, 90 provider responses.
2. `P009-H1-EXP-OUTPUT-CONTRACT-v1`: nine-call diagnostic exploration.
3. `P009-H1-EXP-CODE-FEEDBACK-v1`: four submissions retained as a schema-defect diagnostic.
4. `P009-H1-EXP-CODE-FEEDBACK-v2`: two ECDSA first-submission acceptances.
5. `P009-H1-EXP-CODE-FEEDBACK-CHACHA20-v1`: two ChaCha20 first-submission acceptances.
6. `P009-H1-EXP-CODE-FEEDBACK-RC4-v1`: two RC4 first-submission acceptances.
7. R1 V4 namespace 02: 12 canonical real-agent sessions, separate fixed-executor controls.
8. RUNS009 CBC controls: amended 4,096-query and frozen 400-query deterministic cohorts.

The global cost ledger is append-only and records estimated accounting costs,
provider route, token counts where available, and free-route/no-invoice
qualification. Provider credentials remain local. No verifier-held secret,
oracle scalar, or candidate secret is written to portable public-input files or
the research state manifests.

Reproduction is bounded: scripts use fixed seed sets, local synthetic fixtures,
two-turn maximum exploratory lanes, independent local oracle checks, and raw
response/event retention. Reproduction of provider behavior cannot establish
hosted model-weight identity; the route remains provider-attested only.

Open artifact work: full semantic closure of the 81-family synthesis, review of
all source-linked run IDs for claim-critical differences, anonymous release
packaging, and a final claim-to-artifact audit after any manuscript edit.
