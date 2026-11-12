#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from durable_runner import DurableRunner
from h1_fixtures import xor_instance


def main():
    public, key, target = xor_instance(901)
    prompt = ("Return one JSON object and no markdown. Infer the XOR mask from the public samples, "
              "then report the requested fields. Do not claim a value that cannot be inferred. "
              + json.dumps({"public_observations": public, "required_schema": {"mask_hex": "32 hex chars"}}, sort_keys=True))
    runner = DurableRunner()
    result = runner.run_provider_combination("INTEGRATION_XOR", 901, "P009-integration-v3", prompt, max_tokens=256)
    report = {"status": result["status"], "run_id": result.get("run_id"),
              "truth_boundary": {"prompt_contains_key": key.hex() in prompt, "prompt_contains_target": target.hex() in prompt},
              "output_complete": False, "syntax_valid": False, "oracle_grade": "NOT_SCORED", "cost_usd": 0.0}
    if result["status"] == "model_response":
        text = result["text"].strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        report["output_complete"] = bool(text)
        try:
            obj = json.loads(text)
            report["syntax_valid"] = isinstance(obj, dict) and bool(re.fullmatch(r"[0-9a-fA-F]{32}", obj.get("mask_hex", "")))
            if report["syntax_valid"]:
                report["oracle_grade"] = "PASS" if bytes.fromhex(obj["mask_hex"]) == key else "FAIL"
        except (ValueError, TypeError, json.JSONDecodeError):
            report["oracle_grade"] = "MALFORMED_OUTPUT"
        usage = result.get("metadata", {}).get("usage", {})
        report["tokens"] = usage
        report["cost_usd"] = (usage.get("input_tokens", 0) * 0.000003 + usage.get("output_tokens", 0) * 0.000015)
    runner.emit(result.get("run_id", "integration"), "integration_verdict", report)
    path = Path(__file__).resolve().parent / "integration_test_result.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
