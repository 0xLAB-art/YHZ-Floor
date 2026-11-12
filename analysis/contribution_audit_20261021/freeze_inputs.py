import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def main():
    paths = set()
    paper = ROOT / "sp2027/paper/capability_revision_20261020"
    for directory in (paper, paper / "main_sections", paper / "supp_sections", paper / "figures"):
        paths.update(directory.glob("*.tex"))
    cohort = ROOT / "sp2027/analysis/h1r3_20261019"
    paths.update(path for path in (cohort / "runs/confirmatory").rglob("*") if path.is_file())
    paths.update(cohort.glob("*.py"))
    paths.update(cohort.glob("*PREREG*"))
    files = {}
    for path in sorted(paths):
        if path.is_file():
            files[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    dest = HERE / "INPUT_FREEZE.json"
    with dest.open("x") as stream:
        json.dump({"scope": "pre-analysis manuscript sources and frozen H1-R3 confirmatory evidence", "files": files}, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"files": len(files), "manifest": str(dest)}))


if __name__ == "__main__":
    main()
