# R12: separate statistical targets

Disposition: **addressed**. The paper's effect table now contains only the median-of-paired-cell wall effects and conditional bootstrap intervals. The current reporting artifact separates all seven primary median effects from seven auxiliary pooled-mean diagnostics, each with its own null, Welch statistic/degrees of freedom and historical normal-approximation p-value. The appendix explains that the diagnostic does not test the median estimand.

No p-value was recomputed or interval replaced. Figure3's combined descriptor now names cell pairs; the exact extra text replacement is included in the drawing-preservation check. All numerical points, bars, colors, fonts and geometry remain unchanged. The reporter reproduces the original wall effects from32,000 retained rows and exposes diagnostic provenance separately.

Structural checks confirm seven separated outputs and no Welch/p-value field in the primary contrast records. The20-check preservation/reporting regression and13/5/18 page builds pass. The historical analysis/export and statistical locks remain unchanged.
