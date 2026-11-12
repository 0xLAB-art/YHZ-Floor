import hashlib
import json
from pathlib import Path

import pytest

from manifest_verifier import PreflightError, preflight_then_execute, verify_manifest


def write_bundle(tmp_path: Path) -> tuple[Path, Path]:
    files = {
        "protocol.md": b"protocol v1\n",
        "runner.py": b"runner\n",
        "component.py": b"component\n",
        "labels.json": b"{}\n",
        "trust.json": b"{}\n",
        "cases/a/request.json": b"a\n",
        "cases/b/request.json": b"b\n",
    }
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def entry(name):
        return {"path": name, "sha256": hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()}

    manifest = {
        "schema": "acts-integrity-remediation/1",
        "protocol": entry("protocol.md"),
        "measurement_runner": entry("runner.py"),
        "components": {"verifier": entry("component.py")},
        "labels_trust": {"labels": entry("labels.json"), "trust": entry("trust.json")},
        "case_inventory": {
            "root": "cases",
            "files": {
                "a/request.json": entry("cases/a/request.json")["sha256"],
                "b/request.json": entry("cases/b/request.json")["sha256"],
            },
            "count": 2,
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path, tmp_path


def test_clean_bundle_passes(tmp_path):
    manifest, root = write_bundle(tmp_path)
    report = verify_manifest(manifest, root)
    assert report.passed
    assert report.checked_files == 7


@pytest.mark.parametrize("mutation", ["tamper", "missing", "unexpected", "escape"])
def test_tamper_and_inventory_defects_fail_closed(tmp_path, mutation):
    manifest, root = write_bundle(tmp_path)
    data = json.loads(manifest.read_text())
    if mutation == "tamper":
        (root / "component.py").write_text("changed\n")
    elif mutation == "missing":
        (root / "trust.json").unlink()
    elif mutation == "unexpected":
        (root / "cases" / "extra.json").write_text("extra\n")
    else:
        data["protocol"]["path"] = "../outside.md"
        manifest.write_text(json.dumps(data))
    report = verify_manifest(manifest, root)
    assert not report.passed
    assert report.errors


def test_preflight_precedes_execution(tmp_path):
    manifest, root = write_bundle(tmp_path)
    (root / "labels.json").write_text("tampered\n")
    called = []
    with pytest.raises(PreflightError):
        preflight_then_execute(manifest, root, lambda: called.append("ran"))
    assert called == []


def test_preflight_allows_execution_after_clean_check(tmp_path):
    manifest, root = write_bundle(tmp_path)
    called = []
    result = preflight_then_execute(manifest, root, lambda: called.append("ran") or 17)
    assert result == 17
    assert called == ["ran"]


def test_symlinked_component_is_rejected(tmp_path):
    manifest, root = write_bundle(tmp_path)
    target = root / "component.py"
    target.unlink()
    (root / "component.py").symlink_to(root / "runner.py")
    report = verify_manifest(manifest, root)
    assert not report.passed
    assert any("symlink" in error for error in report.errors)


@pytest.mark.parametrize("inventory_root", ["/absolute", "../escape", "bad\x00root"])
def test_unsafe_inventory_root_returns_structured_failure(tmp_path, inventory_root):
    manifest, root = write_bundle(tmp_path)
    payload = json.loads(manifest.read_text())
    payload["case_inventory"]["root"] = inventory_root
    manifest.write_text(json.dumps(payload))
    report = verify_manifest(manifest, root)
    assert report.passed is False
    assert isinstance(report.errors, tuple)
    assert report.errors

    called = []
    with pytest.raises(PreflightError):
        preflight_then_execute(manifest, root, lambda: called.append("ran"))
    assert called == []


def test_nonexistent_inventory_root_returns_structured_failure(tmp_path):
    manifest, root = write_bundle(tmp_path)
    payload = json.loads(manifest.read_text())
    payload["case_inventory"]["root"] = "not-present"
    manifest.write_text(json.dumps(payload))
    report = verify_manifest(manifest, root)
    assert report.passed is False
    assert any("missing or not a directory" in error for error in report.errors)


@pytest.mark.parametrize("manifest_bytes", [b"{not-json", b"\xff\xfe\x00\x00"])
def test_malformed_manifest_returns_structured_failure(tmp_path, manifest_bytes):
    manifest, root = write_bundle(tmp_path)
    manifest.write_bytes(manifest_bytes)
    report = verify_manifest(manifest, root)
    assert report.passed is False
    assert report.errors


def test_manifest_io_failure_returns_structured_failure(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    report = verify_manifest(missing, tmp_path)
    assert report.passed is False
    assert report.errors
