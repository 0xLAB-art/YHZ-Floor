import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "sp2027/analysis/RESULTS_LOCK_V4.json"
OLD = ROOT / "sp2027/analysis/RESULTS_LOCK.json"
MANIFEST = ROOT / "sp2027/agent-eval/R1_CLEAN_COHORT_V4_02_MANIFEST.json"
LEDGER = ROOT / "sp2027/agent-eval/R1_CLEAN_COHORT_V4_ROW_LEDGER.csv"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    d = json.loads(LOCK.read_text())
    assert sha(OLD) == d["predecessor_lock_sha256"]
    assert sha(MANIFEST) == d["v4"]["manifest_sha256"]
    assert sha(LEDGER) == d["v4"]["row_ledger_sha256"]
    rows = list(csv.DictReader(LEDGER.open()))
    v = d["v4"]
    assert len(rows) == v["planned"] == v["physical"] == v["retained"]
    assert len({r["entry_id"] for r in rows}) == v["unique_identities"]
    assert len({r["run_id"] for r in rows}) == v["unique_identities"]
    statuses = {r["status"]: sum(x["status"] == r["status"] for x in rows) for r in rows}
    assert statuses == {"ORACLE_FAIL": 4, "SUCCESS": 8}
    assert sum(r["eligible"] == "true" for r in rows) == v["retained"]
    assert v["success"] + v["oracle_fail"] == v["terminal_statuses"]
    assert v["provider_unavailable"] == 0
    assert v["conditional"]["success"] == v["operational"]["success"] == 8
    assert v["conditional"]["denominator"] == v["operational"]["denominator"] == 12
    l = d["legacy_values_retained"]
    assert l["planned"] == l["provider_unavailable"] + l["non_gateway"]
    assert l["valid_graded"] == l["non_gateway"] - l["relay_defects"]
    assert l["strict_admissible"] == l["valid_graded"] - l["historical_clock_exclusions"]
    assert l["operational"]["denominator"] == l["strict_admissible"] + l["provider_unavailable"]
    print("RESULTS_LOCK_V4_PASS")
    print("legacy=10/19 conditional, 10/47 operational; v4=8/12 both")
    print("arms=34 mapped + 1 historical = 35 actual; MAP-CLOSURE-034 non-arm")

if __name__ == "__main__":
    main()
