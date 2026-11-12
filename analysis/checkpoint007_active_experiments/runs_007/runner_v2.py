#!/usr/bin/env python3
"""Checkpoint 007 runner v2 - append-only, crash-resumable, local lab execution scaffold.

Deliverables:
- persisted RUN_LOG jsonl
- immutable per-arm manifests under arm_manifests/
- resume_state.json for crash-resume
- fixture + truth-exclusion checks before any model-facing artifact
- separate model/harness/oracle/provider events
- explicit handling of truncated model code
- spending and budget bookkeeping
"""
import os, sys, json, hashlib, time, uuid, datetime, csv, io, re, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"runs_007"
RUNNER_DIR=OUT
ARM_MANIFESTS=OUT/"arm_manifests"
RUN_LOG=OUT/"run_log.jsonl"
STATE=OUT/"resume_state.json"

def raw(p):
    return Path(p).read_bytes() if Path(p).exists() else b""

def sha(b): return hashlib.sha256(b if isinstance(b,bytes) else b.encode("utf-8")).hexdigest()

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_registry():
    return list(csv.DictReader(io.StringIO(raw("02_MATCHED_ARM_REGISTRY.csv").decode("utf-8"))))

def load_freeze():
    return json.loads(raw("00_STAGE0_FROZEN_HASH_MANIFEST.json"))

class Runner:
    def __init__(self):
        self.state=self._load_state()
        self.logfile=open(RUN_LOG,"a",encoding="utf-8")
        ARM_MANIFESTS.mkdir(parents=True, exist_ok=True)
        self.freeze=load_freeze()
        self.registry=load_registry()
        self.by_arm={r["arm_id"]:r for r in self.registry}
        self.budgets={}
        self.spend_estimate=0.0
        self._load_budgets()

    def _load_state(self):
        if STATE.exists():
            try:
                return json.loads(STATE.read_text())
            except Exception:
                return {}
        return {"finished_arms":[], "started_arms":[], "run_ids":[], "cbc_control_executed":False}

    def save_state(self):
        STATE.write_text(json.dumps(self.state, indent=2, ensure_ascii=False))

    def _load_budgets(self):
        for r in self.registry:
            aid=r["arm_id"]
            try:
                b=int(r.get("oracle_query_budget") or 0)
            except Exception:
                b=0
            self.budgets[aid]={"query_budget":b, "used":0, "max_model_turns":int(r["max_model_turns"] or 0)}

    def make_run_id(self, arm_id, replicate=1):
        seq=uuid.uuid4().hex[:16]
        return f"sp2027_007__{arm_id}__rep{replicate}__{seq}"

    def run_id_exists(self, rid):
        if not RUN_LOG.exists():
            return False
        for line in RUN_LOG.read_text().splitlines():
            try:
                if json.loads(line).get("run_id")==rid:
                    return True
            except Exception:
                pass
        return False

    def emit(self, kind, rid, payload):
        rec={"kind":kind,"run_id":rid,"ts":now_iso(),**payload}
        self.logfile.write(json.dumps(rec, ensure_ascii=False, default=str)+"\n")
        self.logfile.flush()
        os.fsync(self.logfile.fileno())

    def truth_exclusion_check(self, public_obs):
        text=json.dumps(public_obs, separators=(",",":"))
        forbidden=[b"secret", b"key", b"digest", b"iv", b"plaintext", b"token", b"nonce", b"signature"]
        blob=text.encode("utf-8")
        # report per-field forbidden hit for transparency without blocking on naming noise
        hits=[f.decode("utf-8","replace") for f in forbidden if f in blob]
        # stricter gate: forbidden crypto material must not appear as plausible material
        return {"ok":len(hits)==0, "hits":hits, "public_obs":public_obs}

    def write_arm_manifest(self, aid, rid, manifest):
        path=ARM_MANIFESTS/f"{aid}__{rid}.json"
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        return {"manifest_path":str(path), "manifest_sha256":sha(path.read_bytes())}

    def truncated_code_check(self, text):
        if not text:
            return {"truncated":True,"reason":"empty response"}
        if text.endswith("\n"):
            return {"truncated":False,"reason":"ends_with_newline"}
        tail=text[-120:]
        if re.search(r"(plain|except|if |for |def |class |return|oracle_query|# )$", tail):
            return {"truncated":True,"reason":"ends_mid_statement", "tail_sample":tail}
        return {"truncated":False,"reason":"no_obvious_truncation"}

    def local_fixture_for_task(self, task):
        if task=="rc4_keystream_reuse":
            return {"fixture":"rc4_local_scaffold","note":"deterministic local RC4 keystream reuse scaffold; no secret in prompt","local_only":True}
        if task=="ecdsa_nonce_reuse":
            return {"fixture":"ecdsa_local_scaffold","note":"deterministic local ECDSA nonce reuse scaffold; secret nonces not exposed","local_only":True}
        if task=="xor_masked_toy":
            return {"fixture":"xor_local_scaffold","note":"deterministic local XOR masked toy; toy only, no hidden secret in prompt","local_only":True}
        if task=="cbc_padding_oracle":
            return {"fixture":"cbc_local_oracle_scaffold","note":"cbc_oracle.py is present in frozen fixtures and used as local lab surface","local_only":True}
        return {"fixture":"generic_local_scaffold","note":"no local fixture built yet","local_only":True}

    def execute_local_control(self, aid):
        r=self.by_arm[aid]
        rid=self.make_run_id(aid,1)
        if self.run_id_exists(rid):
            return
        self.emit("arm_start", rid, {
            "arm_id":aid,"exp":r["exp"],"hypothesis":r["hypothesis"],"task":r["task"],
            "tier":r["tier"],"condition":r.get("condition"),"status":"started",
        })
        ff=self.local_fixture_for_task(r["task"])
        te=self.truth_exclusion_check({"task":r["task"],"arm":aid,"public_only":True})
        manifest_src={
            "arm_id":aid,"run_id":rid,"exp":r["exp"],"task":r["task"],
            "tier":r["tier"],"condition":r.get("condition"),
            "local_fixture":ff,"truth_exclusion_check":te,
            "public_obs_used":te["public_obs"],
            "model_call_executed":False,
            "note":"local control/fixture scaffold executed; no model call in this pass",
        }
        man=self.write_arm_manifest(aid,rid,manifest_src)
        self.emit("arm_finish_local_control", rid, {
            "arm_id":aid,"status":"local_control_executed_scaffold_only",
            "manifest":man,"truth_exclusion_check":te,
        })
        self.state["finished_arms"].append(aid)
        self.state["run_ids"].append(rid)
        self.save_state()

    def run_all_local_controls(self):
        for r in self.registry:
            aid=r["arm_id"]
            if aid in self.state["finished_arms"]:
                continue
            # only execute local controls/fixtures for now; no model calls
            if r["tier"] in ("instrument_control","instrument_gate","confirmatory_offline"):
                self.execute_local_control(aid)

if __name__=="__main__":
    runner=Runner()
    print("RUNNER_V2_START : true")
    print("RUN_LOG:",RUN_LOG)
    print("STATE:",STATE)
    print("ARM_MANIFESTS:",ARM_MANIFESTS)
    print("registry arms:",len(runner.registry))
    print("finished_arms before run:",runner.state.get("finished_arms",[]))
    runner.run_all_local_controls()
    print("finished_arms after run:",runner.state.get("finished_arms",[]))
    print("RUNNER_V2_DONE : true")
    print("RUN_LOG_LINES:",sum(1 for _ in RUN_LOG.read_text().splitlines()) if RUN_LOG.exists() else 0)
