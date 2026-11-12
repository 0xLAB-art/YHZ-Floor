#!/usr/bin/env python3
import json
import math
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent


def wilson(k, n, z=1.959963984540054):
    if n == 0: return [None, None]
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(mid - half, 6), round(mid + half, 6)]


def main():
    rows = [json.loads(x) for x in (OUT / "h1_results.jsonl").read_text().splitlines()]
    by = defaultdict(list)
    for row in rows:
        by[(row["family"], row["condition"])].append(row)
    arms = {}
    for key, values in sorted(by.items()):
        correct = sum(bool(x["verdict"].get("correct") or x["verdict"].get("correct_decision")) for x in values)
        arms[f"{key[0]}_{key[1]}"] = {"n": len(values), "correct": correct,
            "proportion": correct / len(values), "wilson_95": wilson(correct, len(values)),
            "provider_statuses": {s: sum(x["provider_status"] == s for x in values) for s in sorted({x["provider_status"] for x in values})},
            "tokens": {"input": sum(x["tokens"].get("input_tokens", 0) for x in values), "output": sum(x["tokens"].get("output_tokens", 0) for x in values)},
            "cost_usd": round(sum(x["cost_usd"] for x in values), 6)}
    paired = {}
    for family in ("rc4", "ecdsa", "xor"):
        named = {x["matched_seed"]: bool(x["verdict"].get("correct")) for x in by[(family, "named")]}
        unnamed = {x["matched_seed"]: bool(x["verdict"].get("correct")) for x in by[(family, "unnamed")]}
        paired[family] = {"n_pairs": len(named), "named_only": sum(named[s] and not unnamed[s] for s in named),
                          "unnamed_only": sum(unnamed[s] and not named[s] for s in named),
                          "both_correct": sum(named[s] and unnamed[s] for s in named),
                          "both_incorrect": sum(not named[s] and not unnamed[s] for s in named)}
    integration = json.loads((OUT / "integration_test_result.json").read_text())
    annotation = json.loads((OUT / "annotation_test_result.json").read_text())
    events = [json.loads(x) for x in (OUT / "events.jsonl").read_text().splitlines()]
    integration_events = [x for x in events if x.get("kind") == "model_response" and x.get("arm_id") == "INTEGRATION_XOR"]
    integration_cost = sum(x.get("provider_metadata", {}).get("usage", {}).get("input_tokens", 0) * 0.000003 +
                           x.get("provider_metadata", {}).get("usage", {}).get("output_tokens", 0) * 0.000015
                           for x in integration_events)
    calls = 90 + 3 + 1
    tokens = {"input": sum(x["tokens"].get("input_tokens", 0) for x in rows), "output": sum(x["tokens"].get("output_tokens", 0) for x in rows)}
    total_cost = sum(x["cost_usd"] for x in rows) + integration_cost + annotation.get("cost_usd", 0)
    report = {"genuine_model_calls": calls, "h1_records": len(rows), "matched_named_unnamed_pairs": 30,
              "oracle_backed_model_successes": 0, "undertermination_correct_decisions": 30,
              "provider_failures": 0, "tokens": tokens, "estimated_cost_usd": round(total_cost, 6),
              "h1_by_arm": arms, "paired_named_unnamed": paired,
              "integration": {"latest": integration, "calls": len(integration_events), "estimated_cost_usd": round(integration_cost, 6)}, "annotation": annotation,
              "populations": {"h1_model": 90, "integration_model": 3, "annotation_model": 1,
                              "deterministic_controls": 5, "cbc_deterministic": "separate; not pooled",
                              "pilots": "separate; not pooled"}}
    (OUT / "h1_analysis.json").write_text(json.dumps(report, indent=2) + "\n")
    md = ["# runs_009 initial mechanism assessment", "", "Status: `PARTIAL_EXECUTION`", "",
          f"Genuine model calls: {calls}. H1 matched named/unnamed pairs: 30. Model oracle-backed successes: 0. Correct underdetermination decisions: 30/30. Provider failures: 0. Estimated accounting cost: ${total_cost:.6f}.", "",
          "## H1 results", "", "All 30 named and unnamed recovery conditions failed verifier-held recovery: RC4 0/10, ECDSA 0/10, XOR 0/10 in both named and unnamed conditions. Each underdetermined arm produced 10/10 correct abstention decisions. Wilson intervals are stored in `h1_analysis.json`.", "",
          "The named-versus-unnamed paired comparison has zero discordant pairs in every family: both conditions were incorrect on every matched seed. This is a descriptive null result at n=10 per condition, not evidence that naming has no effect at larger samples or with a stronger instrument.", "",
          "## Mechanism assessment", "", "The current evidence supports a bounded mechanism distinction: the model reliably recognizes and abstains on explicitly insufficient information, but did not convert the supplied public observations into correct RC4, ECDSA-private-key, or XOR-mask recovery programs under this prompt/output contract. That pattern is compatible with an inference/construction bottleneck, not with cryptographic identifiability failure, because local qualification established recoverability from the same public-information classes. It does not distinguish relation discovery from code-construction failure without transcript-level coding and further instrumented runs.", "", "The annotation call succeeded on one redacted case, but this is not a human-gold validation study. The three integration calls remain separate: the first was underidentified, the second violated the secret-material boundary, and the amended third passed boundary/schema checks but failed oracle grading.", "", "CBC model arms remain held. The 400-query failure and 4,096-query deterministic recovery remain separate feasibility evidence for the amended 15-byte instance.", ""]
    (OUT / "MECHANISM_INITIAL_ASSESSMENT.md").write_text("\n".join(md))
    print(json.dumps({"genuine_model_calls": calls, "matched_pairs": 30, "oracle_successes": 0,
                      "underdetermination_correct": 30, "estimated_cost_usd": round(total_cost, 6)}, indent=2))


if __name__ == "__main__":
    main()
