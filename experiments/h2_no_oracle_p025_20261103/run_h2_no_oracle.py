#!/usr/bin/env python3
"""H2-CBC-NOORACLE-20261103-v1 — matched oracle-separation arm.

One-shot arm (one turn, no feedback), same seeds and fixture as the 2026-10-24
extension cohort, same frozen prompt/policy/predicate/execution. The **only**
manipulated factor is the oracle's information content: `oracle.query` keeps
its interface and its 4096-call budget but always returns False, and counts
every call.

Everything else is imported from the frozen runner rather than reimplemented:
`build_prompt`, `extract_action`, `policy_check`, `verdict`,
`classify_rejection`, `run_program`, `ProviderClient`, `instance`. The frozen
file is not modified; only its module-level output paths are redirected here.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXT = HERE.parent / "h2_pairs_extension_20261024"
PROTOCOL = "H2-CBC-NOORACLE-20261103-v1"
EXTENDS = "H2-CBC-PAIRS-EXT-20261024-v1"
SEEDS = (65, 66, 67, 68, 69, 70, 71, 72, 73, 74)
ARM = "C_NO_ORACLE"
SESS = HERE / "sessions"
LEDGER = HERE.parent / "BUDGET_LEDGER.jsonl"

# Amendment A1: the registered route returned HTTP 404 for every seed, so the
# arm runs on the operator-supplied AgentRouter gateway with a substituted
# model. See AMENDMENT.md; the deviation is disclosed, not absorbed.
ROUTE = os.environ.get("ARM_ROUTE", "agentrouter")
EXT_MOD = None  # set by load_extension(); source of the frozen ProviderFailure
TOKEN_FLOOR = 4200  # gateway rejects sub-floor clients with 401
CLI_UA = "claude-cli/2.0.0 (external, cli)"

# ---- black-hole oracle: same interface, same budget, no information ----
BLACKHOLE_ORACLE = '''"""Padding oracle: interface present, information absent (arm C_NO_ORACLE).

query() always returns False. Calls are counted in oracle_usage.json so the
harness can tell "never tried the channel" from "tried and learned nothing".
"""
import json
import os

BUDGET = 4096
_STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oracle_usage.json")
_ENABLED = False


def _load():
    try:
        with open(_STATE) as fh:
            data = json.load(fh)
    except Exception:
        data = {}
    data.setdefault("queries", 0)
    return data


def _save(data):
    data["enabled"] = _ENABLED
    with open(_STATE, "w") as fh:
        json.dump(data, fh, sort_keys=True)


def query(candidate_block_hex):
    if not isinstance(candidate_block_hex, str):
        raise TypeError("candidate_block_hex must be a hex string")
    data = _load()
    if data["queries"] >= BUDGET:
        raise RuntimeError("oracle query budget exhausted")
    data["queries"] += 1
    _save(data)
    return False
'''


def load_extension():
    spec = importlib.util.spec_from_file_location(
        "h2_ext_frozen", EXT / "run_h2_pairs_extension.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    # Redirect every output path; the frozen session tree is never touched.
    mod.SESS = SESS
    mod.LEDGER = LEDGER
    mod.PROTOCOL = PROTOCOL
    global EXT_MOD
    EXT_MOD = mod
    return mod


class AgentRouterClient:
    """Anthropic-shaped /v1/messages client for the A1 fallback route.

    Same return contract as the frozen ``ProviderClient``; raises the frozen
    ``ProviderFailure`` so the runner's handling is unchanged.
    """

    def __init__(self):
        env = {}
        for line in (HERE.parents[2] / ".env").read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
        self.endpoint = env.get("AGENTROUTER_BASE_URL", "").rstrip("/")
        self.model = env.get("AGENTROUTER_LABEL_MODEL", "") or "gpt-6.1-sol"
        self._key = env.get("AGENTROUTER_API_KEY", "")
        if not self.endpoint or not self._key:
            raise RuntimeError("AgentRouter route is not configured")

    def call(self, prompt, max_tokens, timeout=420):
        import requests

        started = time.time()
        sent_tokens = max(int(max_tokens), TOKEN_FLOOR)
        url = self.endpoint + "/v1/messages"
        payload = {"model": self.model, "max_tokens": sent_tokens,
                   "messages": [{"role": "user", "content": prompt}]}
        headers = {"x-api-key": self._key, "Authorization": "Bearer " + self._key,
                   "anthropic-version": "2023-06-01",
                   "content-type": "application/json", "User-Agent": CLI_UA}
        last = None
        response = None
        for attempt in (1, 2):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=timeout)
                break
            except requests.Timeout as exc:
                last = EXT_MOD.ProviderFailure("TIMEOUT", str(exc))
            except requests.RequestException as exc:
                last = EXT_MOD.ProviderFailure("PROVIDER_UNAVAILABLE", str(exc))
            if attempt == 2:
                raise last
        raw = response.content
        if response.status_code >= 400:
            excerpt = raw[:300].decode("utf-8", "replace").replace("\n", " ")
            raise EXT_MOD.ProviderFailure("PROVIDER_UNAVAILABLE",
                                    f"HTTP {response.status_code} {excerpt}", raw[:300])
        try:
            body = response.json()
        except ValueError as exc:
            raise EXT_MOD.ProviderFailure("PROVIDER_UNAVAILABLE",
                                    "provider response was not JSON", raw[:300]) from exc
        content = body.get("content") if isinstance(body, dict) else None
        text = "".join(x.get("text", "") for x in content or []
                       if isinstance(x, dict) and x.get("type") == "text")
        if not text:
            raise EXT_MOD.ProviderFailure("PROVIDER_UNAVAILABLE",
                                    "successful response contained no text", raw[:300])
        metadata = {"endpoint": url, "model_requested": self.model,
                    "max_tokens": max_tokens, "max_tokens_sent": sent_tokens,
                    "token_floor_applied": sent_tokens > int(max_tokens),
                    "user_agent": CLI_UA, "prompt_sha256": hashlib.sha256(
                        prompt.encode()).hexdigest(),
                    "request_started": started, "http_status": response.status_code,
                    "response_sha256": hashlib.sha256(raw).hexdigest(),
                    "response_bytes": len(raw), "response_finished": time.time(),
                    "provider_model": body.get("model"),
                    "finish_reason": body.get("stop_reason"),
                    "usage": body.get("usage", {}), "output_sha256": hashlib.sha256(
                        text.encode()).hexdigest()}
        if metadata["finish_reason"] in ("max_tokens", "length"):
            raise EXT_MOD.ProviderFailure("PROVIDER_UNAVAILABLE",
                                    "provider reported truncation", raw[:300])
        return {"metadata": metadata, "body": body,
                "raw_body": raw.decode("utf-8", "replace"), "text": text}



class ApinexClient:
    """OpenAI-compatible /v1/chat/completions client (amendment A2).

    Same return contract as the frozen ``ProviderClient``.
    """

    def __init__(self):
        env = {}
        for line in (HERE.parents[2] / ".env").read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip().strip('"').strip("'")
        self.endpoint = env.get("APINEX_BASE_URL", "").rstrip("/")
        self.model = env.get("APINEX_LABEL_MODEL", "") or "free/deepseek-v4.1-flash"
        self._key = env.get("APINEX_API_KEY", "")
        if not self.endpoint or not self._key:
            raise RuntimeError("APINEX route is not configured")

    def call(self, prompt, max_tokens, timeout=420):
        import requests

        started = time.time()
        url = self.endpoint + "/v1/chat/completions"
        payload = {"model": self.model, "max_tokens": int(max_tokens),
                   "messages": [{"role": "user", "content": prompt}]}
        headers = {"Authorization": "Bearer " + self._key,
                   "content-type": "application/json"}
        last = None
        response = None
        for attempt in (1, 2):
            try:
                response = requests.post(url, headers=headers, json=payload,
                                         timeout=timeout)
                break
            except requests.Timeout as exc:
                last = EXT_MOD.ProviderFailure("TIMEOUT", str(exc))
            except requests.RequestException as exc:
                last = EXT_MOD.ProviderFailure("PROVIDER_UNAVAILABLE", str(exc))
            if attempt == 2:
                raise last
        raw = response.content
        if response.status_code >= 400:
            excerpt = raw[:300].decode("utf-8", "replace").replace("\n", " ")
            raise EXT_MOD.ProviderFailure(
                "PROVIDER_UNAVAILABLE", f"HTTP {response.status_code} {excerpt}", raw[:300])
        try:
            body = response.json()
        except ValueError as exc:
            raise EXT_MOD.ProviderFailure(
                "PROVIDER_UNAVAILABLE", "provider response was not JSON", raw[:300]) from exc
        try:
            choice = body["choices"][0]
            text = choice["message"]["content"] or ""
            finish = choice.get("finish_reason")
        except (KeyError, IndexError, TypeError) as exc:
            raise EXT_MOD.ProviderFailure(
                "PROVIDER_UNAVAILABLE", "unexpected response shape", raw[:300]) from exc
        if not text:
            raise EXT_MOD.ProviderFailure(
                "PROVIDER_UNAVAILABLE", "successful response contained no text", raw[:300])
        usage = body.get("usage") or {}
        metadata = {"endpoint": url, "model_requested": self.model,
                    "max_tokens": int(max_tokens), "max_tokens_sent": int(max_tokens),
                    "token_floor_applied": False,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "request_started": started, "http_status": response.status_code,
                    "response_sha256": hashlib.sha256(raw).hexdigest(),
                    "response_bytes": len(raw), "response_finished": time.time(),
                    "provider_model": body.get("model"), "finish_reason": finish,
                    "usage": {"input_tokens": usage.get("prompt_tokens", 0),
                              "output_tokens": usage.get("completion_tokens", 0)},
                    "output_sha256": hashlib.sha256(text.encode()).hexdigest()}
        if finish in ("max_tokens", "length"):
            raise EXT_MOD.ProviderFailure(
                "PROVIDER_UNAVAILABLE", "provider reported truncation", raw[:300])
        return {"metadata": metadata, "body": body,
                "raw_body": raw.decode("utf-8", "replace"), "text": text}


def write_orphan_oracle(tdp, seed, d_target):
    """Signature-compatible replacement for fixture_cbc.generate_oracle_module."""
    (Path(tdp) / "oracle.py").write_text(BLACKHOLE_ORACLE)
    (Path(tdp) / "oracle_usage.json").write_text(
        json.dumps({"queries": 0, "enabled": False}, sort_keys=True))


def main():
    for sub in ("raw_provider_responses", "execution_captures", "prompts"):
        (SESS / sub).mkdir(parents=True, exist_ok=True)

    mod = load_extension()
    mod.generate_oracle_module = write_orphan_oracle  # only factor changed

    provider = (ApinexClient() if ROUTE == "apinex"
                else AgentRouterClient() if ROUTE == "agentrouter"
                else mod.ProviderClient())
    prompt_probe = mod.build_prompt(mod.instance(SEEDS[0])[0])
    freeze = {
        "protocol": PROTOCOL, "extends": EXTENDS, "arm": ARM,
        "seeds": list(SEEDS),
        "frozen_runner": str(EXT / "run_h2_pairs_extension.py"),
        "frozen_runner_sha256": hashlib.sha256(
            (EXT / "run_h2_pairs_extension.py").read_bytes()).hexdigest(),
        "preregistration_sha256": hashlib.sha256(
            (HERE / "PREREGISTRATION.md").read_bytes()).hexdigest(),
        "blackhole_oracle_sha256": hashlib.sha256(
            BLACKHOLE_ORACLE.encode()).hexdigest(),
        "prompt_template_sha256": mod.sha(mod.PROMPT_TEMPLATE),
        "seed65_prompt_sha256": mod.sha(prompt_probe),
        "model": provider.model, "endpoint": provider.endpoint, "route": ROUTE,
        "amendment": "A1 (route fallback + model substitution; see AMENDMENT.md)",
        "max_tokens": mod.MAX_TOKENS, "exec_timeout_s": mod.EXEC_TIMEOUT,
        "oracle_budget": mod.ORACLE_BUDGET, "oracle_information": "absent (always False)",
        "predicate": "exact match on plaintext hex (lowercased)",
        "frozen_at": time.time(),
    }
    (HERE / "FREEZE.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    (HERE / "run_info.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"frozen": freeze["frozen_runner_sha256"],
                      "prereg": freeze["preregistration_sha256"],
                      "model": provider.model}, sort_keys=True), flush=True)

    done = set()
    results_path = HERE / "results.jsonl"
    if results_path.is_file():
        for line in results_path.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["seed"])

    call_index = 0
    for seed in SEEDS:
        if seed in done:
            print(json.dumps({"skipped_already_recorded": seed}), flush=True)
            continue
        public, secret = mod.instance(seed)
        truth = secret["plaintext"]
        witnesses = {"full_padded_second_block_hex": secret["padded"][16:32].hex(),
                     "decrypted_first_block_hex": secret["d_c0"].hex(),
                     "prefix_hex_witness": secret["prefix"].hex()}
        run_id = f"{PROTOCOL}__{ARM}__seed_{seed}__{uuid.uuid4().hex[:12]}"
        mod.event(run_id, "arm_start", {"seed": seed, "arm": ARM, "protocol": PROTOCOL,
                                        "oracle_information": "absent"})
        session = {"run_id": run_id, "seed": seed, "arm": ARM, "protocol": PROTOCOL,
                   "turns": 0, "submissions": 0, "provider_failures": 0,
                   "status": "INCOMPLETE", "accepted": False, "final_timed_out": False,
                   "public_input_sha256": hashlib.sha256(
                       json.dumps(public, sort_keys=True).encode()).hexdigest(),
                   "turn_records": []}
        prompt = mod.build_prompt(public)
        (SESS / "prompts" / f"{run_id}__turn1.txt").write_text(prompt)
        mod.event(run_id, "model_start", {"seed": seed, "arm": ARM, "turn": 1,
                                          "prompt_sha256": mod.sha(prompt),
                                          "provider_route": provider.model})
        last_text = None
        try:
            result = provider.call(prompt, mod.MAX_TOKENS)
        except mod.ProviderFailure as exc:
            session["provider_failures"] += 1
            session["_provider_category"] = ("TIMEOUT" if exc.category == "TIMEOUT"
                                             else "PROVIDER_UNAVAILABLE")
            mod.event(run_id, "provider_failure", {"seed": seed, "arm": ARM, "turn": 1,
                                                   "category": exc.category,
                                                   "detail": str(exc)[:300]})
            session["status"] = session["_provider_category"]
            session.pop("_provider_category", None)
            with results_path.open("a") as fh:
                fh.write(json.dumps(session, sort_keys=True) + "\n")
            print(json.dumps({"seed": seed, "status": session["status"]}), flush=True)
            continue

        (SESS / "raw_provider_responses" / f"{run_id}__turn1.json").write_text(
            result["raw_body"])
        usage = result["metadata"]["usage"] or {}
        call_index += 1
        mod.ledger_append({
            "timestamp": time.strftime("%Y-%m-%d", time.gmtime()),
            "namespace": PROTOCOL, "classification": "experiment call",
            "protocol": PROTOCOL, "run_id": run_id, "arm": ARM, "seed": seed,
            "turn": 1, "call_index": call_index, "model": provider.model,
            "input_tokens": int(usage.get("input_tokens", 0)),
            "output_tokens": int(usage.get("output_tokens", 0)),
            "estimated_accounting_cost_usd": round(
                int(usage.get("input_tokens", 0)) * mod.RATE_INPUT_PER_MTOK / 1e6
                + int(usage.get("output_tokens", 0)) * mod.RATE_OUTPUT_PER_MTOK / 1e6, 9),
            "invoice_status": "not claimed; provider route reported free plan",
        })
        session["turns"] = 1
        last_text = result["text"]
        action = mod.extract_action(result["text"])
        if not action:
            session["turn_records"].append({"turn": 1, "stage": "parse",
                                            "error_class": "encoding", "queries": 0,
                                            "submitted": False})
            mod.event(run_id, "action_parse_failed", {"seed": seed, "arm": ARM, "turn": 1})
            session["status"] = mod.terminal_state(session, last_text)
            with results_path.open("a") as fh:
                fh.write(json.dumps(session, sort_keys=True) + "\n")
            print(json.dumps({"seed": seed, "status": session["status"],
                              "stage": "parse"}), flush=True)
            continue

        session["submissions"] = 1
        code = action["code"]
        allowed, policy = mod.policy_check(code)
        if not allowed:
            session["turn_records"].append({"turn": 1, "stage": "policy",
                                            "error_class": mod.classify_rejection(
                                                "policy", code, None, None, "", "", 0,
                                                truth, witnesses, policy_reason=policy),
                                            "queries": 0, "submitted": True,
                                            "policy_reason": policy})
            mod.event(run_id, "policy_rejected", {"seed": seed, "arm": ARM,
                                                  "policy_reason": policy})
            session["status"] = mod.terminal_state(session, last_text)
            with results_path.open("a") as fh:
                fh.write(json.dumps(session, sort_keys=True) + "\n")
            print(json.dumps({"seed": seed, "status": session["status"],
                              "policy": policy}), flush=True)
            continue

        facts = mod.run_program(code, seed, public, run_id, 1)
        candidate = None
        if facts["stage"] == "output" and facts["out"]:
            try:
                candidate = json.loads(facts["out"].splitlines()[-1])
            except (ValueError, IndexError):
                candidate = None
        accepted = (facts["stage"] == "output" and facts["proc_rc"] == 0
                    and mod.verdict(candidate, truth))
        session["turn_records"].append(
            {"turn": 1, "stage": facts["stage"], "submitted": True,
             "returncode": facts["proc_rc"], "queries": facts["queries"],
             "oracle_usage_present": facts["usage_present"],
             "accepted": accepted,
             "error_class": None if accepted else mod.classify_rejection(
                 facts["stage"], code, facts["proc_rc"], candidate, facts["out"],
                 facts["err"], facts["queries"], truth, witnesses),
             "candidate_digest": mod.sha(facts["out"]) if facts["out"] else None,
             "timed_out": facts["timed_out"]})
        mod.event(run_id, "execution_verdict",
                  {"seed": seed, "arm": ARM, "turn": 1,
                   "verdict": "accepted" if accepted else "rejected",
                   "queries": facts["queries"], "stage": facts["stage"]})
        if accepted:
            session["accepted"] = True
            session["oracle_verdict"] = "accepted"
            session["accepted_turn"] = 1
            session["accepted_queries"] = facts["queries"]
        session["final_timed_out"] = bool(facts["timed_out"])
        session["status"] = mod.terminal_state(session, last_text)
        with results_path.open("a") as fh:
            fh.write(json.dumps(session, sort_keys=True) + "\n")
        print(json.dumps({"seed": seed, "status": session["status"],
                          "queries": facts["queries"],
                          "stage": facts["stage"]}, sort_keys=True), flush=True)

    rows = [json.loads(line) for line in results_path.read_text().splitlines() if line.strip()]
    evaluable = [r for r in rows if r["status"] in ("SUCCESS", "ORACLE_FAIL", "AGENT_GIVEUP", "MODEL_REFUSAL")]
    summary = {
        "schema": "h2-no-oracle/1.0", "protocol": PROTOCOL, "arm": ARM,
        "seeds": list(SEEDS), "model": provider.model,
        "sessions": len(rows), "evaluable": len(evaluable),
        "accepted": sum(1 for r in rows if r.get("accepted")),
        "acceptance": f"{sum(1 for r in rows if r.get('accepted'))}/{len(rows)}",
        "oracle_attempts_total": sum((r.get("turn_records") or [{}])[0].get("queries", 0)
                                     or 0 for r in rows),
        "statuses": {s: sum(1 for r in rows if r["status"] == s)
                     for s in sorted({r["status"] for r in rows})},
        "error_classes": {},
        "note": ("Oracle interface present, information absent. Acceptance under "
                 "this arm cannot be attributed to the oracle channel."),
    }
    for r in rows:
        for rec in r.get("turn_records") or []:
            key = rec.get("error_class") or ("accepted" if rec.get("accepted") else "none")
            summary["error_classes"][key] = summary["error_classes"].get(key, 0) + 1
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
