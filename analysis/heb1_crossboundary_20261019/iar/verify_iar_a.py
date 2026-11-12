#!/usr/bin/env python3
"""Independent offline verifier for IAR-A (Stage01 cross-boundary transfer).

Re-runs the two frozen Stage01 components on the archived IAR-A inputs and
re-checks every composition fact, file hash, and stored verdict against
iar_a_results.json. Stdlib only; no campaign artifact is modified; temp
bundles are written under /tmp/opencode.

Usage:  python3 sp2027/analysis/heb1_crossboundary_20261019/iar/verify_iar_a.py
Exit 0 = all checks pass (warnings allowed); exit 1 = at least one FAIL.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
ANA = REPO / "sp2027" / "analysis"
IAR = ANA / "heb1_crossboundary_20261019" / "iar" / "iar_a_20261019"
CLEAN = ANA / "contract_sound_stage01_hardened_v2_20261018" / "stage1" / "clean" / "clean_01"
VALIDATOR = ANA / "contract_sound_stage01_validator_v2.py"
REFERENCE = ANA / "contract_sound_stage01_reference_verifier_v2.py"
TMP = Path("/tmp/opencode/iar_a_verify")
RESULTS = IAR / "iar_a_results.json"
MEMO = IAR / "IAR_A_RESULTS_MEMO.md"

EXPECTED = {
    "validator_sha256": "f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a",
    "reference_sha256": "15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b",
    "results_sha256": "c3f225825d8b0989d6a14336ba44e80342c572a23bee9b64b79448f300401313",
    "registry_X_candidate": "aed7e1d8456b4e98548b7bb8b88dd2fbc7ae191e1feb7701448733b6eeaca8ad",
    "registry_Y_candidate": "e1647eab901a58ebef676f731590014cc86620bb21cf5a594bebab2e65a3aae7",
    "X_session": "iar-session-X",
    "Y_session": "stage01-hardened-session-001",
}
PROTECTED = {
    ANA / "RESULTS_LOCK.json": "4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39",
    ANA / "RESULTS_LOCK_H1PC.json": "8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103",
    REPO / "sp2027" / "paper" / "main.tex": "51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461",
    REPO / "sp2027" / "paper" / "main.pdf": "fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a",
}

CHECKS: list[tuple[str, str, str]] = []  # (status, name, detail)


def check(name: str, ok: bool, detail: str = "", warn_only: bool = False) -> None:
    CHECKS.append(("WARN" if (warn_only and not ok) else ("PASS" if ok else "FAIL"), name, detail))


def warn(name: str, detail: str) -> None:
    CHECKS.append(("WARN", name, detail))


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parse_json_line(text: str):
    for line in reversed([ln for ln in text.splitlines() if ln.strip()]):
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    return None


def run_validator(cert_path: Path):
    with open(cert_path, "rb") as fh:
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR)], stdin=fh, capture_output=True, cwd=str(IAR)
        )
    out = proc.stdout.decode("utf-8", "replace")
    return proc.returncode, parse_json_line(out), out, proc.stderr.decode("utf-8", "replace")


def run_reference(bundle_path: Path):
    proc = subprocess.run(
        [sys.executable, str(REFERENCE), str(bundle_path)], capture_output=True, cwd=str(IAR)
    )
    out = proc.stdout.decode("utf-8", "replace")
    return proc.returncode, parse_json_line(out), out, proc.stderr.decode("utf-8", "replace")


def write_bundle(name: str, cert: Path, target: Path, cand: Path) -> Path:
    bpath = TMP / f"{name}.bundle.json"
    bpath.write_text(json.dumps({
        "case_id": name,
        "target_state_path": str(target),
        "candidate_path": str(cand),
        "certificate_path": str(cert),
    }, indent=1, sort_keys=True) + "\n")
    return bpath


SPECS = [
    dict(name="baseline_A0", pub=CLEAN / "public_certificate.json",
         priv=CLEAN / "certificate.private.json", target=CLEAN / "target_state.private.json",
         cand=CLEAN / "candidate.json", exp_val="ACCEPT", exp_ref="ACCEPTED",
         exp_err=[], stored="baseline_A0", exp_pub_sha=None),
    dict(name="A1_trace_candidate_splice", pub=IAR / "A1_trace_candidate_splice.public_certificate.json",
         priv=IAR / "A1_trace_candidate_splice.private_certificate.json", target=IAR / "y_target_state.private.json",
         cand=IAR / "y_candidate.json", exp_val="ACCEPT", exp_ref="ACCEPTED", exp_err=[],
         stored="A1_trace_candidate_splice",
         exp_pub_sha="1e738566ae78a61806c55ca6b54add650da3defce9543c3e706506f5b2e0b0f2"),
    dict(name="A1b_session_binding", pub=IAR / "A1b_session_binding.public_certificate.json",
         priv=IAR / "A1b_session_binding.private_certificate.json", target=IAR / "y_target_state.private.json",
         cand=IAR / "y_candidate.json", exp_val="REJECT", exp_ref="REJECTED",
         exp_err=["execution-session-binding"], stored=None, exp_pub_sha=None),
    dict(name="A2_trace_hash_wrong", pub=IAR / "A2_trace_hash_wrong.public_certificate.json",
         priv=IAR / "A2_trace_hash_wrong.private_certificate.json", target=IAR / "y_target_state.private.json",
         cand=IAR / "y_candidate.json", exp_val="ACCEPT", exp_ref="ACCEPTED", exp_err=[],
         stored="A2_trace_hash_wrong",
         exp_pub_sha="507af789005f062d43fa35b98985ee360c15ea27ad04b7e1d3161b07ed7baf41"),
    dict(name="A2_agent_session_mismatch", pub=IAR / "A2_agent_session_mismatch.public_certificate.json",
         priv=IAR / "A2_agent_session_mismatch.private_certificate.json", target=IAR / "y_target_state.private.json",
         cand=IAR / "y_candidate.json", exp_val="ACCEPT", exp_ref="ACCEPTED", exp_err=[],
         stored="A2_agent_session_mismatch",
         exp_pub_sha="0c29d1d26608c339bfa196bc7d2131eff479b8d0710163f0eef089040e3d06d2"),
    dict(name="A2_reference_claim_unbound", pub=IAR / "A2_reference_claim_unbound.public_certificate.json",
         priv=IAR / "A2_reference_claim_unbound.private_certificate.json", target=IAR / "y_target_state.private.json",
         cand=IAR / "y_candidate.json", exp_val="ACCEPT", exp_ref="ACCEPTED", exp_err=[],
         stored="A2_reference_claim_unbound",
         exp_pub_sha="f965153fe4ac67567055f1f30f11cab08aca3c92ddc0f4202f2e06f086cf77be"),
    dict(name="A3_relabeled_trace", pub=IAR / "A3_relabeled_trace.public_certificate.json",
         priv=IAR / "A3_relabeled_trace.private_certificate.json", target=IAR / "y_target_state.private.json",
         cand=IAR / "y_candidate.json", exp_val="ACCEPT", exp_ref="ACCEPTED", exp_err=[],
         stored="A3_relabeled_trace", exp_pub_sha=None),
]


def stored_entry(results: dict, key: str):
    if key is None:
        return None
    if key in results:
        return results[key]
    for e in results.get("A2_unbound_references", []):
        if e.get("variant") == key:
            return e
    return None


def main() -> int:
    TMP.mkdir(parents=True, exist_ok=True)

    # --- frozen component and archive integrity -------------------------------
    val_sha = sha256(VALIDATOR)
    ref_sha = sha256(REFERENCE)
    res_sha = sha256(RESULTS)
    check("component: validator bytes", val_sha == EXPECTED["validator_sha256"],
          f"sha256={val_sha}")
    check("component: reference bytes", ref_sha == EXPECTED["reference_sha256"],
          f"sha256={ref_sha}")
    check("archive: iar_a_results.json bytes", res_sha == EXPECTED["results_sha256"],
          f"sha256={res_sha}")
    results = json.loads(RESULTS.read_text())

    # registry facts
    reg = results.get("registry", {})
    check("registry: X failed-run entry",
          reg.get("X", {}).get("candidate_sha256") == EXPECTED["registry_X_candidate"]
          and reg.get("X", {}).get("effect_status") == "NOT_OBSERVED"
          and reg.get("X", {}).get("session_id") == EXPECTED["X_session"])
    check("registry: Y successful-run entry",
          reg.get("Y", {}).get("candidate_sha256") == EXPECTED["registry_Y_candidate"]
          and reg.get("Y", {}).get("effect_status") == "OBSERVED"
          and reg.get("Y", {}).get("session_id") == EXPECTED["Y_session"])

    # --- per-variant re-execution --------------------------------------------
    for spec in SPECS:
        nm = spec["name"]
        cert = json.loads(spec["pub"].read_text())

        # public cert byte hash vs archive record
        pub_sha = sha256(spec["pub"])
        if spec["exp_pub_sha"]:
            check(f"{nm}: public cert bytes vs archive",
                  pub_sha == spec["exp_pub_sha"], f"sha256={pub_sha}")
        else:
            check(f"{nm}: public cert readable", True, f"sha256={pub_sha}")

        # evidence file hashes
        ev_ok = True
        ev_detail = []
        for ev in cert.get("evidence", []):
            p = Path(ev["path"])
            got = sha256(p) if p.exists() else "MISSING"
            ev_ok &= got == ev["sha256"]
            ev_detail.append(f"{ev['kind']}={got[:12]}")
        check(f"{nm}: evidence file hashes", ev_ok, "; ".join(ev_detail))

        # candidate pointer
        cand_sha = sha256(spec["cand"])
        check(f"{nm}: candidate sha vs certificate pointer",
              cand_sha == cert.get("agent_artifact", {}).get("sha256"),
              f"candidate={cand_sha[:12]} pointer={str(cert.get('agent_artifact', {}).get('sha256'))[:12]}")

        # blind validator (stdin) and reference verifier (temp bundle)
        vrc, vverdict, vout, verr = run_validator(spec["pub"])
        bpath = write_bundle(nm, spec["priv"], spec["target"], spec["cand"])
        rrc, rverdict, rout, rerr = run_reference(bpath)

        check(f"{nm}: validator verdict == expected",
              isinstance(vverdict, dict) and vverdict.get("decision") == spec["exp_val"],
              f"decision={None if not isinstance(vverdict, dict) else vverdict.get('decision')} "
              f"reason={None if not isinstance(vverdict, dict) else vverdict.get('reason')}")
        check(f"{nm}: reference verdict == expected",
              isinstance(rverdict, dict) and rverdict.get("reference_verdict") == spec["exp_ref"]
              and sorted(rverdict.get("certificate_errors", [])) == sorted(spec["exp_err"]),
              f"verdict={None if not isinstance(rverdict, dict) else rverdict.get('reference_verdict')} "
              f"errors={None if not isinstance(rverdict, dict) else rverdict.get('certificate_errors')}")

        # stored archive verdicts
        stored = stored_entry(results, spec["stored"])
        if stored is None:
            warn(f"{nm}: stored verdict in archive", "no entry in iar_a_results.json")
        else:
            sv = stored.get("blind_validator", {}).get("verdict", {})
            rv = stored.get("reference_verifier", {}).get("verdict", {})
            check(f"{nm}: archive validator verdict matches re-run",
                  sv.get("decision") == vverdict.get("decision") and sv.get("reason") == vverdict.get("reason"),
                  f"archive={sv.get('decision')}/{sv.get('reason')}")
            check(f"{nm}: archive reference verdict matches re-run",
                  rv.get("reference_verdict") == rverdict.get("reference_verdict")
                  and sorted(rv.get("certificate_errors", [])) == sorted(rverdict.get("certificate_errors", [])),
                  f"archive={rv.get('reference_verdict')}/{rv.get('certificate_errors')}")

        # --- composition facts -------------------------------------------------
        exec_sess = cert.get("execution", {}).get("session_id")
        ev_by_kind = {e["kind"]: e for e in cert.get("evidence", [])}
        if nm == "A1_trace_candidate_splice":
            trace = json.loads(Path(ev_by_kind["execution_trace"]["path"]).read_text())
            author = json.loads(Path(ev_by_kind["agent_artifact"]["path"]).read_text())
            check("A1: execution identity credited to X", exec_sess == EXPECTED["X_session"],
                  f"execution.session_id={exec_sess}")
            check("A1: trace evidence record is X's",
                  Path(ev_by_kind["execution_trace"]["path"]).name == "x_execution_trace.json"
                  and trace.get("session_id") == EXPECTED["X_session"])
            check("A1: authorship evidence record is X's",
                  Path(ev_by_kind["agent_artifact"]["path"]).name == "x_agent_artifact.json"
                  and author.get("session_id") == EXPECTED["X_session"])
            check("A1: trace carries no candidate hash",
                  not any("candidate" in k for k in trace.keys()), f"trace keys={sorted(trace)}")
            check("A1: authorship record names candidate without a hash",
                  author.get("artifact") == "candidate.json" and not any("sha" in k for k in author.keys()),
                  f"authorship keys={sorted(author)}")
            check("A1: accepted candidate is Y's, not X's",
                  cert.get("agent_artifact", {}).get("sha256") == EXPECTED["registry_Y_candidate"]
                  and cert.get("agent_artifact", {}).get("sha256") != EXPECTED["registry_X_candidate"])
            check("A1: archive records registry mismatch (submitted != X)",
                  results["A1_trace_candidate_splice"].get("candidate_matches_registry") is False
                  and results["A1_trace_candidate_splice"].get("ground_truth_registry_origin") == "X")
        elif nm == "A1b_session_binding":
            trace = json.loads(Path(ev_by_kind["execution_trace"]["path"]).read_text())
            check("A1b: claimed execution Y but trace record is X's",
                  exec_sess == EXPECTED["Y_session"] and trace.get("session_id") == EXPECTED["X_session"],
                  f"execution={exec_sess} trace={trace.get('session_id')}")
            check("A1b: both components reject on session binding",
                  vverdict.get("reason") == "execution-session-binding"
                  and rverdict.get("certificate_errors") == ["execution-session-binding"])
        elif nm == "A2_trace_hash_wrong":
            check("A2a: declared trace_hash is zeroed",
                  cert.get("execution", {}).get("trace_hash") == "0" * 64,
                  f"trace_hash={cert.get('execution', {}).get('trace_hash')}")
            check("A2a: both components accept despite wrong declared trace_hash",
                  vverdict.get("decision") == "ACCEPT" and rverdict.get("reference_verdict") == "ACCEPTED")
        elif nm == "A2_agent_session_mismatch":
            author_path = Path(ev_by_kind["agent_artifact"]["path"])
            author = json.loads(author_path.read_text())
            check("A2b: authorship record relabeled to Y while execution/trace are X",
                  author_path.name == "x_agent_artifact_session_Y.json"
                  and author.get("session_id") == EXPECTED["Y_session"]
                  and exec_sess == EXPECTED["X_session"],
                  f"record={author_path.name} record_session={author.get('session_id')} execution={exec_sess}")
            check("A2b: both components accept the unbound authorship session",
                  vverdict.get("decision") == "ACCEPT" and rverdict.get("reference_verdict") == "ACCEPTED")
        elif nm == "A2_reference_claim_unbound":
            check("A2c: public claim reference_oracle_acceptance=ACCEPTED with no reference evidence",
                  cert.get("claims", {}).get("reference_oracle_acceptance") == "ACCEPTED"
                  and "reference_oracle_acceptance" not in ev_by_kind,
                  f"claim={cert.get('claims', {}).get('reference_oracle_acceptance')}")
            check("A2c: both components accept the unbound public claim",
                  vverdict.get("decision") == "ACCEPT" and rverdict.get("reference_verdict") == "ACCEPTED")
        elif nm == "A3_relabeled_trace":
            trace_path = Path(ev_by_kind["execution_trace"]["path"])
            trace = json.loads(trace_path.read_text())
            x_sha = sha256(IAR / "x_execution_trace.json")
            check("A3: trace evidence is the relabeled copy of X's trace",
                  trace_path.name == "x_trace_relabeled_Y.json"
                  and sha256(trace_path) != x_sha
                  and trace.get("session_id") == EXPECTED["Y_session"],
                  f"record={trace_path.name} session={trace.get('session_id')}")
            check("A3: declared trace_hash follows the rewritten bytes",
                  cert.get("execution", {}).get("trace_hash") == sha256(trace_path))
            check("A3: both components accept the rewritten unsigned metadata",
                  vverdict.get("decision") == "ACCEPT" and rverdict.get("reference_verdict") == "ACCEPTED")

    # --- archival gap notes ---------------------------------------------------
    if "A1b" not in json.dumps(results):
        warn("archive: A1b control verdict absent from iar_a_results.json",
             "re-verified here from stored A1b files; memo row only")
    memo_text = MEMO.read_text()
    check("archive: memo records A1b rejection row",
          "execution-session-binding" in memo_text and "A1b" in memo_text)

    # --- protected files ------------------------------------------------------
    for p, want in PROTECTED.items():
        got = sha256(p)
        check(f"protected unchanged: {p.name}", got == want, f"sha256={got[:16]}")

    # --- report ---------------------------------------------------------------
    fails = [c for c in CHECKS if c[0] == "FAIL"]
    warns = [c for c in CHECKS if c[0] == "WARN"]
    width = max(len(c[1]) for c in CHECKS)
    for status, name, detail in CHECKS:
        line = f"{status:4} {name:<{width}} {detail}"
        print(line.rstrip())
    print()
    print(f"TOTAL {len(CHECKS)} checks | PASS {len(CHECKS) - len(fails) - len(warns)} | "
          f"WARN {len(warns)} | FAIL {len(fails)}")
    report = {
        "verifier": str(Path(__file__).resolve()),
        "component_sha256": {"validator": val_sha, "reference": ref_sha, "results": res_sha},
        "checks": CHECKS,
        "fails": len(fails),
        "warns": len(warns),
    }
    (TMP / "verify_report.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"report: {TMP / 'verify_report.json'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
