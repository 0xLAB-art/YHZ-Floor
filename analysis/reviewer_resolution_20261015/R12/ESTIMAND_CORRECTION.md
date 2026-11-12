# R12 estimand separation

The primary effect is the median of the selected V-minus-CT cell-median
differences. Its retained percentile interval resamples trials within cells
under the historical host/label strata. The auxiliary Welch statistic
instead uses pooled trial samples and a mean-difference null. The shared
historical helper reports a normal-approximation tail; it is not an exact
Student-t tail evaluated using the retained Welch degrees of freedom.

The current table prints only the primary median effect and its conditional
interval. The current report stores those under wall_contrasts and the
mean-null diagnostics separately under auxiliary_pooled_mean_diagnostics.
Each diagnostic names its null, statistic, degrees of freedom and recorded
normal-approximation p-value. Neither is silently represented as a test of
the other estimand. No new p-value or interval was generated.

Figure3's combined-row descriptor now says median of cell pairs, rather than
median of levels. This is one additional text-only correction beyond R2;
the preservation checker explicitly permits that exact replacement while
continuing to compare every drawing command and numeric value. Source,
data, points and conditional intervals are otherwise preserved.
