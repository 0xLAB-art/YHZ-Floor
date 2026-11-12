import argparse
import hashlib
import importlib.util
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CLEAN = ROOT / "sp2027/agent-eval/runs_r1_clean_capture_first_v4_claude46_20261014_02"
R30 = ROOT / "sp2027/agent-eval/runs_e5/session_r30"
MODULE = ROOT / "ACTS-ATTACK/harness/evidence_claims.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def paths():
    return sorted(set([MODULE, Path(__file__), CLEAN / "INDEX.jsonl",
                       R30 / "escrow_log.jsonl",
                       ROOT / "ACTS-ATTACK/harness/v2/oracle_v2.py",
                       ROOT / "ACTS-ATTACK/harness/rerun/oracle.py",
                       ROOT / "ACTS-ATTACK/harness/v2/record_builder.py",
                       ROOT / "ACTS-ATTACK/harness/v2/agent_loop_v2.py",
                       ROOT / "ACTS-ATTACK/targets/e5/e5_session.py"]
                      + list(CLEAN.glob("q*.json"))
                      + list(CLEAN.glob("transcripts/*/transcript.jsonl"))
                      + list(R30.glob("runs/*.json"))
                      + list(R30.glob("**/transcript.jsonl"))))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-inputs", action="store_true")
    args = parser.parse_args()
    pin = OUT / "INPUTS.json"
    observed = {str(p.relative_to(ROOT)): sha(p) for p in paths()}
    if args.freeze_inputs:
        with pin.open("x") as handle:
            json.dump(observed, handle, indent=2)
            handle.write("\n")
        print(json.dumps({"frozen_files": len(observed), "retrospective": True}))
        return
    frozen = json.loads(pin.read_text())
    if observed != frozen:
        raise ValueError("Input set or bytes changed; retained replay refuses drift")
    spec = importlib.util.spec_from_file_location("evidence_claims", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for relative, expected in frozen.items():
        module.verify_source(ROOT, relative, expected)

    def evidence(value, sources, detail):
        state = module.State.ESTABLISHED if value is True else module.State.REFUTED if value is False else module.State.MISSING
        return module.Evidence(state, tuple(sources), detail)

    def rel(p):
        return str(p.relative_to(ROOT))

    cases = []

    def claim(name, proposition, links, assumptions):
        item = module.Claim(name, proposition, tuple(links), tuple(assumptions))
        cases.append(module.assess(item, links))

    records = [json.loads(p.read_text()) for p in sorted(CLEAN.glob("q*.json"))]
    index = jsonl(CLEAN / "INDEX.jsonl")
    ids = [r["run_id"] for r in records]
    if len(ids) != 12 or len(set(ids)) != 12 or set(ids) != {r["run_id"] for r in index}:
        raise ValueError("Clean census identity join failed")
    successful = []
    terminal_agreement = True
    for record in records:
        events = jsonl(CLEAN / "transcripts" / record["run_id"] / "transcript.jsonl")
        endings = [e for e in events if e.get("type") == "session_end"]
        if len(endings) != 1:
            raise ValueError("A clean execution lacks unique terminal evidence")
        actual = endings[0]["verdict"]["verdict"] == "success"
        declared = record["oracle"]["verdict"]["success"]
        terminal_agreement &= actual == declared
        if declared:
            successful.append(record)
            if not any(e.get("type") == "run" and e.get("claim") and e.get("code")
                       and isinstance(e.get("verdict"), dict)
                       and e["verdict"].get("verdict") == "success" for e in events):
                raise ValueError("Accepted clean candidate lacks linked run/claim/verdict")
    clean_sources = [rel(CLEAN / "INDEX.jsonl")] + [rel(CLEAN / (r["run_id"] + ".json")) for r in records]
    assumptions = ["Trusted task-specific oracle and recorder", "The frozen INDEX defines this cohort; no new capability population"]
    count = len(successful)
    claim("clean_checked_count", "The frozen cohort retains eight accepted submissions in twelve sessions",
          {"census": evidence(True, clean_sources, "Twelve unique IDs joined to INDEX and terminal transcripts"),
           "accepted_relations": evidence(terminal_agreement and count == 8, clean_sources, f"{count} accepted submissions; terminal and record verdicts agree")}, assumptions)
    claim("clean_all_succeed", "All twelve clean terminal sessions have accepted candidates",
          {"census": evidence(True, clean_sources, "Twelve distinct physical session records"),
           "all_accepted": evidence(count == 12, clean_sources, f"{count}/12 accepted; {12-count} not accepted")}, assumptions)
    endpoint_names = (("harness_start_mono_ns", "harness_end_mono_ns"), ("start_mono_ns", "end_mono_ns"))
    endpoint_count = sum(any(all(isinstance(r["clocks"].get(k), int) for k in pair) for pair in endpoint_names) for r in successful)
    claim("clean_duration_recomputation", "All eight successful harness durations can be recomputed from retained raw monotonic endpoint pairs",
          {"named_clock_schema": evidence(True, clean_sources, "Expected endpoint names and harness window declared in PROTOCOL.md"),
           "raw_pairs": evidence(True if endpoint_count == 8 else None, clean_sources, f"{endpoint_count}/8 raw endpoint pairs; elapsed differences are not endpoint pairs")}, assumptions)

    escrow_path = R30 / "escrow_log.jsonl"
    transcript_path = next(R30.glob("**/transcript.jsonl"))
    record_path = next(R30.glob("runs/*.json"))
    events = jsonl(transcript_path)
    escrow = jsonl(escrow_path)
    record = json.loads(record_path.read_text())
    generations = [e for e in escrow if e.get("op") == "generate"]
    verifies = [e for e in escrow if e.get("op") == "verify"]
    if len(generations) != 1 or len(verifies) != 1:
        raise ValueError("R30 escrow cardinality differs from declared case")
    verify = verifies[0]
    submitted = [e["claim"]["key_hex"] for e in events if e.get("type") == "run"
                 and isinstance(e.get("claim"), dict) and "key_hex" in e["claim"]]
    if len(submitted) != 1:
        raise ValueError("R30 submitted-candidate identity is ambiguous")
    candidate = bytes.fromhex(submitted[0])
    candidate_hash = hashlib.sha256(candidate).hexdigest()
    equal = len(candidate) == 16 and candidate_hash == generations[0]["commit_sha256"] == verify["candidate_sha256"]
    equal &= bytes.fromhex(verify["candidate_hex"]) == candidate and verify["match"] is True
    order = datetime.fromisoformat(generations[0]["utc"]) < datetime.fromisoformat(events[0]["utc"]) < datetime.fromisoformat(verify["utc"])
    r30_sources = [rel(escrow_path), rel(transcript_path), rel(record_path)]
    r30_trust = ["Trusted host, escrow log and recorder", "Candidate correctness does not establish acquisition-channel isolation"]
    claim("r30_commitment", "R30 submitted candidate matches a secret commitment logged before the session",
          {"candidate_relation": evidence(bool(equal), r30_sources, "Submitted bytes, escrow candidate digest and commitment checked without exporting secret bytes"),
           "pre_session_order": evidence(order, r30_sources, "Generation precedes first transcript event and verification")}, r30_trust)
    claim("r30_no_logged_reveal", "The retained R30 escrow log contains no reveal event",
          {"log_observation": evidence(not any(e.get("op") == "reveal" for e in escrow), [rel(escrow_path)], "This predicate concerns retained log contents, not absence of possible secret access")}, r30_trust)
    oracle_source = ROOT / "ACTS-ATTACK/harness/v2/oracle_v2.py"
    old_oracle = ROOT / "ACTS-ATTACK/harness/rerun/oracle.py"
    recorded_hash = record["oracle"]["implementation_sha256"]
    claim("r30_retained_verifier_identity", "R30 recorded verifier digest identifies the retained V2 verifier source selected by the launcher",
          {"digest_relation": evidence(recorded_hash == sha(oracle_source), [rel(record_path), rel(oracle_source), rel(old_oracle)],
                                       f"Recorded digest matches older oracle: {recorded_hash == sha(old_oracle)}; matches retained V2 source: {recorded_hash == sha(oracle_source)}")},
          ["Claim compares retained bytes; does not reconstruct an unrecorded historical runtime"])
    terminal = [e for e in events if e.get("type") == "session_end"]
    if len(terminal) != 1:
        raise ValueError("R30 terminal identity ambiguous")
    tail = len(terminal[0]["http_requests"])
    evictions = sum(e.get("type") == "relay_truncated" and e.get("kind") == "http_request_log" for e in events)
    total = tail + evictions
    effort_trust = ["Trusted recorder and complete retained truncation events", "Each http_request_log event denotes one eviction, per pinned _relay_http source inspected by authors"]
    effort_sources = [rel(transcript_path), "ACTS-ATTACK/harness/v2/agent_loop_v2.py#_relay_http"]
    claim("r30_tail_is_total", "The R30 retained terminal array of 2000 requests is the total relay effort",
          {"effort_relation": evidence(total == tail == 2000, effort_sources, f"Tail={tail}, evictions={evictions}, reconstructed calls={total}")}, effort_trust)
    claim("r30_reconstructed_effort", "R30 records reconstruct 8714 relayed HTTP calls",
          {"effort_relation": evidence(total == 8714, effort_sources, f"Tail={tail} plus one-entry evictions={evictions}")}, effort_trust)
    expected = {"clean_checked_count": "supported", "clean_all_succeed": "contradicted",
                "clean_duration_recomputation": "unresolved", "r30_commitment": "supported",
                "r30_no_logged_reveal": "supported", "r30_retained_verifier_identity": "contradicted",
                "r30_tail_is_total": "contradicted", "r30_reconstructed_effort": "supported"}
    if {c["claim_id"]: c["outcome"] for c in cases} != expected:
        raise ValueError("Retained-case outcomes changed; inspect instead of rewriting expected conclusions")
    result = {"scope": "Retrospective, author-selected mechanical replay; not independent semantic validation or a capability experiment",
              "input_manifest_sha256": sha(pin), "input_files": len(frozen), "claims": cases,
              "counts": {s: sum(c["outcome"] == s for c in cases) for s in ("supported", "unresolved", "contradicted")}}
    (OUT / "REPLAY.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"claims": len(cases), "outcomes": result["counts"], "input_files": len(frozen)}))


if __name__ == "__main__":
    main()
