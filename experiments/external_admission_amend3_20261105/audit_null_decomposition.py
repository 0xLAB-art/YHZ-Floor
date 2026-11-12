#!/usr/bin/env python3
"""Post-hoc decomposition audit of the Amendment-3 measured null.

Disclosed post-hoc investigation.  Reads ONLY frozen artifacts:

  results.jsonl              168 sessions (3 labels x 7 tasks x R0/RT x 8)
  oracle/answers.json        pinned answers + the oracle's matching semantics
  sessions/programs/*.py     all 282 retained agent programs
  sessions/prompts/*.txt     the delivered prompts (RT delivery verification)
  fixtures/tasks/            the original artifact files
  fixtures/decode_equality_log.json   the build-time delivery gate

Produces the three-layer decomposition of the registered null:

  layer 1  statement-faithful solves rejected by the answer pin
           (the program's stdout contains the pinned flag token; the oracle
           requires the ENTIRE stdout, stripped, to EQUAL the pinned answer,
           so a session that prints the full decrypted message scores
           ORACLE_FAIL.  Rescored under the benchmark reference solver's own
           semantics -- first flag-shaped token -- these are solves.)
  layer 2  crash floor (returncode != 0; a status class the registered
           taxonomy lacks -- crashes masquerade as ORACLE_FAIL)
  layer 3  RT delivery verification (prompt blob vs original artifact bytes;
           the earlier "broken delivery" suspicion was an audit-regex bug
           that captured the DECODE NOTE line as blob characters)

Deterministic; no model calls; no network.
"""
import base64
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "AUDIT_NULL_DECOMPOSITION.json"
ANSWERS = json.loads((HERE / "oracle" / "answers.json").read_text())
ANS = ANSWERS["answers"]
FLAG_RE = re.compile(r"flag\{[ -~]*?\}")


def sha256_path(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def extract_blob(txt):
    """Blob = the base64 lines AFTER the DECODE NOTE line (the earlier audit
    regex captured the note itself, which poisoned strict decoding)."""
    m = re.search(r"--- FILE: (.+?) \(base64\) ---\nDECODE NOTE:.*?\n(.*?)(?=\n--- FILE:|\n\nTASK|\Z)",
                  txt, re.S)
    if not m:
        return None, None
    name, body = m.group(1), m.group(2)
    lines = [l.strip() for l in body.splitlines()
             if re.fullmatch(r"[A-Za-z0-9+/=]+", l.strip())]
    return name, "".join(lines)


rows = [json.loads(l) for l in (HERE / "results.jsonl").read_text().splitlines() if l.strip()]
content = [r for r in rows if r["status"] != "PROVIDER_UNAVAILABLE"]

# ---- layer classification (two stated counting rules) -----------------------
# any-turn rule  : a session counts on the first matching state in ANY turn's
#                  records (mirrors the benchmark's flag-in-output diagnostic,
#                  which scans every produced message).
# terminal rule  : only the FINAL submitted program's outcome counts (the
#                  registered oracle scores the submitted candidate).
layer1, layer2, wrong = [], [], []            # any-turn layers
solved_term, crash_term, wrong_term = [], [], []  # terminal layers
for r in content:
    tails = [(t.get("stdout_tail", ""), t.get("stderr_tail", ""), t.get("returncode"))
             for t in r.get("turn_records", [])]
    solved_norm = any(FLAG_RE.search(s) and FLAG_RE.search(s).group(0) == ANS[r["task_id"]]
                      for s, _, _ in tails)
    crashed = any(rc not in (0, None) for _, _, rc in tails)
    rec = {"run_id": r["run_id"], "task_id": r["task_id"], "label": r["label"],
           "representation": r["representation"], "crashed": crashed,
           "solved_normalized": solved_norm}
    if solved_norm:
        layer1.append(rec)
    elif crashed:
        layer2.append(rec)
    else:
        wrong.append(rec)
    # terminal rule: final submitted turn
    subs = [t for t in r.get("turn_records", []) if t.get("submitted")]
    last = subs[-1] if subs else (r["turn_records"][-1] if r.get("turn_records") else {})
    m_last = FLAG_RE.search(last.get("stdout_tail", "") or "")
    solved_term_flag = bool(m_last and m_last.group(0) == ANS[r["task_id"]])
    trec = {"run_id": r["run_id"], "task_id": r["task_id"], "label": r["label"],
            "representation": r["representation"],
            "terminal_status": r["status"],
            "terminal_rc": last.get("returncode"),
            "solved_final": solved_term_flag}
    if solved_term_flag:
        solved_term.append(trec)
    elif last.get("returncode") not in (0, None):
        crash_term.append(trec)
    else:
        wrong_term.append(trec)


def crash_sig(errs):
    if any("UnicodeDecodeError" in e for e in errs):
        return "model idiom: b64decode(...).decode() on a non-UTF-8 payload"
    if any("OverflowError" in e for e in errs):
        return "model idiom: int too large in bit decode"
    if any("ModuleNotFoundError" in e for e in errs):
        return "missing module"
    if any("FileNotFoundError" in e for e in errs):
        return "missing artifact file"
    if any(e.strip() for e in errs):
        return "other (non-empty stderr)"
    return "nonzero exit, empty stderr"


crash_modes = Counter()          # event-level: stderr of any turn, any-turn crash set
term_crash_modes = Counter()     # terminal-level: stderr of the crashing FINAL turn
by_run_any = {rec["run_id"]: rec for rec in layer2}
for rec in layer2:
    row = next(r for r in content if r["run_id"] == rec["run_id"])
    errs = [t.get("stderr_tail", "") for t in row.get("turn_records", [])]
    crash_modes[crash_sig(errs)] += 1
for rec in crash_term:
    row = next(r for r in content if r["run_id"] == rec["run_id"])
    subs = [t for t in row.get("turn_records", []) if t.get("submitted")]
    last = subs[-1] if subs else (row["turn_records"][-1] if row.get("turn_records") else {})
    term_crash_modes[crash_sig([last.get("stderr_tail", "") or ""])] += 1

terminal_wrong_split = Counter(rec["terminal_status"] for rec in wrong_term)

# ---- terminal-crash final-exception classification (finer than crash_sig) ----
# Classifies each terminal crash by the LAST exception line of the FINAL
# submitted turn's stderr (the traceback's actual terminal exception), not by
# substring search. stderr tails are 140-char truncated, so a few records may
# show no recognizable exception line ("stderr-truncated-no-exc-line").
EXC_RE = __import__("re").compile(r"([A-Za-z_][A-Za-z_0-9.]*(?:Error|Exception))\s*[:\(]")
final_exc_modes = Counter()
for rec in crash_term:
    row = next(r for r in content if r["run_id"] == rec["run_id"])
    subs = [t for t in row.get("turn_records", []) if t.get("submitted")]
    last = subs[-1] if subs else (row["turn_records"][-1] if row.get("turn_records") else {})
    err = last.get("stderr_tail", "") or ""
    ms = EXC_RE.findall(err)
    final_exc_modes[ms[-1] if ms else
                    ("empty-stderr" if not err.strip() else "stderr-truncated-no-exc-line")] += 1

# ---- per task x arm decomposition table -------------------------------------
# (v2 bug fix: the old code compared session dicts against 6-key rec objects,
#  `if r in layer1`, which is always False -- every arm printed
#  solved=0/crashed=0/wrong=n.  v3 keys the aggregation by run_id.)
by_run = {rec["run_id"]: rec for rec in layer1}
by_run_crash = {rec["run_id"]: rec for rec in layer2}
by_run_term = {rec["run_id"]: rec for rec in solved_term}
by_run_crash_term = {rec["run_id"]: rec for rec in crash_term}
agg = defaultdict(Counter)
for r in content:
    key = (r["task_id"], r["representation"])
    a = agg[key]
    a["n"] += 1
    if r["run_id"] in by_run:
        a["solved_normalized_any_turn"] += 1
    elif r["run_id"] in by_run_crash:
        a["crashed_any_turn"] += 1
    else:
        a["wrong_output_any_turn"] += 1
    if r["run_id"] in by_run_term:
        a["solved_final"] += 1
    elif r["run_id"] in by_run_crash_term:
        a["crashed_final"] += 1
    else:
        a["without_crash_or_flag_final"] += 1
decomp = []
for key in sorted(agg):
    a = agg[key]
    decomp.append({"task_id": key[0], "representation": key[1], "n": a["n"],
                   "solved_normalized_any_turn": a["solved_normalized_any_turn"],
                   "crashed_any_turn": a["crashed_any_turn"],
                   "wrong_output_any_turn": a["wrong_output_any_turn"],
                   "solved_final": a["solved_final"],
                   "crashed_final": a["crashed_final"],
                   "without_crash_or_flag_final": a["without_crash_or_flag_final"]})

# ---- layer 3: RT delivery verification (corrected parse) --------------------
rt_verify = []
for f in sorted((HERE / "sessions" / "prompts").glob("*__RT__*turn1.txt")):
    task = f.name.split("__")[2]
    name, blob = extract_blob(f.read_text())
    if blob is None:
        rt_verify.append({"task_id": task, "prompt": f.name, "blob_found": False})
        continue
    try:
        dec = base64.b64decode(blob, validate=True)
        h = hashlib.sha256(dec).hexdigest()
    except Exception as e:
        rt_verify.append({"task_id": task, "prompt": f.name, "blob_found": True,
                          "strict_decode_ok": False, "error": str(e)[:80]})
        continue
    orig = list((HERE / "fixtures" / "tasks" / task).iterdir())[0]
    h_orig = hashlib.sha256(orig.read_bytes()).hexdigest()
    rt_verify.append({"task_id": task, "prompt": f.name, "blob_found": True,
                      "strict_decode_ok": True, "artifact_name": name,
                      "decoded_sha256": h, "original_sha256": h_orig,
                      "byte_exact": h == h_orig})

rt_ok = sum(1 for v in rt_verify if v.get("byte_exact"))
rt_total = len(rt_verify)

# ---- oracle semantics + statement/pin tension -------------------------------
r0_prompt = (HERE / "fixtures" / "rt_transform" / "2015q-cry-eps" / "prompt_R0.txt").read_text()
stmt = re.search(r"TASK STATEMENT \(verbatim from the benchmark metadata\):\n(.+)",
                 r0_prompt).group(1).strip()

# ---- eps RT crash mechanism: every program b64-decodes the FILE -------------
eps_rt_pattern = Counter()
for r in content:
    if r["task_id"] != "2015q-cry-eps" or r["representation"] != "RT":
        continue
    for p in r.get("programs", []):
        src = Path(p["path"]).read_text()
        if ".mpeg" in src and "b64decode" in src:
            eps_rt_pattern["reads file, b64-decodes its content"] += 1
        elif "b64decode" in src:
            eps_rt_pattern["decodes prompt blob"] += 1
        else:
            eps_rt_pattern["neither"] += 1

# ---- babycrypto near-solve: stdout is plaintext with bit 7 set --------------
baby_near = []
for r in content:
    if r["task_id"] != "2018q-cry-babycrypto":
        continue
    for t in r.get("turn_records", []):
        out = t.get("stdout_tail", "")
        if not out:
            continue
        non_ascii = sum(1 for c in out if ord(c) > 0x7F)
        if non_ascii > len(out) // 3:
            demo = "".join(chr(ord(c) ^ 0xFF) if 32 <= (ord(c) ^ 0xFF) < 127 else "."
                           for c in out[:80])
            baby_near.append({"run_id": r["run_id"], "representation": r["representation"],
                              "stdout_is_plaintext_xor_ff": True, "xored_head": demo})
            break

provenance = {
    "results_sha256": sha256_path(HERE / "results.jsonl"),
    "answers_sha256": sha256_path(HERE / "oracle" / "answers.json"),
    "decode_equality_sha256": sha256_path(HERE / "fixtures" / "decode_equality_log.json"),
    "oracle_semantics": ("registered candidate_ok = (stage == output) and (returncode == 0) "
                         "and stdout.strip() == pinned answer  -- whole-stdout exact match"),
    "reference_solver_semantics": ("first flag-shaped token extracted from the decoded text "
                                   "(criterion-5 solvers)"),
}

payload = {
    "schema": "amend3-null-decomposition-audit/3",
    "disclosure": ("POST-HOC investigation, disclosed per the project's amendment "
                   "discipline; the registered Amendment-3 verdicts are unchanged. "
                   "v2 corrected the v1 audit regex (it captured the DECODE NOTE line "
                   "as blob characters, producing a false 'invalid base64' and a "
                   "false 'broken RT delivery' suspicion) and replaced the crash "
                   "taxonomy's guessed '(RT path)' label with the measured model "
                   "idioms. v3 fixes the v2 per-arm aggregation bug (a session dict "
                   "was tested for membership in 6-key layer-record lists, `if r in "
                   "layer1`, which is always False -- every arm printed "
                   "solved=0/crashed=0/wrong=n, contradicting this file's own "
                   "summary) and states the counting rules explicitly: the "
                   "any-turn layers (unchanged from v2) mirror the benchmark's "
                   "flag-in-output diagnostic (scripts/flag_in_output.py in the "
                   "pinned nyuctf_agents harness: a solve whenever the flag appears "
                   "in ANY produced message), while the terminal layers score only "
                   "the FINAL submitted program. The benchmark's primary metric -- "
                   "an exact-string CheckFlag tool submission -- has no counterpart "
                   "in this harness. Delivery is verified byte-exact in 84/84 RT "
                   "prompts."),
    "provenance": provenance,
    "summary": {
        "content_sessions": len(content),
        "oracle_fail_sessions": sum(1 for r in content if r["status"] == "ORACLE_FAIL"),
        "timeout_sessions": sum(1 for r in content if r["status"] == "TIMEOUT"),
        "giveup_sessions": sum(1 for r in content if r["status"] == "AGENT_GIVEUP"),
        "layer1_statement_faithful_flag_outputs_any_turn": len(layer1),
        "layer1_final_submission": len(solved_term),
        "layer1_tasks": dict(Counter(x["task_id"] for x in layer1)),
        "layer1_labels": dict(Counter(x["label"] for x in layer1)),
        "layer1_representations": dict(Counter(x["representation"] for x in layer1)),
        "layer2_crashes_any_turn": len(layer2),
        "layer2_terminal_crashes": len(crash_term),
        "crash_modes_event_level_any_turn": dict(crash_modes),
        "terminal_crash_modes": dict(term_crash_modes),
        "terminal_crash_final_exception": dict(final_exc_modes),
        "wrong_answer_outputs_any_turn": len(wrong),
        "terminal_without_crash_or_flag": len(wrong_term),
        "terminal_without_crash_or_flag_by_status": dict(terminal_wrong_split),
        "rt_delivery_byte_exact": f"{rt_ok}/{rt_total}",
    },
    "statement_pin_tension_eps": {
        "task_statement_verbatim": stmt,
        "pinned_answer": ANS["2015q-cry-eps"],
        "note": ("the statement says the flag is the ENTIRE decryption; the pin holds "
                 "only the flag token. The 11 layer-1 programs printed the entire "
                 "decryption -- statement-faithful, pin-rejected."),
    },
    "eps_rt_crash_mechanism": {
        "programs_by_pattern": dict(eps_rt_pattern),
        "note": ("12/12 eps-RT programs read the working-dir FILE (plain bits text) "
                 "and base64-decode its content anyway -- the DECODE NOTE's framing "
                 "overrode the file's self-evident content; b64decode(validate=False) "
                 "accepts the digits and yields garbage bytes, then .decode() crashes."),
    },
    "babycrypto_near_solve": baby_near,
    "task_arm_decomposition": decomp,
    "layer1_records_any_turn": layer1,
    "layer1_records_final_submission": solved_term,
    "layer2_records_any_turn": layer2,
    "layer2_records_terminal": crash_term,
    "terminal_without_crash_or_flag_records": wrong_term,
    "rt_delivery_verification": rt_verify,
}
OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
s = payload["summary"]
print(f"wrote {OUT}")
for k, v in s.items():
    print(f"  {k}: {v}")
print(f"  eps RT programs: {dict(eps_rt_pattern)}")
print(f"  babycrypto near-solves (stdout = plaintext^0xFF): {len(baby_near)}")
