#!/usr/bin/env python3
import csv
import hashlib
import json
import os
import tempfile
import time
import uuid
from pathlib import Path
from provider_adapter import ClaudeProvider, ProviderFailure

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
LOG = OUT / "events.jsonl"
STATE = OUT / "state.json"
REGISTRY = ROOT / "02_MATCHED_ARM_REGISTRY.csv"


def digest(data):
    return hashlib.sha256(data).hexdigest()


class DurableRunner:
    def __init__(self):
        OUT.mkdir(parents=True, exist_ok=True)
        self.registry = {r["arm_id"]: r for r in csv.DictReader(REGISTRY.open())}
        self.state = self._read_state()

    def _read_state(self):
        if not STATE.exists():
            return {"completed_run_ids": [], "completed_arms": [], "completed_combinations": [], "inflight": {}}
        state = json.loads(STATE.read_text())
        state.setdefault("completed_combinations", [])
        state.setdefault("inflight", {})
        return state

    def _save_state(self):
        fd, name = tempfile.mkstemp(prefix="state.", dir=OUT)
        try:
            with os.fdopen(fd, "w") as handle:
                json.dump(self.state, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(name, STATE)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def emit(self, run_id, kind, payload):
        record = {"run_id": run_id, "kind": kind, "time": time.time(), **payload}
        with LOG.open("ab") as handle:
            line = (json.dumps(record, sort_keys=True) + "\n").encode()
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

    def complete_local_control(self, arm_id, result):
        if arm_id in self.state["completed_arms"]:
            return {"status": "already_complete", "arm_id": arm_id}
        run_id = f"sp2027_009__{arm_id}__{uuid.uuid4().hex[:16]}"
        self.emit(run_id, "arm_start", {"arm_id": arm_id, "source_hash": digest(REGISTRY.read_bytes())})
        self.emit(run_id, "harness_result", {"arm_id": arm_id, "result": result})
        manifest = {"run_id": run_id, "arm_id": arm_id, "result": result,
                    "event_log_sha256": digest(LOG.read_bytes())}
        path = OUT / f"{arm_id}__{run_id}.json"
        path.write_text(json.dumps(manifest, indent=2) + "\n")
        self.emit(run_id, "arm_finish", {"arm_id": arm_id, "manifest": str(path),
                                          "manifest_sha256": digest(path.read_bytes())})
        self.state["completed_arms"].append(arm_id)
        self.state["completed_run_ids"].append(run_id)
        self._save_state()
        return {"status": "completed", "run_id": run_id, "manifest": str(path)}

    @staticmethod
    def combination_key(arm_id, matched_seed, protocol_version):
        return f"{arm_id}::{matched_seed}::{protocol_version}"

    def run_provider_combination(self, arm_id, matched_seed, protocol_version, prompt, max_tokens=1024,
                                 provider=None, allow_call=True):
        key = self.combination_key(arm_id, matched_seed, protocol_version)
        if key in self.state["completed_combinations"]:
            return {"status": "already_complete", "combination": key}
        if not allow_call:
            return {"status": "DRY_RUN_NOT_CALLED", "combination": key}
        provider = provider or ClaudeProvider()
        run_id = f"sp2027_009__{arm_id}__seed_{matched_seed}__{uuid.uuid4().hex[:16]}"
        self.state["inflight"][key] = {"run_id": run_id, "started": time.time()}
        self._save_state()
        self.emit(run_id, "model_start", {"arm_id": arm_id, "matched_seed": matched_seed,
                   "protocol_version": protocol_version, "provider_route": provider.model,
                   "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()})
        raw_dir = OUT / "raw_provider_responses"
        raw_dir.mkdir(exist_ok=True)
        try:
            result = provider.call(prompt, max_tokens=max_tokens)
            raw_path = raw_dir / f"{run_id}.json"
            raw_path.write_text(result["raw_body"] + "\n")
            self.emit(run_id, "model_response", {"arm_id": arm_id, "matched_seed": matched_seed,
                       "protocol_version": protocol_version, "provider_metadata": result["metadata"],
                       "raw_response_path": str(raw_path)})
            self.state["completed_combinations"].append(key)
            self.state["completed_run_ids"].append(run_id)
            self.state["inflight"].pop(key, None)
            self._save_state()
            return {"status": "model_response", "run_id": run_id, "combination": key,
                    "text": result["text"], "metadata": result["metadata"], "raw_response_path": str(raw_path)}
        except ProviderFailure as exc:
            payload = {"arm_id": arm_id, "matched_seed": matched_seed, "protocol_version": protocol_version,
                       "error_category": exc.category, "error": str(exc)}
            if exc.response is not None:
                raw_path = raw_dir / f"{run_id}.error.json"
                raw_path.write_bytes(exc.response.content)
                payload["raw_response_path"] = str(raw_path)
                payload["http_status"] = exc.response.status_code
            self.emit(run_id, "provider_failure", payload)
            self.state["inflight"].pop(key, None)
            self._save_state()
            return {"status": exc.category, "run_id": run_id, "combination": key, **payload}


if __name__ == "__main__":
    print("durable_runner_module_only")
