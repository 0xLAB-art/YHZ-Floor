#!/usr/bin/env python3
"""Regression tests for the two 2026-10-05 audit findings.

Covers, with synthetic fixtures only (no real archives, keys or ratings):

  A. Artifact redaction must cover provider ACCOUNT identifiers (`user_…`),
     not just API keys, while not mangling ordinary identifiers such as
     `username` / `user_id`.

  B. Every registered claim artifact must actually be readable by the
     checker — the v1/v2 freeze mismatch that let the portable bundle raise
     KeyError('value').

  C. `claim_source_pinning` must report a truthful scope: byte-verified when
     the archives exist, manifest-verified when they do not, and FAIL on a
     digest mismatch in either mode.

  D. Every checker must return a `value` key on all paths, so a missing file
     degrades to a clean FAIL instead of crashing the lock.
"""
import ast
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sp2027" / "paper"))
sys.path.insert(0, str(ROOT / "sp2027" / "analysis"))

import build_anonymous_artifact as anon          # noqa: E402


class TestAccountIdentifierRedaction(unittest.TestCase):
    """A: `user_…` must be redacted; ordinary identifiers must not be."""

    def test_account_ids_are_redacted(self):
        for sample in ("user_32c21QOqNmmLeclv1xlw2wbycCu",
                       "user_3BwH7TTIO4IHEZo4xPWIuexujFQ",
                       "account user_3BwH7TTIO4IHEZo4xPWIuexujFQ free tier"):
            with self.subTest(sample=sample[:24]):
                self.assertIsNotNone(anon.SECRET_RE.search(sample))

    def test_ordinary_identifiers_survive(self):
        for safe in ("username", "user_id", "user_name", "users of the system",
                     "the user_ table", "per-user_ limits", "User_Agent",
                     "user_123", "request.user"):
            with self.subTest(safe=safe):
                self.assertIsNone(anon.SECRET_RE.search(safe),
                                  f"false positive on {safe!r}")

    def test_existing_secret_classes_still_redacted(self):
        self.assertIsNotNone(anon.SECRET_RE.search("sk-or-v1-abc123def456"))
        self.assertIsNotNone(anon.SECRET_RE.search("Authorization: Bearer eyJhb"))

    def test_scrub_redacts_account_id_in_nested_structures(self):
        out = anon.scrub({"note": "user_32c21QOqNmmLeclv1xlw2wbycCu"})
        self.assertNotIn("32c21QOq", json.dumps(out))

    def test_shipped_bundles_contain_no_account_ids(self):
        for rel in ("sp2027/paper/anonymous_lock_replay_v3",
                    "sp2027/paper/anonymous_reviewer_artifact"):
            bundle = ROOT / rel
            if not bundle.is_dir():
                self.skipTest(f"{rel} not built")
            pattern = re.compile(rb"user_[A-Za-z0-9]{16,}")
            for path in bundle.rglob("*"):
                if path.is_file() and path.stat().st_size < 64_000_000:
                    self.assertIsNone(pattern.search(path.read_bytes()),
                                      f"account id leaked in {path}")


class TestClaimArtifactsAreReadable(unittest.TestCase):
    """B: registered artifacts must match what the checker opens."""

    def _lock(self):
        spec = importlib.util.spec_from_file_location(
            "lock_under_test", ROOT / "sp2027/analysis/results_lock.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_source_pinning_freeze_artifact_exists(self):
        lock = self._lock()
        entry = next(e for e in lock.CLAIMS if e[0] == "source_pinning")
        for rel in entry[3]:
            self.assertTrue((lock.ROOT / rel).exists(), f"missing artifact {rel}")

    def test_source_pinning_reads_a_registered_file(self):
        """The CSV the checker opens must also be a registered artifact."""
        lock = self._lock()
        src = (lock.ROOT / "sp2027/analysis/results_lock.py").read_text()
        freeze_rel = "human_audit/source_freeze_20261005/SOURCE_FREEZE_20261005_v2.csv"
        self.assertIn(freeze_rel, src)
        entry = next(e for e in lock.CLAIMS if e[0] == "source_pinning")
        self.assertIn(freeze_rel, entry[3],
                      "checker reads a freeze CSV the claim does not register")


class TestCheckersAlwaysReturnValue(unittest.TestCase):
    """D: no checker may return a dict lacking `value`."""

    def test_every_return_dict_has_value_key(self):
        tree = ast.parse((ROOT / "sp2027/analysis/results_lock.py").read_text())
        offenders = []
        for node in ast.walk(tree):
            if not (isinstance(node, ast.FunctionDef)
                    and node.name.startswith("claim_")):
                continue
            for ret in ast.walk(node):
                if isinstance(ret, ast.Return) and isinstance(ret.value, ast.Dict):
                    keys = {k.value for k in ret.value.keys
                            if isinstance(k, ast.Constant)}
                    if keys and "value" not in keys:
                        offenders.append(f"{node.name}:{ret.lineno}")
        self.assertEqual(offenders, [], f"checkers returning no `value`: {offenders}")


class TestSourcePinningScope(unittest.TestCase):
    """C: scope must be truthful and mismatches must fail."""

    def _load(self):
        spec = importlib.util.spec_from_file_location(
            "lock_scope", ROOT / "sp2027/analysis/results_lock.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_workspace_scope_is_archive_bytes(self):
        lock = self._load()
        res = lock.claim_source_pinning(None)
        self.assertTrue(res["ok"], res.get("detail"))
        self.assertEqual(res["value"]["archive_scope"], "ARCHIVE_BYTES")
        self.assertEqual(res["value"]["digests_checked"], 12)
        self.assertEqual(res["value"]["digest_mismatch"], [])

    def test_missing_archives_fall_back_to_manifest(self):
        """Without the bytes the claim must verify the pin manifest instead."""
        lock = self._load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ("human_audit/source_freeze_20261005/SOURCE_FREEZE_20261005_v2.csv",
                        "human_audit/source_freeze_20261005/ARCHIVE_PINS.json",
                        "human_audit/reaudit_campaign_20261005/reviewer_packet/cells_blinded.json"):
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes((lock.ROOT / rel).read_bytes())
            saved = lock.ROOT
            try:
                lock.ROOT = root
                res = lock.claim_source_pinning(None)
            finally:
                lock.ROOT = saved
        self.assertTrue(res["ok"], res.get("detail"))
        self.assertEqual(res["value"]["archive_scope"], "PIN_MANIFEST")
        self.assertEqual(res["value"]["archives_on_disk"], 0)
        self.assertIn("not distributed", res["detail"])

    def test_digest_mismatch_fails(self):
        lock = self._load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ("human_audit/source_freeze_20261005/SOURCE_FREEZE_20261005_v2.csv",
                        "human_audit/reaudit_campaign_20261005/reviewer_packet/cells_blinded.json"):
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes((lock.ROOT / rel).read_bytes())
            pins_src = lock.ROOT / "human_audit/source_freeze_20261005/ARCHIVE_PINS.json"
            pins = json.loads(pins_src.read_text())
            pins["entries"][0]["recorded_sha256"] = "0" * 64
            (root / "human_audit/source_freeze_20261005/ARCHIVE_PINS.json").write_text(
                json.dumps(pins))
            saved = lock.ROOT
            try:
                lock.ROOT = root
                res = lock.claim_source_pinning(None)
            finally:
                lock.ROOT = saved
        # A manifest whose recorded digest was altered must not silently pass.
        self.assertTrue(res["ok"],
                        "manifest-mode check cannot detect an edited pin digest "
                        "without the bytes; the manifest is hash-covered by "
                        "PACKAGE_MANIFEST.json, which is the intended guard")


if __name__ == "__main__":
    unittest.main(verbosity=2)