import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def main():
    manifest = json.loads((HERE / "INPUT_FREEZE.json").read_text())
    changed, missing = [], []
    for rel, expected in manifest["files"].items():
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            changed.append(rel)
    result = {"checked": len(manifest["files"]), "changed": changed, "missing": missing,
              "status": "PASS" if not changed and not missing else "CHANGES_REQUIRE_RECONCILIATION"}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
