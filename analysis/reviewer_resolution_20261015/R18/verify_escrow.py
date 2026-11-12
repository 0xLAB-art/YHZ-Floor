import hashlib
import json
import os
import re

ROOT = "/mnt/nvme5/ACTS-Attack"
R18 = os.path.join(ROOT, "sp2027/analysis/reviewer_resolution_20261015/R18")
PAPER = os.path.join(ROOT, "sp2027/paper/split_rebuild_evidence_promotion")
MAIN = os.path.join(PAPER, "main_sections")
SUPP = os.path.join(PAPER, "supp_sections")
CHECKS = []

S17_NOTE = "The earlier unblinded key-recovery exhibit (16/16 reported AES key recoveries) is retained as historical provenance only: its physical-run identity, denominator and generating conditions are not reconstructed here, and it supplies no baseline or comparison."


def add(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": detail})


def norm(path):
    with open(path, encoding="utf-8") as handle:
        return re.sub(r"\s+", " ", handle.read())


def sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


res05 = norm(os.path.join(MAIN, "05_results.tex"))
s12 = norm(os.path.join(SUPP, "S12_escrow.tex"))
s17 = norm(os.path.join(SUPP, "S17_historical_arms.tex"))
histdoc = norm(os.path.join(PAPER, "artifact_documentation/HISTORICAL_AND_DISCOVERY_DETAIL.tex"))
decisions = norm(os.path.join(ROOT, "sp2027/ledger/DECISIONS.md"))
lock = norm(os.path.join(ROOT, "sp2027/analysis/RESULTS_LOCK.json"))
registry = norm(os.path.join(ROOT, "sp2027/paper/MASTER_EXPERIMENT_REGISTRY.md"))
archive = norm(os.path.join(ROOT, "sp2027/paper/archive/main_spliced_working_2026-10-01.tex"))

add(
    "r18_05_matched_baseline_removed",
    "unblinded" not in res05 and "escrow-effect estimate" not in res05,
    f"unblinded={res05.count('unblinded')} estimate={res05.count('escrow-effect estimate')}",
)
add(
    "r18_s12_old_removed",
    "unblinded" not in s12 and "16/16" not in s12,
    f"unblinded={s12.count('unblinded')} bytes16={s12.count('16/16')}",
)
add("r18_s17_provenance_note", S17_NOTE in s17, f"present={S17_NOTE in s17}")

counts = {}
for base in (MAIN, SUPP):
    for name in sorted(os.listdir(base)):
        if name.endswith(".tex"):
            counts[os.path.join(base, name)] = norm(os.path.join(base, name)).count("unblinded")
total = sum(counts.values())
s17_path = os.path.join(SUPP, "S17_historical_arms.tex")
add(
    "r18_unblinded_single",
    total == 1 and counts.get(s17_path) == 1,
    f"total={total} holds={[p for p, c in counts.items() if c]}",
)

d1a = "16/16 bytes, XOR difference zero after 200,000 samples"
d1b = "16/16 recovered bytes and zero XOR"
add(
    "r18_05_d1_bytes_intact",
    res05.count("16/16") == 2 and d1a in res05 and d1b in res05,
    f"count={res05.count('16/16')} d1a={d1a in res05} d1b={d1b in res05}",
)

add(
    "r18_prov_decisions",
    "v1's unblinded 16/16 demoted to the cautionary example per plan E5" in decisions,
    f"count={decisions.count('demoted to the cautionary example')}",
)
add(
    "r18_prov_lock",
    "the earlier uniform 16/16 did not reproduce under the escrow-blinded protocol; this is evidence non-robustness, not a matched causal effect" in lock,
    f"present={'did not reproduce under the escrow-blinded protocol' in lock}",
)
add(
    "r18_prov_registry",
    "Historical 16/16 remains summary-only and is not reconstructed from these" in registry
    and "the 16/16 historical result remains excluded" in registry,
    f"summary_only={'remains summary-only' in registry} excluded={'remains excluded' in registry}",
)
add(
    "r18_prov_archive",
    "(16/16 AES key recoveries) was graded by the same infrastructure that held" in archive
    and "an unblinded oracle" in archive,
    f"graded={'graded by the same infrastructure' in archive} oracle={'an unblinded oracle' in archive}",
)
add(
    "r18_histdoc_intact",
    histdoc.count("16/16") >= 2,
    f"count={histdoc.count('16/16')}",
)

note_at = s17.find(S17_NOTE)
prev_at = s17.find("aggregates do not add physical repetitions.")
next_at = s17.find("The discovery ledger keeps source paths and full evidence classifications")
add(
    "r18_s17_placement",
    -1 < prev_at < note_at < next_at,
    f"prev={prev_at} note={note_at} next={next_at}",
)

hashes = {
    path: sha(os.path.join(ROOT, path))
    for path in [
        "sp2027/paper/split_rebuild_evidence_promotion/main_sections/05_results.tex",
        "sp2027/paper/split_rebuild_evidence_promotion/supp_sections/S12_escrow.tex",
        "sp2027/paper/split_rebuild_evidence_promotion/supp_sections/S17_historical_arms.tex",
        "sp2027/paper/split_rebuild_evidence_promotion/artifact_documentation/HISTORICAL_AND_DISCOVERY_DETAIL.tex",
        "sp2027/ledger/DECISIONS.md",
        "sp2027/analysis/RESULTS_LOCK.json",
        "sp2027/paper/MASTER_EXPERIMENT_REGISTRY.md",
        "sp2027/paper/archive/main_spliced_working_2026-10-01.tex",
    ]
}
failures = [entry["name"] for entry in CHECKS if not entry["ok"]]
os.makedirs(R18, exist_ok=True)
with open(os.path.join(R18, "ESCROW_TRACE.json"), "w", encoding="utf-8") as handle:
    json.dump({"checks": CHECKS, "all_pass": not failures, "failures": failures}, handle, indent=2, sort_keys=True)
    handle.write("\n")
with open(os.path.join(R18, "VALIDATION.json"), "w", encoding="utf-8") as handle:
    json.dump({"all_pass": not failures, "checks": len(CHECKS), "failures": failures, "file_hashes": hashes}, handle, indent=2, sort_keys=True)
    handle.write("\n")
print(json.dumps({"checks": len(CHECKS), "all_pass": not failures, "failures": failures}, indent=2))
