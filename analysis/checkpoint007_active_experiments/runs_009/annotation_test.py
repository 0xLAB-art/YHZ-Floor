#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from durable_runner import DurableRunner


def main():
    redacted = {"run_id": "redacted-case-001", "arm": "H1", "model_output": "<candidate-value-redacted>",
                "provider_status": "model_response", "finish_reason": "end_turn",
                "transcript_boundary": "raw model response only"}
    prompt = ("Annotate this redacted transcript. Return JSON only with annotation_label equal to one of "
              "COMPLETE_RESPONSE, MALFORMED_RESPONSE, REFUSAL, or PROVIDER_FAILURE. Do not infer or provide any secret. "
              + json.dumps(redacted, sort_keys=True))
    runner = DurableRunner()
    result = runner.run_provider_combination("E_ANNOTATION", 1, "P009-annotation-v1", prompt, max_tokens=128)
    out = {"run_id": result.get("run_id"), "status": result.get("status"), "input_truth_excluded": True,
           "annotation_label": None, "schema_valid": False, "gold_label_held_out": "COMPLETE_RESPONSE",
           "model_agrees_with_gold": False}
    if result.get("status") == "model_response":
        text = result["text"].strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            obj = json.loads(text)
        except (ValueError, TypeError, json.JSONDecodeError):
            obj = {}
        label = obj.get("annotation_label") if isinstance(obj, dict) else None
        out["annotation_label"] = label
        out["schema_valid"] = label in {"COMPLETE_RESPONSE", "MALFORMED_RESPONSE", "REFUSAL", "PROVIDER_FAILURE"}
        out["model_agrees_with_gold"] = label == out["gold_label_held_out"]
        usage = result.get("metadata", {}).get("usage", {})
        out["tokens"] = usage
        out["cost_usd"] = usage.get("input_tokens", 0) * 0.000003 + usage.get("output_tokens", 0) * 0.000015
    path = Path(__file__).resolve().parent / "annotation_test_result.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    runner.emit(result.get("run_id", "annotation"), "annotation_verdict", out)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
