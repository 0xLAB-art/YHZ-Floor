#!/usr/bin/env python3
"""Sync docs_site/docs/*.md from the repository's reader-facing markdown.

The repository markdown is the single source of truth; this script is the only
path by which the rendered site's pages change. Relative links are rewritten:
site pages point at their site siblings, everything else becomes an absolute
GitHub URL. Run from the repository root:

    python3 tools/build_docs_site.py && (cd docs_site && mkdocs build)
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs_site" / "docs"
GITHUB = "https://github.com/0xLAB-art/YHZ-Floor"

PAGES = [
    # (repo source, site target, front matter)
    ("README.md", "index.md", "---\nhide:\n  - navigation\n---\n\n"),
    ("GUIDE.md", "guide.md", ""),
    ("docs/VERIFYING.md", "verifying.md", ""),
    ("docs/SETUP_AND_API.md", "setup_and_api.md", ""),
    ("docs/RUNNING_EXPERIMENTS.md", "running_experiments.md", ""),
    ("docs/REPO_MAP.md", "repo_map.md", ""),
    ("reviewer_bundle/README.md", "reviewer_bundle.md", ""),
    ("experiments/INDEX.md", "experiments_index.md", ""),
]

SITE_SIBLINGS = {
    "README.md": "index.md",
    "GUIDE.md": "guide.md",
    "EXPLANATION.md": "guide.md",
    "docs/VERIFYING.md": "verifying.md",
    "docs/SETUP_AND_API.md": "setup_and_api.md",
    "docs/RUNNING_EXPERIMENTS.md": "running_experiments.md",
    "docs/REPO_MAP.md": "repo_map.md",
    "experiments/INDEX.md": "experiments_index.md",
    "reviewer_bundle/README.md": "reviewer_bundle.md",
}

LINK = re.compile(r"(\]\()([^)\s]+)(\))")


def transform(src_repo_path: str, text: str) -> str:
    base = pathlib.PurePosixPath(src_repo_path).parent

    def repl(m: re.Match) -> str:
        tgt = m.group(2)
        if tgt.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        anchor = ""
        if "#" in tgt:
            tgt, anchor = tgt.split("#", 1)
            anchor = "#" + anchor
        if not tgt:
            return m.group(0)
        resolved = str(pathlib.PurePosixPath(base, tgt).as_posix() if str(base) != "." else tgt)
        resolved = re.sub(r"^\.\./", "", resolved)
        # site pages
        if resolved in SITE_SIBLINGS:
            return f"{m.group(1)}{SITE_SIBLINGS[resolved]}{anchor}{m.group(3)}"
        # release shortcuts
        if resolved.endswith("/releases/tag/v1.0.0-codes-results"):
            url = f"{GITHUB}/releases/tag/v1.0.0-codes-results"
            return f"{m.group(1)}{url}{anchor}{m.group(3)}"
        # images: docs/ holds the SVGs at its top level = the site root
        if resolved.startswith("assets/"):
            return f"{m.group(1)}{resolved.split('/')[-1]}{anchor}{m.group(3)}"
        # top-level community files
        if resolved in ("LICENSE", "CITATION.cff"):
            return f"{m.group(1)}{GITHUB}/blob/main/{resolved}{anchor}{m.group(3)}"
        # everything else: a repository path → GitHub
        return f"{m.group(1)}{GITHUB}/blob/main/{resolved}{anchor}{m.group(3)}"

    out = LINK.sub(repl, text)
    # Python-Markdown passes HTML-block content through raw unless blocks are
    # marked markdown="1" (GitHub/GFM needs no marker — the repository README
    # keeps its plain <div>/<details>; only the site copy is patched).
    out = out.replace('<div align="center">', '<div align="center" markdown="1">')
    out = out.replace('<details>', '<details markdown="1">')
    return out


def main() -> int:
    for src, dst, front in PAGES:
        p = ROOT / src
        if not p.is_file():
            print(f"ERROR: missing source {src}", file=sys.stderr)
            return 1
        out = DOCS / dst
        body = transform(src, p.read_text(encoding="utf-8"))
        out.write_text(front + body, encoding="utf-8")
        print(f"synced {src} → docs_site/docs/{dst}")
    # keep the figure assets at the docs top level (site root) AND under
    # docs/assets/ so both markdown and <img src="assets/..."> references resolve
    assets = ROOT / "assets"
    (DOCS / "assets").mkdir(exist_ok=True)
    for svg in assets.glob("*.svg"):
        (DOCS / svg.name).write_bytes(svg.read_bytes())
        (DOCS / "assets" / svg.name).write_bytes(svg.read_bytes())
        print(f"asset copied: {svg.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
