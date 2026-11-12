# R2: corrected E3 measurement semantics

Disposition: **addressed**. The main results, appendix cell table, contrast table and original-style Figure3 now identify both estimates as subprocess wall elapsed time. The factor is capture arm, not wall-versus-CPU timer. W is wall-only capture; W+R adds child user-CPU instrumentation. Existing historical cell IDs retain their names as identifiers.

The current reporter is `sp2027/analysis/e3_wall_reporting.py`, documented by `e3_rig/REPORTING_ENTRYPOINT.md` and the manuscript source map. It verifies the raw-input hash against the historical analysis, consumes all32,000 rows, reproduces all16 wall medians and seven wall contrasts, and writes a separate versioned correction artifact. CPU values are descriptive only; zeros are retained and CPU/wall ratios use corresponding trials. Six tests exercise zero retention, trial pairing, missing CPU samples and invalid values.

The historical driver, analysis script and original analysis outputs remain unchanged. Their old presentation is not the current reporting entry point. Bootstrap intervals and auxiliary diagnostics are retained with explicit provenance; no new bootstrap, hypothesis test or timing experiment was run. R3, R4 and R12 remain separate methodological findings.

`VALIDATION.json` records20 passing checks, including the seven original protected input groups and ten frozen inputs. Figure source comparison permits exactly three label/subtitle replacements; all drawing commands, fonts, colors, geometry, points and intervals are unchanged. The generated figure was visually checked. Current PDFs remain13/5/18 pages with clean LaTeX logs.
