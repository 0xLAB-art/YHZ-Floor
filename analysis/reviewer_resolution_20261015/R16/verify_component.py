import csv
import hashlib
import json
import os
import re

ROOT = "/mnt/nvme5/ACTS-Attack"
R16 = os.path.join(ROOT, "sp2027/analysis/reviewer_resolution_20261015/R16")
PKG = os.path.join(ROOT, "sp2027/agent-eval/h1_positive_control_20261014_v2")
PAPER = os.path.join(ROOT, "sp2027/paper/split_rebuild_evidence_promotion")
DIGEST = "sha256:f8cddd76e34aed0e04ee3f41a958a213cf72f6658996beb41888418101a41040"
HEADER = ["control_row", "source", "configuration", "task", "immutable_environment", "execution", "result", "h1_verdict", "run_id"]
FIELDS = HEADER[1:7]
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


csv_path = os.path.join(PKG, "H1_POSITIVE_CONTROL_H1_CHECK.csv")
add("h1_check_csv_exists", os.path.isfile(csv_path), csv_path)
rows = []
if os.path.isfile(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
add("h1_check_header_exact", bool(rows) and rows[0] == HEADER, str(rows[0] if rows else None))
data = rows[1:] if rows else []
add("h1_check_three_rows", len(data) == 3, "rows=%d" % len(data))
add("h1_check_control_rows", sorted(row[0] for row in data) == ["H1PC201", "H1PC202", "H1PC203"], str([row[0] for row in data]))
field_ok = len(data) == 3 and all(
    all(row[HEADER.index(field)] == "PASS" for field in FIELDS) for row in data)
add("h1_check_all_fields_pass", field_ok, "six fields per row")
add("h1_check_verdict_h1", len(data) == 3 and all(row[HEADER.index("h1_verdict")] == "H1" for row in data), str([row[7] for row in data]))
add("h1_check_run_ids", len(data) == 3 and all("__sha256_fixed_payload__" in row[HEADER.index("run_id")] for row in data), "")

manifest_path = os.path.join(PKG, "H1_POSITIVE_CONTROL_MANIFEST.json")
manifest_text = norm(manifest_path) if os.path.isfile(manifest_path) else ""
add("manifest_exists", os.path.isfile(manifest_path), manifest_path)
add("manifest_digest_pinned", DIGEST in manifest_text, DIGEST)
add("manifest_base_digest", "base_image_digest" in manifest_text, "")

results_path = os.path.join(PKG, "H1_POSITIVE_CONTROL_RESULTS.md")
results_text = norm(results_path) if os.path.isfile(results_path) else ""
add("results_records_3_of_3", "3/3" in results_text and "POSITIVE CONTROL PASSED" in results_text, "")
add("results_records_separation", "0/54" in results_text and "0/12" in results_text, "")

limit_path = os.path.join(PAPER, "main_sections/05_results.tex")
limit_text = norm(limit_path)
add("results_tex_no_provider_call", "without a provider/model call" in limit_text, "")
add("results_tex_component_boundary", "outside that boundary" in limit_text and "host kernel, CPU, external services and any provider remain trusted components" in limit_text, "")
add("results_tex_implementation_demo", "implementation demonstration" in limit_text and "claims neither necessity, sufficiency nor reliability" in limit_text and "mutable backend state" in limit_text, "")
add("results_tex_negative_control_named", "representative missing-component negative control" in limit_text and "H1=0/12" in limit_text, "")

fw_path = os.path.join(PAPER, "main_sections/02_framework.tex")
fw_text = norm(fw_path)
add("framework_tex_environment_bound", "The environment component is bounded at the digest-identified runtime and its declared inputs" in fw_text and "outside that boundary" in fw_text, "")

s_path = os.path.join(PAPER, "supp_sections/S04c_h1_provenance_control.tex")
s_text = norm(s_path)
add("supplement_component_bounded", "component-bounded" in s_text and "remain trusted components" in s_text, "")
add("supplement_networked_reuse_bound", "constrained provider egress" in s_text and "outside the pinned identity" in s_text, "")
add("supplement_population_separation", "H1=0/54" in s_text and "H1=0/12" in s_text and "3/3" in s_text, "")

hashes = {path: sha(os.path.join(ROOT, path)) for path in [
    "sp2027/paper/split_rebuild_evidence_promotion/main_sections/05_results.tex",
    "sp2027/paper/split_rebuild_evidence_promotion/main_sections/02_framework.tex",
    "sp2027/paper/split_rebuild_evidence_promotion/supp_sections/S04c_h1_provenance_control.tex",
]}
add("edited_file_hashes_recorded", all(len(value) == 64 for value in hashes.values()), json.dumps(hashes))

failures = [entry["name"] for entry in CHECKS if not entry["ok"]]
trace = {"checks": CHECKS, "all_pass": not failures, "failures": failures}
validation = {"checks": len(CHECKS), "all_pass": not failures, "failures": failures, "file_hashes": hashes}

with open(os.path.join(R16, "H1_COMPONENT_TRACE.json"), "w", encoding="utf-8") as handle:
    json.dump(trace, handle, indent=2, sort_keys=True)
    handle.write("\n")
with open(os.path.join(R16, "VALIDATION.json"), "w", encoding="utf-8") as handle:
    json.dump(validation, handle, indent=2, sort_keys=True)
    handle.write("\n")

print(json.dumps({"checks": len(CHECKS), "all_pass": not failures, "failures": failures}, indent=2))
