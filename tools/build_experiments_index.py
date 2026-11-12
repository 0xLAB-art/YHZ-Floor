#!/usr/bin/env python3
"""Regenerate experiments/INDEX.md from the frozen tree.

Deterministic: directory list, results.jsonl row counts and the registered
descriptions below are the only inputs. No network, no execution of any
recorded program. Run from the repository root:

    python3 tools/build_experiments_index.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXP = ROOT / "experiments"

# One line per registered record directory: what it is + the manuscript
# section it backs ("§" = the accompanying manuscript under review).
DESCRIPTIONS = {
 "blind_opportunity_chacha20_20261018": "the ChaCha20 blind-opportunity diagnostic",
 "blind_opportunity_ecdsa_20261018": "the ECDSA blind-opportunity diagnostic",
 "blind_opportunity_rc4_20261018": "the RC4 blind-opportunity diagnostic",
 "cvebench_census_20261024": "the CVE-Bench census — 40 web-CVE targets, zero crypto",
 "diag_empty_20261103": "the empty-diagnostic control",
 "exploratory_code_feedback_20261017": "the exploratory code-feedback probe (pre-registered cohort era)",
 "exploratory_code_feedback_20261017_v2": "the second pass of the code-feedback probe",
 "exploratory_code_feedback_chacha20_20261018": "the ChaCha20 code-feedback probe",
 "exploratory_code_feedback_chacha20_replication_20261018": "the ChaCha20 code-feedback replication",
 "exploratory_code_feedback_chacha20_replication_20261018_seeds56": "the ChaCha20 replication, seeds-56 variant",
 "exploratory_code_feedback_ecdsa_replication_20261018": "the ECDSA code-feedback replication",
 "exploratory_code_feedback_ecdsa_replication_20261018_seeds56": "the ECDSA replication, seeds-56 variant",
 "exploratory_code_feedback_rc4_20261018": "the RC4 code-feedback probe",
 "exploratory_code_feedback_rc4_replication_20261018": "the RC4 code-feedback replication",
 "exploratory_code_feedback_rc4_replication_20261018_seeds56": "the RC4 replication, seeds-56 variant",
 "exploratory_output_contract_20261017": "the output-contract exploration probe (pre-registered cohort era)",
 "external_admission_20261024": "the single-session external-admission qualification probe",
 "external_admission_amend1_20261024": "the HTB grid cohort A — 31/37 vs 0/37 admission contrast",
 "external_admission_amend2_20261025": "the Amend-2 first pass, superseded by the 20261029 qualification cohort",
 "external_admission_amend2_20261029": "the Amend-2 registration + qualification arms",
 "external_admission_amend3_20261105": "the NYU three-label panel cohort B — 282 programs, 0 oracle-correct, 18/282 regrade",
 "external_admission_amend4_frontier_20261106": "the Amend-4 frontier panel on the damaged transport — superseded by the Amend-5 repanel",
 "external_admission_amend5_transport_20261109": "the Amend-5 frontier repanel on the visible-completion transport — 35/36 oracle-correct, 7/61 admission, 61/61 external",
 "external_published_audit_20261110": "the M1 published-protocol audit — 60 sessions, the censoring finding, 20/50 → 28/50",
 "external_review_amend4_c1_20261107": "the blind 3-reviewer re-derivation of the headline counts",
 "external_rule_admission_20261110": "the external-rule admission read on the frozen windows",
 "external_transfer_nondomain_20261109": "the out-of-domain premise witness — 8/8 vs 0/8, exact Fisher 7.77e-5",
 "h2_cbc_agency_20261023": "the CBC agency probe cohort",
 "h2_no_oracle_p025_20261103": "the oracle-separation control — 0/10 with 256 probes",
 "h2_pairs_extension_20261024": "the 10-pair wrapper extension + the format-compliance reversal diagnosis",
 "h2_pairs_powered_20261107": "the powered 32-pair wrapper cohort — 0/32 each direction, ≤10.7% Wilson upper",
 "info_contract_2x2_20261018": "the original 2×2 factorial that isolated the zero-reference premise",
 "info_contract_2x2_rc4_20261024": "the saturated RC4 honest null — 4/4",
 "info_contract_aesctr_20261026": "the AES-CTR boundary run — both withheld arms 0/16",
 "info_contract_aesgcm_20261102": "the AES-GCM cohort opening the modern-AEAD wave",
 "info_contract_aesgcm_apinex_20261102": "the APINEX-routed cohort — transport deviation disclosed, never pooled",
 "info_contract_aesgcm_c2_floor8000_p026_20261103": "the floor-sensitivity dose-response — 53.1% → 7.3% floor exhaustion, zero acceptance at both floors",
 "info_contract_aesgcm_labels_20261102": "the multi-label scheduling cohort",
 "info_contract_aesgcm_labels_gpt_5_6_sol__rerun_ar_20261103": "the multi-label scheduling rerun on the gpt-5.6-sol label (AgentRouter transport)",
 "info_contract_aesgcm_labels_gpt_6_1_sol__rerun_ar_20261103": "the multi-label scheduling rerun on the gpt-6.1-sol label (AgentRouter transport)",
 "info_contract_aesgcm_p017_20261102": "the P017 AES-GCM cohort",
 "info_contract_aesgcm_p022a_20261102": "the P022a AES-GCM cohort",
 "info_contract_aesgcm_p022b_20261102": "the P022b AES-GCM cohort — the transport-damaged first pass",
 "info_contract_aesgcm_p024a_20261103": "the truncation-reading closure — withholding makes every answer wrong",
 "info_contract_aesgcm_p024b_20261103": "the printed boundary condition — consistent, under-powered at every coding",
 "info_contract_aesgcm_random_20261102": "the first CSPRNG-sampled AES-GCM cohort",
 "info_contract_aesgcm_random_p021_20261102": "the P021 power cohort, first pass on the degraded transport",
 "info_contract_aesgcm_random_p021ar_20261103": "the 96-instance CSPRNG power cohort (repairs P021) — paired C1-vs-C4 96/0, Holm 4.04e-28",
 "info_contract_aesgcm_random_p021r_20261103": "the APINEX label probe — superseded, never pooled",
 "info_contract_aesgcm_random_p023_20261103": "the fresh-seed 96-instance cohort — paired 95/0",
 "info_contract_chachapoly_random_20261102": "the ChaCha20-Poly1305 CSPRNG cohort",
 "info_contract_confirmatory_c1_20261107": "the m=3 confirmatory cohort on gpt-5.6-sol — bar NOT cleared, the observability axis's registered prediction",
 "info_contract_ecdsa_20261026": "the observable-premise ECDSA control (nonce-reuse family) — 16/16 stated vs 32/32 withheld",
 "info_contract_gcmsiv_random_20261102": "the registered negative control — AES-GCM-SIV accepts nothing in any cell",
 "info_contract_label2_20261025": "the label-2 replication",
 "info_contract_label3_20261029": "the label-3 replication",
 "info_contract_label3_n32_20261101": "the n=32 scale-up + its damaged first pass and clean rerun",
 "info_contract_label4_20261030": "the label-4 replication",
 "info_contract_label5_20261030": "the label-5 replication, first pass after quota exhaustion",
 "info_contract_label5r_20261030": "the label-5 recovery rerun, disclosed per-label",
 "info_contract_n16_20261026": "the n=16 ChaCha20 cohort resolving the exact-test floor — paired 10/0",
 "info_contract_p010_driftcheck_20261026": "the drift check on the P010 family",
 "info_contract_powered_20261025": "the powered information-contract cohort",
 "info_contract_x1_gptoss_20261026": "the X1-family cohort on the gpt-oss label",
 "paper_tables_20261103": "the generator for the manuscript's registered tables",
 "provider_health_20261023": "the provider-health calibration record (infrastructure, not a cohort)",
}

RERUN_SUFFIX = "__rerun_ar_20261103"
RERUN_NOTE = "the AgentRouter-transport rerun of {base}"

# Manuscript-section anchors by directory prefix (§ = the accompanying
# manuscript under review; reproduced from the frozen registration records).
SECTION_BY_PREFIX = (
    ("blind_opportunity_", "§4"),
    ("diag_empty_", "§5"),
    ("info_contract_", "§5"),
    ("h2_", "§6"),
    ("external_admission_", "§7"),
    ("external_rule_", "§7"),
    ("external_review_", "§7"),
    ("external_published_audit_", "§7"),
    ("cvebench_census_", "§7"),
    ("external_transfer_", "§10.2"),
    ("exploratory_", "§8"),
)

# Top-level files inside experiments/ that are records a reader may want,
# grouped; everything else is run output (logs, resume scripts, sweeps).
TOPLEVEL_NOTABLE = {
    "BUDGET_LEDGER.jsonl": "per-call cost estimates for the whole campaign (3,494 rows)",
    "ACTS_ATTACK_FINAL_SCIENTIFIC_SYNTHESIS.md": "the campaign-level scientific synthesis record",
    "ACTS_ATTACK_FINAL_EVIDENCE_INDEX.csv": "the final evidence index (machine-readable)",
    "PAPER_EVIDENCE_20261103.json": "the evidence-to-manuscript mapping ledger",
    "CENSUS_P_PROVIDER_20261103.json": "the provider-side census (with its CORRECTED variant)",
    "CROSS_FAMILY_STAGE_ANALYSIS.json": "the cross-family stage analysis",
    "NOVELTY_FULLTEXT_REVIEW.md": "the prior-art full-text review record",
}


def results_rows(d: pathlib.Path) -> str:
    f = d / "results.jsonl"
    if f.is_file():
        with f.open("rb") as fh:
            return str(sum(1 for line in fh if line.strip()))
    return "—"


def main() -> int:
    def registered(name: str) -> bool:
        if name in DESCRIPTIONS:
            return True
        return name.endswith(RERUN_SUFFIX) and name[: -len(RERUN_SUFFIX)] in DESCRIPTIONS

    dirs = sorted(p for p in EXP.iterdir() if p.is_dir())
    missing = [p.name for p in dirs if not registered(p.name)]
    if missing:
        print("ERROR: no registered description for:", missing, file=sys.stderr)
        return 1
    extra = [k for k in DESCRIPTIONS if not (EXP / k).is_dir()]
    if extra:
        print("ERROR: registered description without a directory:", extra, file=sys.stderr)
        return 1

    lines = []
    w = lines.append
    w("# Experiments index — every record directory, browsable")
    w("")
    w("One row per record directory under [`experiments/`](.). \"rows\" is the exact line count of")
    w("the directory's append-only `results.jsonl` (\"—\" where the cohort records outcomes only in")
    w("per-slot or summary files). \"§\" is the section of the accompanying manuscript the record")
    w("backs — the manuscript itself travels through the venue's submission system and is not")
    w("served here. Registered cohorts, diagnostics, controls and superseded first passes all")
    w("appear; nothing is pooled and nothing is hidden.")
    w("")
    w("| Directory | rows | What it is | § |")
    w("|---|---:|---|---|")
    for p in dirs:
        if p.name in DESCRIPTIONS:
            desc = DESCRIPTIONS[p.name]
        elif p.name.endswith(RERUN_SUFFIX):
            base = DESCRIPTIONS.get(p.name[: -len(RERUN_SUFFIX)], p.name[: -len(RERUN_SUFFIX)])
            desc = RERUN_NOTE.format(base=base.rstrip("."))
        else:
            desc = p.name
        sect = next((s for pre, s in SECTION_BY_PREFIX if p.name.startswith(pre)), "")
        w(f"| [`{p.name}/`]({p.name}/) | {results_rows(p)} | {desc} | {sect} |")
    w("")
    w("## Top-level records (not cohort directories)")
    w("")
    w("The remaining entries at this level are campaign-level records and runners. The notable ones:")
    w("")
    w("| File | What it is |")
    w("|---|---|")
    for name, what in TOPLEVEL_NOTABLE.items():
        if (EXP / name).exists():
            w(f"| [`{name}`]({name}) | {what} |")
    w("")
    n_other = sum(1 for p in EXP.iterdir() if p.is_file() and p.name not in TOPLEVEL_NOTABLE)
    w(f"The other {n_other} files are run artifacts of the waves above: cohort runners (`run_*.py`),")
    w("sweep/summary outputs, per-wave logs and resume scripts — retained verbatim as part of the")
    w("frozen record, safe to ignore when reading a specific cohort.")
    w("")
    w("---")
    w("")
    w("*Regenerated by [`tools/build_experiments_index.py`](../tools/build_experiments_index.py) from")
    w("the frozen tree — re-run it after adding a cohort.*")
    w("")
    (EXP / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"experiments/INDEX.md written: {len(dirs)} directories, {n_other} other files noted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
