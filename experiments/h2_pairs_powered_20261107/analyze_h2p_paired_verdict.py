#!/usr/bin/env python3
"""H2-POWERED registered verdict — the PAIRED exact binomial (frozen).

Computes exactly the registered primary statistic of
PREREGISTRATION_H2_POWERED.md section 3 from the fresh recovery-wave rows
in results.jsonl (the transport-blocked rows live in
results_transport_blocked_441_472.jsonl and are NOT read):

  per seed: A-accepted vs B-accepted (status SUCCESS);
  b_A = one-directional discordances (A accepted, B not — the interactive
        arm's advantage);
  b_B = counter-directional discordances (reported; 0 required for a
        directional claim);
  REGISTERED SIGNIFICANCE: b_A >= 6  (p = 2 * 0.5^b_A = 0.03125 at 6);
  if b_A < 6: the Wilson 95% upper bound on the one-directional discordance
  rate is the honest operating point (prereg section 4).

Secondary descriptives (not tests, prereg section 3): the A revision
pathway (turn-2 submissions/recoveries), oracle-budget compliance (max
accepted queries <= 4096), the rejection classification, per-arm query
totals, and the amendment-4 per-arm TRANSPORT ATTEMPT DISTRIBUTION (a
differential attempt rate between arms would itself be measured evidence
of content-dependence).

No pooling with the frozen cohorts; no other test.  Run AFTER the wave
(or at any checkpoint — it is deterministic over the rows present).
"""
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORACLE_BUDGET = 4096
REGISTERED_BAR = 6


def wilson_upper(k, n, z=1.959963985):
    if n == 0:
        return None
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return min(1.0, (centre + spread) / denom)


def main():
    rows = [json.loads(l) for l in (HERE / "results.jsonl").read_text().splitlines()
            if l.strip()]
    by_seed_arm = {}
    for r in rows:  # first row per (seed, arm) wins; resume guard never rewrites
        by_seed_arm.setdefault((r["seed"], r["arm"]), r)

    # only COMPLETE pairs are evaluable (interim checkpoints see one arm of
    # the newest seed; an incomplete pair contributes neither a discordance
    # nor a tie — at the full 64 rows this changes nothing)
    seeds = sorted({s for s, _ in by_seed_arm
                    if (s, "A_INTERACTIVE") in by_seed_arm
                    and (s, "B_ONESHOT") in by_seed_arm})

    def acc(seed, arm):
        r = by_seed_arm.get((seed, arm))
        return 1 if (r and r["status"] == "SUCCESS") else 0

    b_a = b_b = ties = 0
    a_only_seeds, b_only_seeds = [], []
    for s in seeds:
        a, b = acc(s, "A_INTERACTIVE"), acc(s, "B_ONESHOT")
        if a and not b:
            b_a += 1
            a_only_seeds.append(s)
        elif b and not a:
            b_b += 1
            b_only_seeds.append(s)
        else:
            ties += 1

    evaluable_pairs = len(seeds)
    p_b_a = None if b_a == 0 else 2 * 0.5 ** b_a
    significant = b_a >= REGISTERED_BAR
    one_directional = b_b == 0

    def arm_block(arm):
        sub = [by_seed_arm[(s, arm)] for s in seeds if (s, arm) in by_seed_arm]
        attempts = [ca for r in sub for ca in r.get("call_attempts", [])]
        n_calls = len(attempts)
        multi = sum(1 for ca in attempts if ca["n_attempts"] > 1)
        fails = Counter(c for ca in attempts for c in ca.get("fail_categories", []))
        turn2 = sum(1 for r in sub for t in r["turn_records"]
                    if t["turn"] == 2 and t.get("submitted"))
        turn1_rej = sum(1 for r in sub if r["turn_records"]
                        and r["turn_records"][0].get("submitted")
                        and not r["turn_records"][0].get("accepted"))
        classes = Counter(t["error_class"] for r in sub for t in r["turn_records"]
                          if t.get("error_class"))
        acc_queries = [r["accepted_queries"] for r in sub
                       if r["status"] == "SUCCESS" and r.get("accepted_queries")]
        return {
            "sessions": len(sub),
            "accepted": sum(1 for r in sub if r["status"] == "SUCCESS"),
            "turn2_submissions": turn2,
            "turn1_rejections": turn1_rej,
            "rejected_program_error_classes": dict(classes),
            "accepted_query_range": ([min(acc_queries), max(acc_queries)]
                                     if acc_queries else None),
            "budget_violations": sum(1 for q in acc_queries if q > ORACLE_BUDGET),
            "transport_attempts": {
                "calls": n_calls,
                "calls_needing_retry": multi,
                "retry_share": round(multi / n_calls, 4) if n_calls else None,
                "max_attempts": max((ca["n_attempts"] for ca in attempts), default=0),
                "fail_categories": dict(fails),
            },
        }

    a_blk, b_blk = arm_block("A_INTERACTIVE"), arm_block("B_ONESHOT")

    out = {
        "schema": "h2-pairs-powered-paired-verdict/1",
        "protocol": "H2-CBC-PAIRS-POWERED-20261107-v1 (amendment 4)",
        "registered_statistic": {
            "name": "paired exact binomial on the A-vs-B acceptance discordance",
            "significance": "b_A >= 6 one-directional (p = 2*0.5^b_A)",
            "counter_directional_must_be": 0,
        },
        "rows_read": len(rows),
        "evaluable_pairs": evaluable_pairs,
        "pairs": {"b_A_interactive_advantage": b_a,
                  "b_B_counter_directional": b_b,
                  "ties": ties,
                  "a_only_seeds": a_only_seeds,
                  "b_only_seeds": b_only_seeds},
        "verdict": {
            "b_A": b_a, "p": p_b_a,
            "significant_at_registered_bar": significant,
            "one_directional": one_directional,
            "directional_claim": bool(significant and one_directional),
            "note": ("registered bar is b_A >= 6 AND zero counter-directional "
                     "discordances; no other test; no pooling"),
        },
        "wilson_bound_if_not_significant": {
            "one_directional_rate": round(b_a / evaluable_pairs, 4) if evaluable_pairs else None,
            "upper_95": wilson_upper(b_a, evaluable_pairs),
        },
        "arms": {"A_INTERACTIVE": a_blk, "B_ONESHOT": b_blk},
    }
    (HERE / "VERDICT_H2P.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["pairs"], indent=1))
    print(json.dumps(out["verdict"], indent=1))
    print("attempt share A:", a_blk["transport_attempts"]["retry_share"],
          "B:", b_blk["transport_attempts"]["retry_share"])


if __name__ == "__main__":
    main()
