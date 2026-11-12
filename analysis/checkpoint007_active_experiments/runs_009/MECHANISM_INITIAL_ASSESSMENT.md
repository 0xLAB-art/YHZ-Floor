# runs_009 initial mechanism assessment

Status: `PARTIAL_EXECUTION`

Genuine model calls: 94. H1 matched named/unnamed pairs: 30. Model oracle-backed successes: 0. Correct underdetermination decisions: 30/30. Provider failures: 0. Estimated accounting cost: $0.094371.

## H1 results

All 30 named and unnamed recovery conditions failed verifier-held recovery: RC4 0/10, ECDSA 0/10, XOR 0/10 in both named and unnamed conditions. Each underdetermined arm produced 10/10 correct abstention decisions. Wilson intervals are stored in `h1_analysis.json`.

The named-versus-unnamed paired comparison has zero discordant pairs in every family: both conditions were incorrect on every matched seed. This is a descriptive null result at n=10 per condition, not evidence that naming has no effect at larger samples or with a stronger instrument.

## Mechanism assessment

The current evidence supports a bounded mechanism distinction: the model reliably recognizes and abstains on explicitly insufficient information, but did not convert the supplied public observations into correct RC4, ECDSA-private-key, or XOR-mask recovery programs under this prompt/output contract. That pattern is compatible with an inference/construction bottleneck, not with cryptographic identifiability failure, because local qualification established recoverability from the same public-information classes. It does not distinguish relation discovery from code-construction failure without transcript-level coding and further instrumented runs.

The annotation call succeeded on one redacted case, but this is not a human-gold validation study. The three integration calls remain separate: the first was underidentified, the second violated the secret-material boundary, and the amended third passed boundary/schema checks but failed oracle grading.

CBC model arms remain held. The 400-query failure and 4,096-query deterministic recovery remain separate feasibility evidence for the amended 15-byte instance.
