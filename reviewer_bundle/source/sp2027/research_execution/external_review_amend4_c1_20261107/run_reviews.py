#!/usr/bin/env python3
"""Independent GPT-family review of the Amend-4 + C1 numbers (blind).
Review A: C1 confirmatory — derive H1/H2/H3 + Holm from raw session rows.
Review B: Amend-4 — verify the headline counts from the frozen record.
Both payloads contain DATA ONLY (no reference numbers)."""
import json, os, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from agentrouter_client import AgentRouterClient, ProviderFailure

KEY = os.environ.get("AGENTROUTER_API_KEY", "")
LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]
BASE = "https://agentrouter.org"

PROMPT_A = """You are an independent statistical reviewer. Below are 64 session
records from a completed experiment: 16 seeds x 4 cells. Cells:
C1 = named+stated premise, C2 = unnamed+withheld premise,
C3 = unnamed+stated premise, C4 = named+withheld premise.
Each session has accepted=true/false (the registered oracle's decision).

Derive EVERYTHING yourself from the data. Output STRICT JSON only.

A1: accepted counts per cell (over all 16 seeds each).
A2: H1 paired C1-vs-C4: for each of the 16 seeds compare accepted(C1,seed)
    vs accepted(C4,seed); report: one_directional_discordances (C1 accepted
    and C4 not), counter_directional_discordances (C4 accepted and C1 not),
    ties. The registered primary statistic: exact two-sided binomial
    p = 2 * 0.5^b where b = one_directional_discordances (p=1 if b=0).
A3: H2 premise marginal: Fisher exact ONE-SIDED (greater) on the 2x2 table
    [stated-accepted, stated-rejected; withheld-accepted, withheld-rejected]
    where stated = C1+C3 sessions, withheld = C2+C4 sessions.
A4: H3 naming marginal: Fisher exact TWO-SIDED on named (C1+C4) vs unnamed
    (C2+C3) accepted counts.
A5: Holm step-down for m=3 at alpha=0.05: sort the three p-values ascending;
    multiply by 3, 2, 1 respectively with step-down monotonicity (running max,
    capped at 1); report each adjusted p and whether < 0.05.
A6: registered-bar verdict: does H1 clear Holm within the family AND is the
    discordance strictly one-directional (counter_directional == 0)?
    Output "CLEARED" or "NOT_CLEARED" plus one sentence.

{"A1":{"C1":n,"C2":n,"C3":n,"C4":n},
 "A2":{"one_directional_discordances":b,"counter_directional_discordances":c,
       "ties":t,"p":p},
 "A3":{"stated_accepted":n,"stated_rejected":n,"withheld_accepted":n,
       "withheld_rejected":n,"p_one_sided":p},
 "A4":{"named_accepted":n,"unnamed_accepted":n,"p_two_sided":p},
 "A5":{"H1":{"p":p,"holm":a,"sig":bool},"H2":{...},"H3":{...}},
 "A6":{"verdict":"CLEARED|NOT_CLEARED","reason":"..."}}

DATA (64 sessions):
"""

PROMPT_B = """You are an independent verification reviewer. The attached frozen
record has (1) 168 session statuses from a registered panel (3 labels x 7
tasks x 2 representations x 4 seeds; statuses SUCCESS/ORACLE_FAIL/CRASH/
TIMEOUT/AGENT_GIVEUP/PROVIDER_UNAVAILABLE; accepted/accepted_c2 flags under
two registered oracle codings C1=whole-stdout and C2=first-flag-token) and
(2) 57 per-program qualification rows (declared_v4 = the registered declared
rule, stress_repaired = the narrower stress rule; oracle_match = C1-correct,
oracle_match_c2 = C2-correct; violation rule lists for rejected programs).

Verify from the DATA ONLY. Output STRICT JSON only.

B1: session counts: total, by label, by status; count of accepted=true
    (C1) and accepted_c2=true (C2).
B2: program counts: total; oracle_match true count; oracle_match_c2 true
    count; declared_v4 true count; stress_repaired true count.
B3: among declared_v4=false programs: the violation-rule kinds and counts
    (across declared_violation_rules lists). State whether ANY import-rule
    violation (disallowed-import or disallowed-import-from) exists.
B4: tasks with at least one program (list distinct task_ids of programs);
    tasks with zero programs (the 7 registered tasks are: eps, eps_part2,
    almost_xor, another_xor, babycrypto, lowe, crack_me).
B5: per-label per-task C2 acceptance rates over declared_v4-qualified
    programs, for each task with any qualified program (state the rate and
    n per representation arm where both arms have n>0; else mark undefined).
B6: claim check: "the panel produced programs on 2 of 7 tasks" — true or
    false, with the two task names if true.

{"B1":{"total":n,"by_label":{...},"by_status":{...},"c1_accepted":n,
       "c2_accepted":n},
 "B2":{"programs":n,"oracle_match_c1":n,"oracle_match_c2":n,
       "declared_v4":n,"stress_repaired":n},
 "B3":{"violation_kinds":{...},"import_violation_exists":bool},
 "B4":{"tasks_with_programs":[...],"tasks_with_zero_programs":[...]},
 "B5":{...},
 "B6":{"verdict":bool,"tasks":[...]}}

DATA (168 session statuses + 57 program rows):
"""

def main():
    c1_payload = Path("/tmp/c1_blind_payload.json").read_text()
    a4_payload = Path("/tmp/amend4_verify_payload.json").read_text()
    out = HERE / "outputs"
    out.mkdir(exist_ok=True)
    for label in LABELS:
        for name, prompt in (("c1_blind", PROMPT_A + c1_payload),
                             ("amend4_verify", PROMPT_B + a4_payload)):
            dst = out / f"{label.replace('/','_')}__{name}.json"
            if dst.exists():
                print("skip existing", dst.name); continue
            print(f"calling {label} :: {name}", flush=True)
            try:
                client = AgentRouterClient(KEY, label, BASE, None)
                t0 = time.time()
                r = client.call(prompt, 8000, timeout=600)
                dst.write_text(json.dumps({"model": label, "review": name,
                    "elapsed_s": round(time.time()-t0,1), "stop_reason": r["metadata"].get("finish_reason"),
                    "content": r["text"], "usage": r["metadata"].get("usage")}, indent=1))
                print(f"  ok {round(time.time()-t0,1)}s, {len(r['text'])} chars", flush=True)
            except ProviderFailure as exc:
                dst.write_text(json.dumps({"model": label, "review": name,
                    "error": f"{exc.category}: {exc.detail}"[:300]}, indent=1))
                print(f"  FAILED {exc.category}", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
