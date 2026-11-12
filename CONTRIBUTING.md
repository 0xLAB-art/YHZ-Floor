# Contributing

This repository is a **frozen evidence bundle**, not a conventional software project — so the contribution model follows the evidence, not the code.

## What contributions are welcome

| Contribution | How |
|---|---|
| **Verification reports** | You re-ran a check (`offline_checks.py`, a closed-form regeneration, a released-bundle manifest) and got a pass, a mismatch, or a question — open an issue with the command, the expected and actual output, and the commit SHA you checked out. Mismatch reports are the most valuable thing you can file. |
| **Independent re-derivations** | You regenerated a printed statistic from a cohort's `results.jsonl` by your own code. Open an issue (or a PR adding it under `analysis/independent/` with a README stating your environment) — independent derivations strengthen the record. |
| **Corrections to the serving layer** | Typos, broken links, or wrong descriptions in the browsable docs (`README.md`, `GUIDE.md`, `EXPLANATION.md`, `experiments/INDEX.md`, `docs/`) are ordinary PRs. |
| **New cohorts** | Only under the registered discipline below — the bundle's meaning depends on it. |

## What will not be merged

- **Edits to frozen records.** Anything under `experiments/*/results.jsonl`, `FREEZE.json`, preregistrations, or the manifests is append-only history. A correction to a *record* is a new record that cites the old one, never an edit.
- **Anything key-bearing.** Runners read API keys from the process environment only. A PR containing a key-shaped string is rejected on sight — see [SECURITY.md](SECURITY.md).
- **Statistics that pool populations.** Cohorts are never pooled; each prints its own bound. This is the audit's core method, not a style preference.

## Adding a cohort (the registered discipline)

1. Write the preregistration first: grid, cells, falsifiers, allowance, halt rule.
2. Freeze the inputs: tasks, seeds, prompts — SHA-256 in `FREEZE.json`; the runner refuses to start on mismatch.
3. Record every amendment as a numbered entry **before** the run it governs.
4. Write results append-only: `results.jsonl` gains rows, never edits; re-runs go to new per-slot files.
5. Add one line to the description map in [`tools/build_experiments_index.py`](tools/build_experiments_index.py) and regenerate: `python3 tools/build_experiments_index.py`.

[docs/RUNNING_EXPERIMENTS.md](docs/RUNNING_EXPERIMENTS.md) walks this lifecycle end-to-end on the M1 audit.

## Reporting a problem with the evidence

If you believe a registered number does not follow from its rows, or a claim overreaches its bound: open an issue titled `Evidence question: <cohort>` with the exact command and output. Questions about evidence are treated as first-class contributions.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE). The frozen records themselves are cited, not licensed — see [CITATION.cff](CITATION.cff).
