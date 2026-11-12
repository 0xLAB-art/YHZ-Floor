"""Synthetic regression fixtures; none constitute new experimental evidence."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PAPER = Path(__file__).resolve().parents[1] / "paper"
sys.path.insert(0, str(PAPER))
import build_lock_replay_artifact as builder

spec = importlib.util.spec_from_file_location("major_claim_rederive", PAPER / "artifact_tools/rederive.py")
rederive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rederive)


class MajorReconstructionTests(unittest.TestCase):
    def test_missing_pilot_records_cannot_pass_via_complete_derived_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "sp2027/agent-eval/runs_w2_pilot"
            corpus.mkdir(parents=True)
            analysis = root / "sp2027/analysis"
            analysis.mkdir(parents=True)
            (analysis / "aor_runs_w2_pilot.json").write_text(json.dumps(
                {"rows": [{"run_id": f"v2_synthetic_{n}"} for n in range(20)]}))
            (corpus / "v2_synthetic_0.json").write_text("{}")
            with self.assertRaises(ValueError):
                rederive.pilot_decomposition(root)

    def test_campaign_projection_excludes_identifying_errors_and_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "sp2027/agent-eval/runs_e2/v2_synthetic.json"
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps({"run_id": "v2_synthetic", "task_card": {"task_id": "synthetic"},
                "model_config": {"model_id": "synthetic"},
                "session": {"status": "TOOL_FAILURE", "error": "IDENTIFYING_TRACE"},
                "oracle": {"agent_content": "EXCLUDED_CONTENT"}}))
            output, inventory = root / "export", {}
            with patch.object(builder, "ROOT", root):
                builder.export(source, output, inventory, "campaign_identity_metadata")
            exported = (output / source.relative_to(root)).read_text()
            self.assertNotIn("IDENTIFYING_TRACE", exported)
            self.assertNotIn("EXCLUDED_CONTENT", exported)
            self.assertEqual(json.loads(exported)["session"], {"status": "TOOL_FAILURE"})


if __name__ == "__main__":
    unittest.main()
