import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ORDER = ["Cybench", "NYU CTF Bench", "CVE-Bench", "Incalmo",
         "AgentHarm", "WebSP-Eval"]
CLASSES = ["H1", "H2", "H3", "L1", "S1", "U1", "N/A"]
EXPECTED = {"H1": 0, "H2": 14, "H3": 7, "L1": 24, "S1": 6, "U1": 3, "N/A": 0}


def load_rows(root):
    path = root / "docs/revision/forensic_e1/cross_benchmark_provenance/SOURCE_LINEAGE_MATRIX.json"
    rows = json.loads(path.read_text())["rows"]
    if len(rows) != 54:
        raise ValueError(f"expected 54 rows, found {len(rows)}")
    counts = Counter(row["cell_class"] for row in rows)
    if dict(counts) != {key: value for key, value in EXPECTED.items() if value}:
        raise ValueError(f"class counts drifted: {dict(counts)}")
    return rows


def class_summary(rows, benchmark):
    counts = Counter(row["cell_class"] for row in rows if row["benchmark"] == benchmark)
    return ", ".join(f"{key} {counts[key]}" for key in CLASSES if counts[key])


def render(rows):
    by_benchmark = defaultdict(list)
    for row in rows:
        by_benchmark[row["benchmark"]].append(row)
    basis = {
        "Cybench": ("H3 (F1--F4,F6--F8)", "U1 (F5)", "S1 (F9)",
                    "historical candidate to later pin; runtime/run link unresolved"),
        "NYU CTF Bench": ("H2 (F1--F4,F6--F8)", "U1 (F5)", "S1 (F9)",
                          "contemporaneous components; executed revision unresolved"),
        "CVE-Bench": ("L1 (F1--F4,F6--F8)", "L1 (F5)", "S1 (F9)",
                       "later pin; paper-time checkout/image unresolved"),
        "Incalmo": ("L1 (F1--F4,F6--F8)", "L1 (F5)", "S1 (F9)",
                    "post-paper public heads; historical revision unresolved"),
        "AgentHarm": ("H2 (F1--F4,F6--F8)", "U1 (F5)", "S1 (F9)",
                      "release-period path/dataset; exact run link unresolved"),
        "WebSP-Eval": ("L1 (F1--F4,F6--F8)", "L1 (F5)", "S1 (F9)",
                       "post-submission pin; live execution identity unresolved"),
    }
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\begin{threeparttable}",
        r"\caption{Independent provenance strata for the 54 E1 field cells. The semantic YES/PARTIAL/NO judgments remain in Table~\ref{tab:audit}; this table qualifies the source basis and historical execution identity separately.}",
        r"\label{tab:e1-provenance}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3.1pt}",
        r"\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l p{.20\textwidth} p{.15\textwidth} p{.15\textwidth} p{.34\textwidth}@{}}",
        r"\toprule",
        r"Benchmark & F1--F4, F6--F8 & F5 & F9 & Historical interpretation \\",
        r"\midrule",
    ]
    for benchmark in ORDER:
        f123 = basis[benchmark]
        lines.append(f"{benchmark} & {f123[0]} & {f123[1]} & {f123[2]} & {f123[3]} \\\\")
    lines += [
        r"\midrule",
        r"\textbf{Total} & \textbf{H1 0; H2 14; H3 7; L1 24} & \textbf{U1 3; L1 3} & \textbf{S1 6} & \textbf{H1=0/54; N/A=0} \\",
        r"\bottomrule",
        r"\end{tabular*}",
        r"\begin{tablenotes}[flushleft]",
        r"\scriptsize",
        r"\item \textit{Notes:} H1 is a verified historical implementation/configuration/dataset/environment link; H2 is a contemporaneous public component without execution linkage; H3 is statically verified source continuity from a dated historical candidate to a later pin; L1 is a later pinned implementation; S1 is a published artifact whose generating implementation is not linked; U1 is a material unresolved identity or hash dependency. No class establishes that a published result is false. The complete cell-level matrix is \texttt{SOURCE\_LINEAGE\_MATRIX.json}.",
        r"\end{tablenotes}",
        r"\end{threeparttable}",
        r"\end{table*}",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = load_rows(args.root)
    output = args.output or args.root / "sp2027/paper/output/tables/tab_provenance.tex"
    output.write_text(render(rows))
    print(f"wrote {output} from {len(rows)} matrix rows")


if __name__ == "__main__":
    main()
