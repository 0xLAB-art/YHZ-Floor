import hashlib
import json
import os
import re

ROOT = "/mnt/nvme5/ACTS-Attack"
HARNESS = os.path.join(ROOT, "ACTS-ATTACK/harness")
R17 = os.path.join(ROOT, "sp2027/analysis/reviewer_resolution_20261015/R17")
PAPER = os.path.join(ROOT, "sp2027/paper/split_rebuild_evidence_promotion")
TRACES_H1B = os.path.join(HARNESS, "results_c2b_h1b/traces")
TRACES_PQ = os.path.join(HARNESS, "results_c2b_pq/traces")
CHECKS = []


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


def load_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def row_matches(row, truth):
    verdict, groups, key_share, negotiated, fin_client, fin_server = truth
    finished = row.get("finished", {})
    return (
        row.get("verdict") == verdict
        and row.get("client_groups") == groups
        and row.get("client_key_share") == key_share
        and row.get("negotiated_group") == negotiated
        and finished.get("client") is fin_client
        and finished.get("server") is fin_server
        and row.get("trace_disagreement") is False
    )


H1B_CELL = "S-allow_C-hybrid-second"
H1B_TRUTH = ("classical", ["X25519", "X25519MLKEM768"], ["X25519"], "X25519", True, True)
PQ_TRUTH = {
    "S-allow_C-classical-only": ("classical", ["X25519"], ["X25519"], "X25519", True, True),
    "S-allow_C-hybrid-first": ("hybrid", ["X25519MLKEM768", "X25519"], ["X25519MLKEM768"], "X25519MLKEM768", True, True),
    "S-allow_C-hybrid-only": ("hybrid", ["X25519MLKEM768"], ["X25519MLKEM768"], "X25519MLKEM768", True, True),
    "S-classical_C-classical-only": ("classical", ["X25519"], ["X25519"], "X25519", True, True),
    "S-classical_C-hybrid-first": ("classical", ["X25519MLKEM768", "X25519"], ["X25519"], "X25519", True, True),
    "S-classical_C-hybrid-only": ("reject", ["X25519MLKEM768"], ["X25519MLKEM768"], None, False, False),
    "S-require_C-classical-only": ("reject", ["X25519"], ["X25519"], None, False, False),
    "S-require_C-hybrid-first": ("hybrid", ["X25519MLKEM768", "X25519"], ["X25519MLKEM768"], "X25519MLKEM768", True, True),
    "S-require_C-hybrid-only": ("hybrid", ["X25519MLKEM768"], ["X25519MLKEM768"], "X25519MLKEM768", True, True),
}

h1b_rows = load_jsonl(os.path.join(HARNESS, "results_c2b_h1b/c2b_records.jsonl"))
bad = [r.get("run_id") for r in h1b_rows if r.get("cell") != H1B_CELL or not row_matches(r, H1B_TRUTH)]
h1b_reps = sorted(r.get("rep") for r in h1b_rows)
add(
    "h1b_rows_match",
    len(h1b_rows) == 5 and h1b_reps == [1, 2, 3, 4, 5] and not bad,
    f"rows={len(h1b_rows)} reps={h1b_reps} bad={bad}",
)

with open(os.path.join(HARNESS, "results_c2b_h1b/c2b_verdicts.json"), encoding="utf-8") as handle:
    h1b_verdicts = json.load(handle)
h1b_cell_verdicts = h1b_verdicts.get("cells", {}).get(H1B_CELL, {})
add(
    "h1b_verdicts",
    h1b_verdicts.get("n_records") == 5
    and h1b_verdicts.get("trace_disagreements") == []
    and h1b_cell_verdicts.get("verdicts") == ["classical"] * 5
    and h1b_cell_verdicts.get("complete") is True
    and h1b_cell_verdicts.get("unanimous") is True,
    f"n={h1b_verdicts.get('n_records')} td={h1b_verdicts.get('trace_disagreements')}",
)

pq_rows = load_jsonl(os.path.join(HARNESS, "results_c2b_pq/c2b_records.jsonl"))
add("pq_rows_total", len(pq_rows) == 45, f"rows={len(pq_rows)}")
bad = []
reps = {}
for row in pq_rows:
    cell = row.get("cell")
    reps.setdefault(cell, []).append(row.get("rep"))
    truth = PQ_TRUTH.get(cell)
    if truth is None or not row_matches(row, truth):
        bad.append(f"{cell}:{row.get('rep')}")
bad_reps = sorted(c for c, v in reps.items() if sorted(v) != [1, 2, 3, 4, 5])
add("pq_rows_match", not bad and not bad_reps and set(reps) == set(PQ_TRUTH), f"bad={bad[:6]} bad_reps={bad_reps}")

with open(os.path.join(HARNESS, "results_c2b_pq/c2b_verdicts.json"), encoding="utf-8") as handle:
    pq_verdicts = json.load(handle)
cells = pq_verdicts.get("cells", {})
bad_cells = []
for name, truth in PQ_TRUTH.items():
    entry = cells.get(name, {})
    if (
        entry.get("verdicts") != [truth[0]] * 5
        or entry.get("complete") is not True
        or entry.get("unanimous") is not True
    ):
        bad_cells.append(name)
add(
    "pq_verdicts",
    pq_verdicts.get("n_records") == 45
    and pq_verdicts.get("trace_disagreements") == []
    and set(cells) == set(PQ_TRUTH)
    and not bad_cells,
    f"n={pq_verdicts.get('n_records')} bad_cells={bad_cells}",
)

bad = [
    i
    for i in range(1, 6)
    if "00 0a 00 06 00 04 00 1d 11 ec" not in norm(os.path.join(TRACES_H1B, f"c2b_{H1B_CELL}_r{i}_cli.txt"))
]
add("h1b_cli_groups", not bad, f"bad_reps={bad}")

bad = [
    i
    for i in range(1, 6)
    if "00 33 00 26 00 24 00 1d 00 20" not in norm(os.path.join(TRACES_H1B, f"c2b_{H1B_CELL}_r{i}_cli.txt"))
]
add("h1b_cli_keyshare", not bad, f"bad_reps={bad}")

bad = []
for i in range(1, 6):
    text = norm(os.path.join(TRACES_H1B, f"c2b_{H1B_CELL}_r{i}_cli.txt"))
    if "Finished" not in text or "HelloRetryRequest" in text or "cf 21 ad 74" in text or text.count("ClientHello") != 1:
        bad.append(i)
add("h1b_cli_no_hrr", not bad, f"bad_reps={bad}")

bad = [
    i
    for i in range(1, 6)
    if "00 33 00 24 00 1d 00 20" not in norm(os.path.join(TRACES_H1B, f"c2b_{H1B_CELL}_r{i}_srv.txt"))
]
add("h1b_srv_keyshare", not bad, f"bad_reps={bad}")

bad = []
for i in range(1, 6):
    text = norm(os.path.join(TRACES_H1B, f"c2b_{H1B_CELL}_r{i}_srv.txt"))
    if "Finished" not in text or "cf 21 ad 74" in text or "HelloRetryRequest" in text:
        bad.append(i)
add("h1b_srv_no_hrr", not bad, f"bad_reps={bad}")

bad = []
for cell in ["S-allow_C-hybrid-first", "S-classical_C-hybrid-first", "S-require_C-hybrid-first"]:
    for i in range(1, 6):
        text = norm(os.path.join(TRACES_PQ, f"c2b_{cell}_r{i}_cli.txt"))
        if "00 0a 00 06 00 04 11 ec 00 1d" not in text:
            bad.append(f"{cell}:{i}")
add("pq_hybrid_first_groups", not bad, f"bad={bad}")

bad = []
for i in range(1, 6):
    text = norm(os.path.join(TRACES_PQ, f"c2b_S-classical_C-hybrid-first_r{i}_cli.txt"))
    if text.count("cf 21 ad 74") != 1 or text.count("ClientHello") != 2:
        bad.append(i)
add("pq_sclassical_hrr", not bad, f"bad_reps={bad}")

bad = []
for i in range(1, 6):
    text = norm(os.path.join(TRACES_PQ, f"c2b_S-classical_C-hybrid-first_r{i}_cli.txt"))
    if "00 33 04 c6 04 c4 11 ec 04 c0" not in text or "00 33 00 26 00 24 00 1d 00 20" not in text:
        bad.append(i)
add("pq_sclassical_keyshares", not bad, f"bad_reps={bad}")

bad = []
for cell in ["S-classical_C-hybrid-only", "S-require_C-classical-only"]:
    for endpoint in ["cli", "srv"]:
        for i in range(1, 6):
            text = norm(os.path.join(TRACES_PQ, f"c2b_{cell}_r{i}_{endpoint}.txt"))
            if "Finished" in text:
                bad.append(f"{cell}:{i}:{endpoint}")
add("reject_finished_absent", not bad, f"bad={bad}")

res05 = norm(os.path.join(PAPER, "main_sections/05_results.tex"))
s13 = norm(os.path.join(PAPER, "supp_sections/S13_c2b.tex"))

P05_NEW = [
    "parsed negotiated key-share group",
    "pooled verdicts match the predeclared table",
    "client's initial key share follows its configured first group",
    "lists X25519 first with an X25519-only",
    "while the hybrid-first matrix cell against the same server lists X25519MLKEM768 first with a hybrid key share and negotiates the hybrid group in 5/5",
    "Order and key share change together",
    "build-specific preference observation",
    "outer record type alone does not evidence decrypted payload",
    "acceptance rests on the Finished messages instead",
    "The implemented channel check is not a bidirectional echo test",
]
P05_REG = [
    "without a provider/model call",
    "outside that boundary",
    "host kernel, CPU, external services and any provider remain trusted components",
    "implementation demonstration",
    "claims neither necessity, sufficiency nor reliability for a networked agent with mutable backend state",
    "representative missing-component negative control",
    "H1=0/12",
]
P05_ABSENT = [
    "advertising hybrid support",
    "hybrid-first offers carry",
    "Both endpoint traces and the predeclared verdict table agree",
]
S13_PRESENT = [
    "with no endpoint disagreement on the parsed key-share group",
    "Acceptance uses the negotiated key-share group and the Finished messages",
    "whose outer record type alone does not evidence decrypted payload",
    "no echo test was run",
    r"\texttt{supported\_groups} with X25519 first",
    r"X25519-only initial \texttt{key\_share}",
    "versus 5/5 hybrid for the matrix's hybrid-first cell on the same server",
    "not a controlled list-order effect or additional matrix repetitions",
]
S13_ABSENT = [
    "zero trace disagreements",
    "versus hybrid-first's",
    "5/5 hybrid in the matrix",
]

missing = [p for p in P05_NEW if p not in res05]
add("r17_05_results_present", not missing, f"missing={missing}")
present = [p for p in P05_ABSENT if p in res05]
add("r17_05_results_absent", not present, f"present={present}")
missing = [p for p in P05_REG if p not in res05]
add("r16_05_results_regression", not missing, f"missing={missing}")
missing = [p for p in S13_PRESENT if p not in s13]
add("r17_s13_present", not missing, f"missing={missing}")
present = [p for p in S13_ABSENT if p in s13]
add("r17_s13_absent", not present, f"present={present}")

hashes = {
    path: sha(os.path.join(ROOT, path))
    for path in [
        "sp2027/paper/split_rebuild_evidence_promotion/main_sections/05_results.tex",
        "sp2027/paper/split_rebuild_evidence_promotion/supp_sections/S13_c2b.tex",
        "ACTS-ATTACK/harness/results_c2b_h1b/c2b_records.jsonl",
        "ACTS-ATTACK/harness/results_c2b_h1b/c2b_verdicts.json",
        "ACTS-ATTACK/harness/results_c2b_pq/c2b_records.jsonl",
        "ACTS-ATTACK/harness/results_c2b_pq/c2b_verdicts.json",
    ]
}
failures = [entry["name"] for entry in CHECKS if not entry["ok"]]
os.makedirs(R17, exist_ok=True)
trace = {"checks": CHECKS, "all_pass": not failures, "failures": failures}
validation = {"all_pass": not failures, "checks": len(CHECKS), "failures": failures, "file_hashes": hashes}
with open(os.path.join(R17, "PREFERENCE_TRACE.json"), "w", encoding="utf-8") as handle:
    json.dump(trace, handle, indent=2, sort_keys=True)
    handle.write("\n")
with open(os.path.join(R17, "VALIDATION.json"), "w", encoding="utf-8") as handle:
    json.dump(validation, handle, indent=2, sort_keys=True)
    handle.write("\n")
print(json.dumps({"checks": len(CHECKS), "all_pass": not failures, "failures": failures}, indent=2))
