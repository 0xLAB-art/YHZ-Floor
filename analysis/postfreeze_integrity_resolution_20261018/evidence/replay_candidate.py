#!/usr/bin/env python3
"""Replay harness for the surrogate_conversion_20261017_attempt3 CBC run.

Part A: recorded agent transcript -> claim hash vs run_result.candidate_sha256.
Part B: recorded oracle transcript -> query->reply map + sequence equality with agent transcript.
Part C: exact replay of the RECONSTRUCTED executed candidate (sha a5e8ed51...) against the
        recorded replies -> full query-sequence equality + claim-hash equality.
Part D: divergence test of the ARCHIVED generated_agent.py (sha 4fbd70a0...) against the
        recorded query stream (truth is only known for recorded queries; stops at first unknown).
Part E: live re-grade of BOTH programs against a fresh oracle instance (fresh secrets).
Writes /tmp/opencode/replay_results.json. Never modifies any archived file.
"""
import hashlib
import json
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ATT = Path("/mnt/nvme5/ACTS-Attack/sp2027/paper/capability_merge_20261016/artifact_documentation/novelty_program_20261017/surrogate_conversion_20261017_attempt3")
RECON = Path("/tmp/opencode/executed_candidate_reconstructed.py")
ARCHIVED = ATT / "surrogate/generated_agent.py"
INSTANCE = ATT / "surrogate/public_instance_actual.json"
TARGET_CLAIM_SHA = "919ca521b79129d066ceac25ffb6d793d379b8e0e0a631da6a722d77250ce8ef"
EXECUTED_SHA = "a5e8ed514c5c769b3e4e2dbbdd51ea276c852d11d8145b2f344ca7184f78e399"
ARCHIVED_SHA = "4fbd70a05ded111825fd4dedd64dc98155815839c65f35a91a19092a14c472b0"


class Timeout(Exception):
    pass


def _alarm(sig, frm):
    raise Timeout()


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def claim_sha(claim):
    return hashlib.sha256(json.dumps(claim, sort_keys=True).encode()).hexdigest()


out = {}

# ---- sanity + hashes
out["hashes"] = {"reconstructed_file": sha_file(RECON), "archived_file": sha_file(ARCHIVED)}
print("reconstructed sha:", out["hashes"]["reconstructed_file"], "expect", EXECUTED_SHA)
print("archived      sha:", out["hashes"]["archived_file"], "expect", ARCHIVED_SHA)

# ---- Part A: agent transcript
qseq_agent, claim_agent = [], None
for line in open(ATT / "transcripts/surrogate_agent.jsonl"):
    o = json.loads(line)
    l = o["line"]
    if l.startswith("{"):
        try:
            q = json.loads(l)
        except Exception:
            continue
        if isinstance(q, dict) and "q" in q:
            qseq_agent.append(q["q"])
            continue
    if l.startswith("CLAIM:"):
        claim_agent = json.loads(l[6:])
sha_a = claim_sha(claim_agent)
out["A"] = {
    "n_queries": len(qseq_agent),
    "claim": claim_agent,
    "claim_sha": sha_a,
    "claim_sha_matches_run_result": sha_a == TARGET_CLAIM_SHA,
    "plaintext_hex_len": len(claim_agent["plaintext_hex"]) if claim_agent else None,
}
print(f"A: agent queries={len(qseq_agent)} claim_sha={sha_a} match={sha_a == TARGET_CLAIM_SHA}")

# ---- Part B: oracle transcript map
qseq_oracle, qmap, dups, contradictions = [], {}, 0, 0
pending = None
for line in open(ATT / "transcripts/surrogate_oracle.jsonl"):
    o = json.loads(line)
    d, obj = o["dir"], o["object"]
    if d == "to_oracle" and obj.get("type") == "query":
        pending = obj["ct_b64"]
    elif d == "from_oracle" and obj.get("type") == "query_ack" and pending is not None:
        qseq_oracle.append(pending)
        if pending in qmap:
            dups += 1
            if qmap[pending] != obj.get("pad_ok"):
                contradictions += 1
        else:
            qmap[pending] = obj.get("pad_ok")
        pending = None
out["B"] = {
    "n_queries": len(qseq_oracle),
    "same_sequence_as_agent": qseq_oracle == qseq_agent,
    "unique_queries": len(qmap),
    "duplicate_queries": dups,
    "contradictions": contradictions,
}
print(f"B: oracle queries={len(qseq_oracle)} same_seq={qseq_oracle == qseq_agent} uniq={len(qmap)} dups={dups} contradictions={contradictions}")


# ---- replay against recorded map
def run_with_map(prog, limit_seconds=300):
    result = {
        "prog": str(prog),
        "n_queries": 0,
        "first_divergence_index": None,
        "first_divergence_detail": None,
        "claim": None,
        "claim_sha": None,
        "terminated": None,
    }
    proc = subprocess.Popen(
        [sys.executable, str(prog), str(INSTANCE)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(limit_seconds)
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                result["terminated"] = "eof"
                break
            line = line.rstrip("\n")
            if line.startswith("{"):
                try:
                    q = json.loads(line)
                except Exception:
                    continue
                if isinstance(q, dict) and "q" in q:
                    i = result["n_queries"]
                    ct = q["q"]
                    if i < len(qseq_agent) and ct == qseq_agent[i]:
                        proc.stdin.write(json.dumps({"pad_ok": qmap[ct]}) + "\n")
                        proc.stdin.flush()
                        result["n_queries"] += 1
                        continue
                    result["first_divergence_index"] = i
                    result["first_divergence_detail"] = {
                        "emitted": ct,
                        "recorded": qseq_agent[i] if i < len(qseq_agent) else None,
                    }
                    break
            elif line.startswith("CLAIM:"):
                result["claim"] = json.loads(line[6:])
                result["claim_sha"] = claim_sha(result["claim"])
                result["terminated"] = "claim"
                break
    except Timeout:
        result["terminated"] = "timeout"
    finally:
        signal.alarm(0)
        try:
            proc.kill()
        except Exception:
            pass
        try:
            proc.wait(timeout=5)
        except Exception:
            pass
    result["full_match"] = bool(
        result["first_divergence_index"] is None
        and result["n_queries"] == len(qseq_agent)
        and result["claim_sha"] == TARGET_CLAIM_SHA
    )
    return result


out["C"] = run_with_map(RECON)
print(f"C: reconstructed replay -> queries={out['C']['n_queries']} divergence={out['C']['first_divergence_index']} claim_sha={out['C']['claim_sha']} full_match={out['C']['full_match']}")

out["D"] = run_with_map(ARCHIVED)
print(f"D: archived replay      -> queries={out['D']['n_queries']} divergence={out['D']['first_divergence_index']} claim_sha={out['D']['claim_sha']} terminated={out['D']['terminated']}")


# ---- Part E: live fresh-secret grading
def run_live(prog, port, rep, limit_seconds=600):
    oracle = subprocess.Popen(
        [sys.executable, str(ATT / "oracle/oracle.py"), str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(0.6)
    s = socket.create_connection(("127.0.0.1", port))
    f = s.makefile("rwb")

    def send(x):
        f.write((json.dumps(x) + "\n").encode())
        f.flush()

    def recv():
        return json.loads(f.readline().decode())

    send({"type": "hello", "condition": "CBC_Padding_Oracle", "rep": rep})
    recv()
    prov = recv()["material"]
    inst = Path(f"/tmp/opencode/live_instance_rep{rep}.json")
    inst.write_text(json.dumps({"ct_hex": prov["ct_hex"], "iv_hex": prov["iv_hex"]}) + "\n")
    send({"type": "op_start"})
    recv()
    proc = subprocess.Popen(
        [sys.executable, str(prog), str(inst)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    n = 0
    claim = None
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(limit_seconds)
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.rstrip("\n")
            if line.startswith("{"):
                try:
                    q = json.loads(line)
                except Exception:
                    continue
                if isinstance(q, dict) and "q" in q:
                    send({"type": "query", "ct_b64": q["q"]})
                    ans = recv()
                    n += 1
                    proc.stdin.write(json.dumps({"pad_ok": ans.get("pad_ok", False)}) + "\n")
                    proc.stdin.flush()
                    continue
            if line.startswith("CLAIM:"):
                claim = json.loads(line[6:])
                break
    except Timeout:
        pass
    finally:
        signal.alarm(0)
    if claim is not None:
        send({"type": "claim", "claim": claim})
        verdict = recv()
    else:
        verdict = {"verdict": "no_candidate"}
    send({"type": "abort", "reason": "replay_probe"})
    try:
        recv()
    except Exception:
        pass
    f.close()
    s.close()
    try:
        proc.kill()
    except Exception:
        pass
    oracle.terminate()
    try:
        oracle.wait(timeout=5)
    except Exception:
        pass
    return {
        "prog": str(prog),
        "rep": rep,
        "n_queries": n,
        "claim_sha": claim_sha(claim) if claim else None,
        "verdict": verdict,
    }


out["E_reconstructed_live"] = run_live(RECON, 17851, 901)
print("E1: reconstructed live  ->", json.dumps(out["E_reconstructed_live"], default=str)[:400])
out["E_archived_live"] = run_live(ARCHIVED, 17852, 902)
print("E2: archived live       ->", json.dumps(out["E_archived_live"], default=str)[:400])

Path("/tmp/opencode/replay_results.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
print("\nwritten /tmp/opencode/replay_results.json")
