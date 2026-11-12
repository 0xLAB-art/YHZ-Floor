#!/usr/bin/env python3
"""Clone one damaged cohort into a fresh namespace, swap the transport, re-run it.

Usage: python3 rerun_ar_clone.py <original_namespace> [--dry] [--shards N]

The original namespace is never modified. The clone keeps the registered runner
bytes, fixture, seeds, cells, rotation, prompts, oracle and label; only the
provider transport changes, from a P017-era adapter (no retry, and in the P018–P021
generation one that emits `stream_options` without `stream`) to the P023 adapter
(no stream parameters, registered retry policy, backoff 2/5/12 s).

Three execution shapes, chosen by what the cohort shipped with:

1. a launcher that calls `parallelize_cohort.run` → run it as-is in the clone;
2. a launcher with a hard-coded adapter name and SHA (the P010 label series) → the
   two literals are rewritten to the P023 adapter and its hash, and the rewrite is
   recorded in `_REGISTRATION.json`;
3. a serial CLI runner (`run_modern_aead_cohort.py`, the P019/P020 generation) →
   split by seed across N concurrent shard directories and merge on completion.
   Shards are kept as evidence; the merge never rewrites a row.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ADAPTER_NAME = "provider_adapter_agentrouter_p023.py"
ADAPTER = ROOT / ADAPTER_NAME
_SPEC_FILE = ROOT / "RERUN_SPECS_20261103.json"
SPECS = json.loads(_SPEC_FILE.read_text())["cohorts"] if _SPEC_FILE.exists() else {}
CLI_RUNNER = "run_modern_aead_cohort.py"
DEFAULT_SHARDS = 8  # 2026-11-03: 6 -> 8 after the fresh-quota rerun measured ~40 sessions/h at 6 shards (P021AR sustained 8 workers)
SUBS = ("raw_provider_responses", "prompts", "execution_captures")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pick_registration(d):
    for f in ("_REGISTRATION.json", "FREEZE.json"):
        p = d / f
        if p.exists():
            return f, json.loads(p.read_text())
    # launch-record fallback (P011/P010L5R generation kept only run_info.json);
    # the per-cohort spec supplies label/floor/adapter/runner/seeds
    p = d / "run_info.json"
    if p.exists():
        return "run_info.json", json.loads(p.read_text())
    return None, None


def patch_launcher(src: Path, dst: Path, adapter_sha: str):
    """Swap a hard-coded P017-era adapter reference for the P023 adapter."""
    text = src.read_text()
    changed = []
    if "provider_adapter_agentrouter.py" in text:
        text = text.replace('"provider_adapter_agentrouter.py"',
                            f'"{ADAPTER_NAME}"').replace(
            "provider_adapter_agentrouter.py", ADAPTER_NAME)
        changed.append("adapter_name")
    # replace the SHA literal that sat next to the old adapter name
    old = ROOT / "provider_adapter_agentrouter.py"
    if old.exists():
        old_sha = sha(old)
        if old_sha in text:
            text = text.replace(old_sha, adapter_sha)
            changed.append("adapter_sha")
    dst.write_text(text)
    return changed


def merge_shards(ns: Path, shard_dirs, protocol, reg=None):
    rows, failures = [], 0
    per_cell = {}
    turns = subs = 0
    with (ns / "results.jsonl").open("w") as out:
        for d in shard_dirs:
            rp = d / "results.jsonl"
            if not rp.exists():
                continue
            for line in rp.read_text().splitlines():
                if not line.strip():
                    continue
                out.write(line + "\n")
                r = json.loads(line)
                rows.append(r)
                failures += int(r.get("provider_failures", 0) or 0)
                turns += int(r.get("turns", 0) or 0)
                subs += int(r.get("submissions", 0) or 0)
                c = per_cell.setdefault(r["cell"], {"sessions": 0, "accepted": 0,
                                                    "submissions": 0, "turns": 0})
                c["sessions"] += 1
                c["submissions"] += int(r.get("submissions", 0) or 0)
                c["turns"] += int(r.get("turns", 0) or 0)
                if r.get("status") == "SUCCESS":
                    c["accepted"] += 1
        for name in ("events.jsonl", "failure_log.jsonl"):
            with (ns / name).open("w") as out:
                for d in shard_dirs:
                    p = d / name
                    if p.exists():
                        out.write(p.read_text())
    summary = {
        "confirmatory": False,
        "fixture": (reg or {}).get("fixture"),
        "per_cell": {c: per_cell[c] for c in sorted(per_cell)},
        "preregistered": True,
        "protocol": protocol,
        "provider_failures": failures,
        "provider_responses": turns,
        "sessions": len(rows),
        "finished": time.time(),
        "sharded": len(shard_dirs),
        "merge_note": "concatenated from shard results.jsonl; no row rewritten",
    }
    (ns / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def run_sharded(ns, reg_file, reg, label, shards):
    seeds = [int(v) for v in reg["seeds"]]
    buckets = [seeds[i::shards] for i in range(shards)]
    shard_dirs = []
    procs = []
    for i, bucket in enumerate(buckets):
        if not bucket:
            continue
        d = ns / f"shard_{i:02d}"
        d.mkdir()
        sub = dict(reg)
        sub["seeds"] = bucket
        sub["shard"] = {"index": i, "of": shards, "parent": ns.name}
        (d / reg_file).write_text(json.dumps(sub, indent=1, sort_keys=True) + "\n")
        for s in SUBS:
            (d / s).mkdir(parents=True, exist_ok=True)
        log = (d / "console.log").open("w")
        env = dict(os.environ)
        env["AGENTROUTER_LABEL_MODEL"] = label
        env["ACTS_FAILURE_LOG"] = str(d / "failure_log.jsonl")
        procs.append((subprocess.Popen(
            [sys.executable, "-u", str(ROOT / CLI_RUNNER), str(d)],
            cwd=str(ROOT), env=env, stdout=log, stderr=subprocess.STDOUT), log, d))
        shard_dirs.append(d)
        time.sleep(0.4)
    print(f"[shard] {len(shard_dirs)} shards started", flush=True)
    bad = 0
    for p, log, d in procs:
        rc = p.wait()
        log.close()
        if rc != 0:
            bad += 1
            print(f"[shard] {d.name} exit {rc}", flush=True)
    summary = merge_shards(ns, shard_dirs, reg["protocol"], reg)
    print(f"[shard] merged sessions={summary['sessions']} "
          f"failures={summary['provider_failures']} bad_shards={bad}", flush=True)
    return 0 if bad == 0 else 1


def main(orig_name, dry=False, shards=DEFAULT_SHARDS):
    orig = ROOT / orig_name
    if not orig.is_dir():
        raise SystemExit(f"missing {orig_name}")
    reg_file, reg = pick_registration(orig)
    if not reg:
        raise SystemExit(f"no registration in {orig_name}")

    # Per-cohort matched-rerun spec (RERUN_SPECS_20261103.json): carries the
    # cohort's own floor, adapter, label, route and runner. The p023 adapter is
    # correct only for the 4200-floor cohorts; P014/label-series ran at 2800,
    # P024b at 8400, and the kimi-k3 labels live on the APINEX route.
    spec = SPECS.get(orig_name)
    if spec:
        label = spec["label"]
        floor = int(spec["floor"])
        adapter_name = spec["adapter"]
        runner_path = spec["runner_path"]
        seeds_spec = [int(s) for s in spec["seeds"]]
        fixture = spec.get("fixture")
    else:
        label = reg.get("label") or reg.get("model_label")
        floor = int(reg.get("token_floor", 0) or 0)
        adapter_name = ADAPTER_NAME
        runner_path = reg.get("runner_path")
        seeds_spec = None
        fixture = None
    if not label:
        raise SystemExit(f"{orig_name}: no label")
    if floor != 4200 and adapter_name == ADAPTER_NAME:
        raise SystemExit(f"{orig_name}: floor {floor} needs a dedicated adapter, not {ADAPTER_NAME}")

    ns = ROOT / (orig.name + "__rerun_ar_20261103")
    if ns.exists():
        shutil.rmtree(ns)
    ns.mkdir(parents=True)

    for f in (reg_file, "PREREGISTRATION.md"):
        if (orig / f).exists():
            shutil.copy2(orig / f, ns / f)

    use_adapter = ROOT / adapter_name
    adapter_sha = sha(use_adapter)
    reg = dict(reg)
    reg["protocol"] = f"{reg.get('protocol', orig.name)}-RERUN-AR-v1"
    reg["rerun_of"] = orig.name
    reg["rerun_reason"] = ("transport-damaged cohort re-run; same label, seeds, fixture, "
                           "prompts, oracle and registered token floor; only the "
                           "transport/adapter generation differs")
    reg["adapter"] = adapter_name
    reg["adapter_sha256"] = adapter_sha
    reg["token_floor"] = floor
    reg["token_floor_effective"] = floor
    reg["label"] = label
    if runner_path:
        reg["runner_path"] = runner_path
    if fixture:
        reg["fixture"] = fixture
    if seeds_spec:
        reg["seeds"] = seeds_spec
    reg["workers"] = 8
    reg["registered"] = "2026-11-03"

    launchers = sorted(p for p in orig.glob("run_*.py") if "analyze" not in p.name)
    patch_notes = {}
    for p in launchers:
        dst = ns / p.name
        if "provider_adapter" in p.read_text():
            patch_notes[p.name] = patch_launcher(p, dst, adapter_sha)
        else:
            shutil.copy2(p, dst)
    if patch_notes:
        reg["launcher_patched"] = patch_notes
    reg_json = json.dumps(reg, indent=1, sort_keys=True) + "\n"
    (ns / reg_file).write_text(reg_json)
    if reg_file != "_REGISTRATION.json":
        # canonical registration copy: shard_base_main and the workers read this
        (ns / "_REGISTRATION.json").write_text(reg_json)

    env = dict(os.environ)
    env["AGENTROUTER_LABEL_MODEL"] = label
    env["APINEX_LABEL_MODEL"] = label
    env["ACTS_FAILURE_LOG"] = str(ns / "failure_log.jsonl")
    env["ACTS_CONCURRENCY"] = "8"  # launcher shapes are serial without this knob
    env.pop("ACTS_SEEDS", None)

    # Shape 3: serial CLI runner -> shard it.
    uses_pc = any("parallelize_cohort" in p.read_text() for p in launchers)
    if not launchers or not uses_pc:
        if not launchers or "run_modern_aead_cohort" in reg.get("runner_path", ""):
            print(f"[clone] {orig.name} -> {ns.name} sharded x{shards} label={label}",
                  flush=True)
            if dry:
                return 0
            return run_sharded(ns, reg_file, reg, label, shards)
        # Shape 2b: frozen 2x2 runner whose main() is serial (~48 sessions/h) ->
        # shard by seed across N concurrent base.main() processes instead of
        # running the launcher serially. Same runner bytes, same adapter, same
        # plan; only the scheduling differs, per the clone's registration note.
        if "run_info_contract_2x2_" in str(reg.get("runner_path", "")):
            print(f"[clone] {orig.name} -> {ns.name} sharded-via-base.main x{shards} "
                  f"label={label}", flush=True)
            if dry:
                return 0
            return subprocess.call([sys.executable, "-u", str(ROOT / "shard_base_main.py"),
                                    ns.name, str(shards)])

    if launchers:
        launcher = launchers[0]
        cmd = [sys.executable, "-u", launcher.name]
        print(f"[clone] {orig.name} -> {ns.name} via {launcher.name} label={label}",
              flush=True)
    else:
        cmd = [sys.executable, "-u", str(ROOT / CLI_RUNNER), str(ns)]
        print(f"[clone] {orig.name} -> {ns.name} via {CLI_RUNNER} label={label}",
              flush=True)

    if dry:
        print("dry:", " ".join(cmd))
        return 0
    with (ns / "runner_console.log").open("w") as log:
        return subprocess.call(cmd, cwd=str(ns), env=env, stdout=log,
                               stderr=subprocess.STDOUT)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: rerun_ar_clone.py <original_namespace> [--dry] [--shards N]")
    n = DEFAULT_SHARDS
    if "--shards" in sys.argv:
        n = int(sys.argv[sys.argv.index("--shards") + 1])
    sys.exit(main(sys.argv[1], "--dry" in sys.argv, n))
