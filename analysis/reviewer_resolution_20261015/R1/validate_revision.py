import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PAPER = ROOT / "sp2027/paper/split_rebuild_evidence_promotion"


def main():
    replay = subprocess.run(["python", str(OUT / "replay.py")], cwd=ROOT, capture_output=True, text=True)
    tests = subprocess.run(["python", "-m", "unittest", "discover", "-s", "ACTS-ATTACK/harness", "-p", "test_evidence_claims.py"], cwd=ROOT, capture_output=True, text=True)
    checks = {"retained_replay_passes": replay.returncode == 0,
              "implementation_tests_pass": tests.returncode == 0 and "Ran 11 tests" in tests.stderr}
    for job, limit in [("main_content", 13), ("supplement", 5), ("submission", 18)]:
        info = subprocess.check_output(["pdfinfo", str(PAPER / (job + ".pdf"))], text=True)
        pages = int(next(line.split(":", 1)[1] for line in info.splitlines() if line.startswith("Pages:")))
        log = (PAPER / (job + ".log")).read_text()
        checks[job + "_page_budget"] = pages <= limit
        checks[job + "_clean_latex"] = not any(s in log for s in ["undefined", "Overfull", "! LaTeX Error", "Rerun to get cross-references right"])
    abstract = (PAPER / "main_content.tex").read_text()
    intro = (PAPER / "main_sections/01_intro.tex").read_text()
    synthesis = (PAPER / "main_sections/06_synthesis.tex").read_text()
    checks["empirical_title_and_abstract"] = "An Empirical Audit" in abstract and "We introduce claim-relative" not in abstract
    checks["empirical_contribution_primary"] = "primary contribution is this empirical audit" in intro
    checks["same_case_comparison_present"] = "apply selected ABC guidance to the same cases" in synthesis
    checks["independent_accuracy_not_claimed"] = "not independent semantic accuracy" in synthesis
    changes = {}
    baseline = json.loads((PAPER / "rigorous_review_20261015/REVIEWED_SNAPSHOT.json").read_text())
    for relative, old in baseline.items():
        current = hashlib.sha256((PAPER / relative).read_bytes()).hexdigest()
        if current != old["sha256"]:
            changes[relative] = {"reviewed_sha256": old["sha256"], "revised_sha256": current}
    result = {"scope": "R1 revision checks; not independent scientific novelty certification",
              "checks": checks, "all_pass": all(checks.values()), "changed_reviewed_files": changes,
              "replay_stdout": replay.stdout, "test_stderr": tests.stderr}
    (OUT / "REVISION_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": len(checks), "all_pass": result["all_pass"], "changed_files": len(changes)}))
    if not result["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
