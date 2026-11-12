import hashlib
import json
import pathlib

ROOT = pathlib.Path("/mnt/nvme5/ACTS-Attack")
PATHS = {
    "limits": ROOT / "sp2027/paper/split_rebuild_evidence_promotion/main_sections/08_limits.tex",
    "ethics": ROOT / "docs/revision/submission_final/HOTCRP_ETHICS_DRAFT.md",
    "ai": ROOT / "docs/revision/submission_final/HOTCRP_GENERATIVE_AI_DRAFT.md",
}
raw = {k: p.read_text(encoding="utf-8") for k, p in PATHS.items()}
norm = {k: " ".join(v.split()) for k, v in raw.items()}
checks = []

def check(name, cond):
    checks.append({"name": name, "pass": bool(cond)})

check("limits_rationale", "disclosable" in norm["limits"] and "research-artifact defects rather than deployed-system exploits" in norm["limits"])
check("limits_plan", "evidence-bounded notifications to the affected benchmark maintainers" in norm["limits"])
check("limits_timing", "before submission" in norm["limits"])
check("limits_status", "no notification has been sent as of this revision" in norm["limits"])
check("limits_hedge_removed", "Maintainer notification is not documented" not in norm["limits"])
check("ethics_determination", "disclosable research-artifact defects" in norm["ethics"])
check("ethics_plan", "will send evidence-bounded notifications" in norm["ethics"])
check("ethics_status", "No maintainer or vendor notification has been sent as of October 15, 2026" in norm["ethics"])
check("ethics_field_complete", "Ethics field text (complete, prepared for registration)" in norm["ethics"])
check("ethics_deferral_removed", "AUTHOR REVIEW REQUIRED" not in norm["ethics"] and "should be reviewed by the authors" not in norm["ethics"])
check("ai_field_complete", "Generative-AI field text (complete, prepared for registration)" in norm["ai"])
check("ai_scope_stated", "no finer model-version or inspection claim is made than the records support" in norm["ai"])
check("ai_deferral_removed", "AUTHOR REVIEW REQUIRED" not in norm["ai"] and "must verify every" not in norm["ai"])
forbidden = ["notification was sent", "notifications were sent", "has been notified", "have been notified", "was contacted", "were contacted"]
joined = "\n".join(norm.values())
check("no_affirmative_notification_claims", all(f not in joined for f in forbidden))
files = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in PATHS.values()}
result = {"checks": len(checks), "all_pass": all(c["pass"] for c in checks), "failures": [c["name"] for c in checks if not c["pass"]], "files": files}
out = pathlib.Path(__file__).resolve().parent / "VALIDATION.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
