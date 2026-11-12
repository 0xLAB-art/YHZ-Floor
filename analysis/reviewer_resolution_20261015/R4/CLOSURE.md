# R4: historical gate interpretation

Disposition: **addressed by correcting the inferential claim and current reporting path**. The existing gate is not a validated leakage-sensitivity gate. Source inspection shows control fixed versus random samples, but the canary compares vulnerable fixed samples against control random samples. Its cross-build workload contrast cannot establish within-vulnerable input-dependent timing sensitivity. Failure to reject the control difference does not establish equivalence or constant-time behavior.

Main E3 and AppendixC.6 now state that limitation directly. Related work contextualizes the synthetic process-span study rather than implying that it implements AES leakage testing. The current reporter records the historical PASS,60/60 control counts,p=0.676891,actual canary comparison and `leakage_validation_established=false`. It does not require PASS to admit the wall-summary analysis. No stronger evidence is invented.

`trace_gate.py` performs five passing source/verdict checks without importing or executing the gate. Historical verdict and source hashes remain unchanged; no new timing trial, synthetic p-value or bootstrap was generated. The original canary zero remains a recorded floating-point result, not an assertion that a mathematical p-value equals zero. The original raw gate classes are not supplied by its retained verdict artifact.

The20-check reporting/preservation regression passes, as do clean builds at13/5/18 pages. R12 separately addresses presentation of pooled Welch diagnostics alongside a median-of-cell-medians interval; that finding is not preemptively closed here.
