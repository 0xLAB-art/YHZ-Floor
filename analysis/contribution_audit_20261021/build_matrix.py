#!/usr/bin/env python3
"""Build the consolidated claim/evidence/closest-prior-work matrix.

Merges the two prior-work agents' claim comparisons with the wave-1 evidence
summaries, and emits a machine-readable matrix plus a human-readable table.
Every cell is derived from a worker artifact; this script adds no new claims.

Usage:  python3 -B build_matrix.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Evidence produced by the wave-1 analyses, each independently reproduced by
# root_verify.py.  Values are the worker's own reported numbers; the verify
# script is what confirms them.
WAVE1_EVIDENCE = {
    "C1": {
        "mechanism": "policy_mechanism",
        "findings": [
            "Zero of 852 frozen sources were rejected for imports under the v3 policy; "
            "the three pre-output failures are one syntax error and two runtime errors.",
            "The narrower legacy policy is a counterfactual policy, not the task contract: "
            "all 205 of its import rejects concern modules the frozen prompt explicitly "
            "permitted. Calling them task-contract violations would be incorrect.",
            "Conservative removal of eligible whole unused import statements, applied to 128 "
            "derivatives, left every observed output identical; 104 derivatives then qualified "
            "under the legacy policy and 98 of those are cryptographically correct.",
            "Runtime tracing observed a real load of the imported object in 100 of the 101 "
            "sources with static legacy-disallowed references.",
        ],
        "implication": "The policy-sensitivity finding survives the strongest available "
                       "deflation, but it is evaluator-policy dependence under a changed rule, "
                       "not evidence that the evaluator erred against the task contract.",
    },
    "C2": {
        "mechanism": "paired_effects",
        "findings": [
            "L3 R2-R0 under the current contract: 125/128 versus 124/128, a -0.78 pp contrast.",
            "The same 128 matched instances under legacy admission: 100/128 versus 58/128, "
            "a -32.81 pp contrast; the policy change is -32.03 pp with 50 negative and 9 "
            "positive per-instance shifts and 69 unchanged.",
            "The preregistered L3 verdict reproduces exactly: intervals [-2.34375, 3.90625] "
            "and [-4.6875, 3.125] pp, Holm-adjusted p = 1.000, both EQUIVALENT_WITHIN_MARGIN.",
            "The interaction is not uniform: at L1/L2 it is confined to ECDSA, and the "
            "L3 R2 shift runs from -21.88 pp (XOR only) to -42.19 pp (ECDSA only).",
        ],
        "implication": "A changed admission rule moves the apparent representation contrast "
                       "by up to 32 pp while program bytes and historical cryptographic "
                       "outcomes are held fixed. This is an artifact-level counterfactual, "
                       "not a model comparison and not a fresh policy deployment.",
    },
    "C3": {
        "mechanism": "policy_mechanism",
        "findings": [
            "851 syntax-valid originals plus 128 derivatives were freshly executed; all fresh "
            "cryptographic outcomes match the retained predicates, with 738/768 primary, "
            "63/64 noise and 20/20 abstention controls.",
            "Source and prompt hashes match all retained records and the input hashes are unchanged.",
        ],
        "implication": "The replay is a re-execution of retained programs against retained "
                       "public inputs. It is not fresh model generation.",
    },
    "C4": {
        "mechanism": "attribution_evidence",
        "findings": [
            "1,096 validator/adjudicator invocations across 274 bundles agree with the "
            "archived decisions; zero disagreements.",
            "Across the five populations, join-only and signature-only checks each promote "
            "attack-family cases that the combined check rejects (IAR-C 10/28 and 14/28, "
            "combined 0/28; IAR-B heldout 16/44 and 28/44, combined 0/44).",
            "The four soundness corpora recount to 11,256 evaluations of 1,407 mutants with "
            "no observed soundness violation.",
            "The 14/16 rejection figure reflects a full-attribution-only validator rejecting "
            "fourteen lower-level requests; it is a functionality difference, not a fair "
            "comparative false-reject rate.",
            "IAR-C had already evaluated the same 44 case IDs during calibration, so the "
            "preserved corpus is a preserved replay, not an untouched held-out test.",
        ],
        "implication": "Authenticity and claim-specific binding are jointly required against "
                       "the tested record-rewriting and splice cases. This is a domain "
                       "application of existing provenance mechanisms, not a new mechanism, "
                       "and not a prevalence estimate.",
    },
    "C5": {
        "mechanism": "policy_mechanism + paired_effects",
        "findings": [
            "The measurable consequence is confined to the admission axis: 6.2%-47.7% of "
            "unchanged correct programs are rejected by a legacy import policy, moving the "
            "L3 R2-R0 contrast from -0.78 pp to -32.03 pp.",
            "The attribution axis contributes a specified evidence contract and a bounded "
            "mutation test regime, not a prevalence or capability estimate.",
        ],
        "implication": "The security-specific instantiation is real, but the generic 'flaws "
                       "distort performance' half is prior work.",
    },
}

# The consolidated verdict per candidate, after reconciling both prior-work
# assessments against the wave-1 evidence.
VERDICTS = {
    "C1": {
        "combined_novelty": "measurement_technique",
        "verdict": "Supported as a controlled evaluation procedure, not as a new general "
                    "principle. Both comparators own the decomposition template: ABC "
                    "separates true task success from the automatic score (App. A, p. 17), "
                    "AgentSuite decomposes measurement invalidity by benchmark component "
                    "(Table 2, p. 3). Our increment is the unit of analysis (the submitted "
                    "program and its execution evidence) and the intervention (byte-identical "
                    "re-admission).",
        "strongest_support": "The three-way decomposition is executed over 852 sessions "
                              "with an independent cryptographic predicate and a "
                              "stage-resolved denominator, and the middle axis is measured, "
                              "not asserted.",
        "what_would_change_it": "Applying the decomposition to a second, non-cryptographic "
                                 "benchmark's retained programs. Until then it is a local "
                                 "technique with a domain application.",
    },
    "C2": {
        "combined_novelty": "measurement_technique",
        "verdict": "Supported as a measurement instrument, and this is the strongest "
                    "candidate. ABC already varies the evaluation rule on fixed artifacts "
                    "(App. G p. 32; Sec. 5.3/Fig. 6 pp. 9-10) and AgentSuite already shows "
                    "evaluation-side changes move reported capability with a null baseline "
                    "(p. 8). Our increment is narrower and different in kind: the program "
                    "bytes are fixed between the two evaluations, the contrast is paired at "
                    "the instance level, and the estimator is policy dependence rather than "
                    "a leaderboard.",
        "strongest_support": "The -32.03 pp L3 R2-R0 shift is reproduced from 128 matched "
                              "instances, survives conservative unused-import removal, and "
                              "the preregistered L3 verdict is unchanged. The legacy policy "
                              "was legitimate under its own prompt, so the finding is "
                              "evaluator-policy dependence, not evaluator error.",
        "what_would_change_it": "Re-grading a second benchmark's retained programs under "
                                 "two admission rules with byte-identical artifacts and "
                                 "paired contrasts. If the shift does not reproduce there, "
                                 "this is a property of our harness's legacy policy.",
    },
    "C3": {
        "combined_novelty": "domain_application",
        "verdict": "Supported as a domain application with a rigour increment. Independent "
                    "predicates are already ABC's vocabulary (T.7, T.9, O.d.1, pp. 5-6). "
                    "AgentSuite explicitly places execution-based matching in related work "
                    "and does not generalise it (App. A, p. 12), so the fresh-replay "
                    "discipline has no counterpart there.",
        "strongest_support": "852/852 reference-replay agreement with an independent "
                              "cryptographic predicate, and 851 admitted programs re-executed "
                              "in the staged candidate.",
        "what_would_change_it": "Nothing in the comparators; the limit is that the replay is "
                                 "of retained programs, so it cannot support a claim about "
                                 "fresh generation.",
    },
    "C4": {
        "combined_novelty": "domain_application",
        "verdict": "The only candidate with no overlap at either comparator: 'provenance', "
                    "'attribution', 'signature' and 'admission' occur zero times across the "
                    "41 ABC pages and the 20 AgentSuite pages. But the right comparators "
                    "are provenance-aware works (in-toto, SLSA, CTF-ABACUS, ORTHRUS), not "
                    "these two, and the manuscript already concedes that configured "
                    "provenance mechanisms implement the tested policy.",
        "strongest_support": "Joint necessity of authenticity and claim-specific binding "
                              "across 274 bundles with zero disagreements, plus 11,256 "
                              "bounded mechanized evaluations with no observed soundness "
                              "violation, and a configured in-toto inspection reproducing "
                              "21/22 then 22/22 decisions.",
        "what_would_change_it": "A provenance-aware comparator, not ABC or AgentSuite. The "
                                 "release-evidence audit is documentary, not executable "
                                 "validation, and must not be presented as such.",
    },
    "C5": {
        "combined_novelty": "domain_application",
        "verdict": "Not supported as phrased. The contrastive framing 'rather than generic "
                    "discovery that benchmark flaws distort performance' is contradicted: ABC "
                    "is the generic discovery work (abstract p. 1; Sec. 5.2 p. 9) and "
                    "already owns a security-domain case study in CVE-Bench with a 33% "
                    "absolute overestimation reduction; AgentSuite's headline is the same "
                    "generic finding at larger scale (5,086 tasks, 18/30 rank shifts).",
        "strongest_support": "A cryptographic instantiation that adds an admission-policy "
                              "axis and an attribution layer to the audit style, measured "
                              "rather than asserted.",
        "what_would_change_it": "Drop the contrastive framing. The defensible narrowing is "
                                 "'a cryptographic case study that adds a policy-sensitivity "
                                 "contrast and an attribution layer to the ABC-style audit'.",
    },
}


def load_rows(path: Path, key: str):
    doc = json.loads(path.read_text())
    rows = doc.get(key) or doc.get("rows") or []
    return {r["id"]: r for r in rows}


def main() -> int:
    abc = load_rows(HERE / "abc_prior/claim_comparison.json", "rows")
    suite = load_rows(HERE / "agentsuite_prior/claim_comparison.json", "claims")

    matrix = []
    for cid in sorted(set(abc) | set(suite)):
        a = abc.get(cid, {})
        s = suite.get(cid, {})
        v = VERDICTS[cid]
        matrix.append({
            "id": cid,
            "claim": a.get("claim") or s.get("claim"),
            "our_evidence": WAVE1_EVIDENCE[cid],
            "abc_overlap": a.get("abc_overlap"),
            "abc_distinction": a.get("abc_distinction"),
            "abc_novelty_type": a.get("novelty_type"),
            "agentsuite_overlap": s.get("agentsuite_overlap"),
            "agentsuite_distinction": s.get("agentsuite_distinction"),
            "agentsuite_novelty_type": s.get("novelty_type"),
            "would_agentsuite_have_produced_same_finding":
                s.get("would_agentsuite_have_produced_same_finding"),
            "combined_novelty": v["combined_novelty"],
            "verdict": v["verdict"],
            "strongest_support": v["strongest_support"],
            "what_would_change_it": v["what_would_change_it"],
        })

    out = {
        "schema": "contribution-audit-matrix/1",
        "date": "2026-10-21",
        "derived_from": {
            "abc": "abc_prior/claim_comparison.json",
            "agentsuite": "agentsuite_prior/claim_comparison.json",
            "wave1": ["policy_mechanism/REPORT.md", "paired_effects/REPORT.md",
                      "attribution_evidence/REPORT.md"],
            "root_verification": "root_verify.py (43 independent checks)",
        },
        "rows": matrix,
    }
    (HERE / "SYNTHESIS_MATRIX.json").write_text(json.dumps(out, indent=2) + "\n")

    lines = ["# Consolidated claim / evidence / closest-prior-work matrix", "",
             "Derived from `abc_prior/claim_comparison.json`,",
             "`agentsuite_prior/claim_comparison.json` and the three wave-1 analyses.",
             "Every wave-1 number was independently reproduced by `root_verify.py`.",
             "The manuscript was not modified by this audit.", ""]
    for row in matrix:
        lines += ["## %s — %s" % (row["id"], row["combined_novelty"].replace("_", " ")), "",
                  "**Claim.** %s" % row["claim"], "",
                  "**Verdict.** %s" % row["verdict"], "",
                  "**Our evidence.**"]
        for f in row["our_evidence"]["findings"]:
            lines.append("- %s" % f)
        lines += ["", "*Implication.* %s" % row["our_evidence"]["implication"], "",
                  "**ABC.** %s" % (row["abc_distinction"] or "no assessment"), "",
                  "**AgentSuite.** %s" % (row["agentsuite_distinction"] or "no assessment"), "",
                  "**Strongest support.** %s" % row["strongest_support"], "",
                  "**What would change the verdict.** %s" % row["what_would_change_it"], ""]
    (HERE / "SYNTHESIS_MATRIX.md").write_text("\n".join(lines) + "\n")

    print("matrix rows: %d" % len(matrix))
    for row in matrix:
        print("  %s  %-24s abc=%-22s suite=%s"
              % (row["id"], row["combined_novelty"], row["abc_novelty_type"],
                 row["agentsuite_novelty_type"]))
    print("wrote SYNTHESIS_MATRIX.json and SYNTHESIS_MATRIX.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())