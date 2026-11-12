# Current E3 reporting entry point

Use `python sp2027/analysis/e3_wall_reporting.py` from the outer root for
the corrected interpretation of retained E3 measurements. It reads all
32,000 trials, reproduces the sixteen published wall medians and seven
wall contrasts, and writes a separate `reporting_correction_v2` artifact.

Both capture arms use `perf_counter_ns` around subprocess execution for
the reported `t_s`. The getrusage arm additionally records child user CPU
time. Historical CPU/Wall or two-timer labels must not be reused as the
meaning of the published effects. The corrected names are Wall only and
Wall + rusage. Raw cell keys retain their historical names for identity.

`e3_analyze.py`, the original driver and the existing rig analysis outputs
remain historical evidence. Do not rerun that exporter over its original
output paths to refresh the manuscript: its historical CPU-fraction loader
drops zeros and its presentation uses obsolete timer labels. The new
entry point preserves zeros and trial pairing for descriptive CPU summaries.
It preserves the old wall-effect intervals with explicit provenance rather
than silently rerunning the bootstrap or rewriting original results.

R3 additionally traces the synthetic workload, fresh-process interval and
filesystem-cache operation. The retained initial driver applies SMT toggles
during block preparation, before measurement. The resume code applies them
per remaining block. The interrupted prefix has no per-trial hardware-state
attestation. Treat on/off as recorded labels, not an identified SMT effect.
Do not use the retained historical launchers as a validated future protocol.

The historical gate's PASS is not leakage validation: its canary compares
vulnerable-fixed with control-random process spans. The corrected report
retains that verdict as provenance and sets leakage validation false.
Non-rejection on the control does not establish constant-time behavior.
