import hashlib
import json
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "sp2027/analysis/RESULTS_LOCK_H1PC.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    lock = json.loads(LOCK.read_text())
    predecessor = ROOT / lock["predecessor_lock"]
    assert digest(predecessor) == lock["predecessor_lock_sha256"]
    control = ROOT / lock["h1_positive_control"]["h1_check"]
    rows = list(csv.DictReader(control.open()))
    assert len(rows) == 3
    assert all(row["h1_verdict"] == "H1" for row in rows)
    assert lock["e1_public_h1"] == {"numerator": 0, "denominator": 54}
    assert lock["exp034_positive_control_h1"] == {"numerator": 0, "denominator": 12}
    assert lock["h1_positive_control"]["n"] == lock["h1_positive_control"]["pass"] + lock["h1_positive_control"]["fail"]
    assert lock["h1_positive_control"]["pass"] == 3
    assert lock["arm_accounting"]["actual_repository_evidence_arms"] == 35 + 1
    print("RESULTS_LOCK_H1PC_PASS")


if __name__ == "__main__":
    main()
