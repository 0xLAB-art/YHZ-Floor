import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PAPER = "sp2027/paper/capability_revision_20261020/"
POST = PAPER + "artifact_documentation/novelty_program_20261017/"
INDEX = ROOT / "sp2027/analysis/poc_inventory_20261021/extracted_recursive_v3/manifest.csv"


def scope(identifier, prefixes, authorities, observed, coverage, boundary):
    return dict(scope_id=identifier, prefixes=prefixes, authorities=authorities,
                recorded_result=observed, coverage=coverage, boundary=boundary)


SCOPES = [
    scope("H1R3", ["sp2027/analysis/h1r3_20261019/"],
          [PAPER + "main_sections/04_capability.tex",
           "sp2027/analysis/h1r3_20261019/ADMISSION_RULE_PROVENANCE.json"],
          "852 scheduled sessions; primary L3 contrasts bounded by declared margin",
          "Representation variation within two local task families",
          "One route; namespace also contains calibration and aborted attempts; only confirmatory cohort supports primary inference"),
    scope("ADMISSION_MECHANISM", ["sp2027/analysis/policy_mechanism_20261021/"],
          ["sp2027/analysis/policy_mechanism_20261021/DERIVED.json", PAPER + "main_sections/04_capability.tex"],
          "Fixed-program contrast -0.8 to -32.8 pp; cleanup contrast +3.9 pp",
          "Source-level explanation and output-preserving cleanup",
          "Counterfactual on H1R3 programs; not a second population or external benchmark"),
    scope("V4", ["sp2027/agent-eval/runs_r1_clean_capture_first_v4_claude46_20261014_02/"],
          ["sp2027/agent-eval/R1_CLEAN_COHORT_V4_RESULTS.md"],
          "8 accepted / 12 sessions; 31 submitted programs",
          "Capture-first interactive construction across four local tasks",
          "One recorded hosted route; n=3 per task; no matched comparison with CLI cohorts"),
    scope("EXPLICIT_CODE", ["sp2027/research_execution/" + name + "/" for name in
          ["exploratory_code_feedback_20261017_v2", "exploratory_code_feedback_chacha20_20261018",
           "exploratory_code_feedback_rc4_20261018", "exploratory_code_feedback_ecdsa_replication_20261018",
           "exploratory_code_feedback_chacha20_replication_20261018", "exploratory_code_feedback_rc4_replication_20261018",
           "exploratory_code_feedback_ecdsa_replication_20261018_seeds56",
           "exploratory_code_feedback_chacha20_replication_20261018_seeds56",
           "exploratory_code_feedback_rc4_replication_20261018_seeds56"]],
          ["sp2027/research_execution/ACTS_ATTACK_FINAL_SCIENTIFIC_SYNTHESIS.md", PAPER + "main_sections/04_capability.tex"],
          "6/6 first submissions per family, retained as separate 2+2+2 cohorts",
          "Additional seeds and explicit observations in RC4, ChaCha20 and ECDSA",
          "Same local fixture families; not independent benchmark replication; defective ECDSA v1 excluded"),
    scope("REDUCED_OBSERVATIONS", ["sp2027/research_execution/blind_opportunity_" + x + "_20261018/" for x in ["ecdsa", "rc4", "chacha20"]],
          ["sp2027/research_execution/ACTS_ATTACK_FINAL_SCIENTIFIC_SYNTHESIS.md"],
          "ECDSA 2/2; RC4 2/2; ChaCha20 0/2",
          "Observation-contract diagnostic",
          "Information removed asymmetrically; not label blinding or a causal information effect"),
    scope("CLI_COMPOSITION", [POST + "compositional_20261017_attempt2/"],
          [POST + "compositional_20261017_attempt2/oracle_verdict.json", PAPER + "main_sections/05_adaptive.tex"],
          "One accepted supplied AES-CTR capability-to-payload chain",
          "OpenCode CLI / recorded GLM label; HTTP target consequence",
          "Purpose-built local fixture; supplied chain; not autonomous discovery or replication of admission effect"),
    scope("CLI_HELDOUT", [POST + "heldout_generalization_20261017_attempt4/"],
          [POST + "heldout_generalization_20261017_attempt4/manifest.json", PAPER + "main_sections/05_adaptive.tex"],
          "Development 2/2 and held-out 2/2, on two shared secrets",
          "Within-family alphabet transfer",
          "Rule supplied to both arms; earlier integrity-failed attempts excluded; not independent weakness families"),
    scope("HEB1", ["sp2027/analysis/heb1_crossboundary_20261019/"],
          ["sp2027/analysis/heb1_crossboundary_20261019/HEB1_EVALUATION_REPORT.md"],
          "Held-out defect cases: baseline promotions 36/36; join validator 0/36",
          "Held-out synthetic composition patterns, including new split-half pattern",
          "Project-constructed fixtures and trusted adjudicator; not deployed failure prevalence"),
    scope("IARB", ["sp2027/analysis/experiment_b_20261019/iar_b/", "sp2027/analysis/experiment_b_20261019/iar_b_heldout/"],
          ["sp2027/analysis/experiment_b_20261019/IAR_B_RESULTS_REPORT.md", PAPER + "supp_sections/S28c_lineage_cells.tex"],
          "Held-out attack-family promotions: joins 16/44; signatures 28/44; combined 0/44",
          "Separate held-out IDs/keys and an unseen reference-replay pattern",
          "Shared project, schema and cryptographic infrastructure; malformed controls remain in denominator"),
    scope("IARC", ["sp2027/analysis/experiment_b_20261019/iar_c/"],
          ["sp2027/analysis/experiment_b_20261019/iar_c/IAR_C_RESULTS_REPORT.md",
           "sp2027/analysis/contribution_audit_20261021/attribution_evidence/REPORT.md"],
          "Preserved attack-family promotions: joins 10/28; signatures 14/28; combined 0/28",
          "Separately written generator and adjudicator",
          "Shared schema/crypto module; preserved cases used in calibration; not untouched held-out or external-lab replication"),
    scope("INTOTO", ["sp2027/analysis/acts_next_phase_20261019_v2/stage6_matched_translation/"],
          ["sp2027/analysis/acts_next_phase_20261019_v2/stage6_matched_translation/translation_results_v2.json",
           PAPER + "supp_sections/S27c_attribution_compact.tex"],
          "Configured inspection agrees 21/22 stateless, 22/22 with shared replay state",
          "Another implementation of the specified attribution policy",
          "Same evidence and policy design; not an independent benchmark or superiority test; SLSA not comparable"),
    scope("LOCAL_TARGET_ATTRIBUTION", ["sp2027/analysis/acts_next_phase_20261019_v2/stage5_live_campaign/"],
          [PAPER + "supp_sections/S27c_attribution_compact.tex"],
          "Local target positive attribution and bounded failed model attempt; loopback exercise reported separately",
          "Operational reachability in a project-owned target environment",
          "One local deployment, trusted observer/reference roles; not arbitrary-host soundness"),
    scope("RELEASE_AUDIT", [],
          [PAPER + "main_sections/09_audit.tex", PAPER + "supp_sections/S04_e1_provenance.tex"],
          "Six releases, 54 field assessments; 0/6 meet all nine reconstruction fields",
          "External documentary evidence about reconstructability",
          "No external executable benchmark or imported attack-success cohort; no program-inventory match expected"),
]


def main():
    counts, hashes = Counter(), {s["scope_id"]: set() for s in SCOPES}
    total = linked = 0
    with INDEX.open(newline="") as source, (OUT / "inventory_scope_links.csv").open("w", newline="") as dest:
        fields = ["scope_id", "source_path", "source_root", "sha256", "object_path", "association", "program_outcome"]
        writer = csv.DictWriter(dest, fieldnames=fields)
        writer.writeheader()
        for row in csv.DictReader(source):
            total += 1
            path = row["source_path"].split("::", 1)[0]
            matches = [s for s in SCOPES if any(path.startswith(p) or "/" + p in path for p in s["prefixes"])]
            linked += bool(matches)
            for s in matches:
                identifier = s["scope_id"]
                counts[identifier] += 1
                hashes[identifier].add(row["sha256"])
                writer.writerow(dict(scope_id=identifier, source_path=row["source_path"], source_root=row["source_root"],
                                     sha256=row["sha256"], object_path=row["object_path"],
                                     association="namespace_path_only_including_snapshot_copies",
                                     program_outcome="NOT_ASSIGNED_BY_THIS_LINKER"))
    for s in SCOPES:
        s["inventory_occurrences"] = counts[s["scope_id"]]
        s["inventory_unique_hashes"] = len(hashes[s["scope_id"]])
        s["authority_files"] = []
        for path in s["authorities"]:
            target = ROOT / path
            if not target.is_file():
                raise FileNotFoundError(target)
            s["authority_files"].append(dict(path=path, sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    report = dict(schema="acts-existing-evidence-scope/1", experiments_executed=False,
                  evidence_rescored=False, inventory_rows=total, linked_inventory_rows=linked,
                  unassigned_inventory_rows=total-linked,
                  warning="Namespace links are not per-program score joins. Zero matches do not imply absent evidence. Scope hash counts are not trials.",
                  inventory_sha256=hashlib.sha256(INDEX.read_bytes()).hexdigest(), scopes=SCOPES)
    (OUT / "EVIDENCE_SCOPE_MATRIX.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ["inventory_rows", "linked_inventory_rows", "unassigned_inventory_rows", "experiments_executed", "evidence_rescored"]}))
    print(json.dumps({s["scope_id"]: s["inventory_occurrences"] for s in SCOPES}))


if __name__ == "__main__":
    main()
