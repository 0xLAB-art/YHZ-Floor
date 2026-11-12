import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PAPER = ROOT / "sp2027/paper/split_rebuild_evidence_promotion"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    tests = subprocess.run(["python", "-m", "unittest", "discover", "-s", "sp2027/analysis", "-p", "test_e3_wall_reporting.py"], cwd=ROOT, capture_output=True, text=True)
    replay = subprocess.run(["python", "sp2027/analysis/e3_wall_reporting.py"], cwd=ROOT, capture_output=True, text=True)
    checks = {"six_reporting_tests": tests.returncode == 0 and "Ran 6 tests" in tests.stderr,
              "all_wall_medians_and_contrasts_reproduced": replay.returncode == 0}
    baseline = json.loads((PAPER / "strength_clarity_revision/BEFORE.json").read_text())
    additions = {"sp2027/analysis/e3_rig/REPORTING_ENTRYPOINT.md", "sp2027/analysis/e3_rig/reporting_correction_v2/e3_wall_report.json"}
    for relative, before in baseline["input_groups"].items():
        rows = [(str(p.relative_to(ROOT)), sha(p)) for p in sorted((ROOT / relative).rglob("*")) if p.is_file() and str(p.relative_to(ROOT)) not in additions]
        observed = {"file_count": len(rows), "manifest_sha256": hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()}
        checks["original_group_unchanged:" + relative] = observed == before
    checks["ten_frozen_inputs_unchanged"] = all(sha(ROOT / p) == digest for p, digest in baseline["frozen_inputs"].items())
    original = baseline["sources"]["figures/fig_effects.tex"]
    expected = original.replace("Difference of medians (ms), vulnerable minus control, with 95\\% confidence intervals across timer, cache and SMT levels", "Wall-time median contrasts (ms), vulnerable minus control, across capture-arm, cache and SMT levels")
    expected = expected.replace("{perf\\_counter\\_ns}{Timer}", "{Wall only}{Capture arm}")
    expected = expected.replace("{getrusage\\_utime}{Timer}", "{Wall + rusage}{Capture arm}")
    expected = expected.replace("{Combined}{median of levels}", "{Combined}{median of cell pairs}")
    expected = re.sub(r"\\fontsize\{([\d.]+)\}\{([\d.]+)\}", lambda m: "\\fontsize{" + f"{float(m[1])*1.2:.1f}" + "}{" + f"{float(m[2])*1.2:.1f}" + "}", expected)
    checks["original_figure_style_and_numbers_preserved"] = (PAPER / "figures/fig_effects.tex").read_text() == expected
    printed = (PAPER / "supp_sections/S11_e3.tex").read_text() + (PAPER / "tables/tab_timing-contrasts.tex").read_text()
    checks["no_cpu_estimate_rows"] = "CPU &" not in printed and "CPU time uses" not in printed
    checks["wall_semantics_explicit"] = "Both arms measure wall" in printed and "W+R" in printed
    checks["current_reporting_entrypoint_documented"] = (ROOT / "sp2027/analysis/e3_rig/REPORTING_ENTRYPOINT.md").is_file()
    pages = {}
    for job, limit in [("main_content", 13), ("supplement", 5), ("submission", 18)]:
        info = subprocess.check_output(["pdfinfo", str(PAPER / (job + ".pdf"))], text=True)
        pages[job] = int(next(line.split(":", 1)[1] for line in info.splitlines() if line.startswith("Pages:")))
        if job == "main_content":
            text_pages = subprocess.check_output(["pdftotext", str(PAPER / (job + ".pdf")), "-"], text=True).split("\f")
            ref_pages = [(i + 1, t.split("References", 1)[0]) for i, t in enumerate(text_pages) if "References" in t]
            if len(ref_pages) != 1:
                raise ValueError("Cannot identify the main/reference boundary")
            boundary, prefix = ref_pages[0]
            main_text_pages = boundary if prefix.strip() else boundary - 1
            checks[job + "_page_budget"] = main_text_pages <= limit
            pages["main_text_excluding_references"] = main_text_pages
        else:
            checks[job + "_page_budget"] = pages[job] <= limit
        log = (PAPER / (job + ".log")).read_text()
        checks[job + "_clean_latex"] = not any(s in log for s in ["undefined", "Overfull", "! LaTeX Error", "Rerun to get cross-references right"])
    result = {"checks": checks, "all_pass": all(checks.values()), "pages": pages,
              "intentional_added_evidence_files": sorted(additions), "test_output": tests.stderr,
              "report_output": replay.stdout}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": len(checks), "all_pass": result["all_pass"], "failures": [k for k, v in checks.items() if not v]}))
    if not result["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
