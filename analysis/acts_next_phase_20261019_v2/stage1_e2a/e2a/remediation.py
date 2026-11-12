"""Loader for the *audited* HEB-1 remediation primitives.

The E2A contract deliberately reuses the existing, reviewed remediation
components instead of re-implementing them:

* ``sp2027/analysis/heb1_remediation_v1/signing/protected_signing.py``
* ``sp2027/analysis/heb1_remediation_v1/context/context_validator.py``

They are loaded by absolute path so that the remediation tree is never
modified, re-packaged, or shadowed by a local copy.  Nothing in this module
changes the behaviour of the loaded code.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
STAGE1_ROOT = HERE.parent
ANALYSIS_ROOT = STAGE1_ROOT.parents[1]
REMEDIATION_ROOT = ANALYSIS_ROOT / "heb1_remediation_v1"

PROTECTED_SIGNING_PATH = REMEDIATION_ROOT / "signing" / "protected_signing.py"
CONTEXT_VALIDATOR_PATH = REMEDIATION_ROOT / "context" / "context_validator.py"

# The three trusted issuer roles.  The canonical strings live in ``canonical``
# (the single definition of the contract's constants); they are re-exported
# here because the signing / policy code refers to roles alongside the audited
# components loaded below.
from .canonical import ROLE_AGGREGATOR, ROLE_OBSERVER, ROLE_REFERENCE  # noqa: E402

# The frozen Stage 01 components.  Never modified, never re-implemented.
STAGE01_VALIDATOR_PATH = ANALYSIS_ROOT / "contract_sound_stage01_validator_v2.py"
STAGE01_REFERENCE_PATH = ANALYSIS_ROOT / "contract_sound_stage01_reference_verifier_v2.py"
STAGE01_GENERATOR_PATH = ANALYSIS_ROOT / "run_contract_sound_stage01.py"
STAGE01_PILOT_PATH = ANALYSIS_ROOT / "run_contract_sound_agent_pilot.py"

_CACHE: dict[str, ModuleType] = {}


def _load(name: str, path: Path) -> ModuleType:
    if name in _CACHE:
        return _CACHE[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    # Register the module in ``sys.modules`` *before* executing it.  The
    # audited context validator defines a dataclass; ``dataclasses`` resolves
    # string annotations and ClassVar detection through
    # ``sys.modules[cls.__module__]``, which raises ``AttributeError`` if the
    # module was never registered.  Registration does not alter the loaded
    # code's behaviour.
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    _CACHE[name] = module
    return module


def protected_signing() -> ModuleType:
    """The audited Ed25519 issuer / signed-record utility."""
    return _load("heb1_protected_signing", PROTECTED_SIGNING_PATH)


def context_validator() -> ModuleType:
    """The audited signed-context validator and explicit replay ledger."""
    return _load("heb1_context_validator", CONTEXT_VALIDATOR_PATH)


def manifest_verifier() -> ModuleType:
    """The audited fail-closed integrity manifest verifier."""
    return _load("heb1_manifest_verifier", REMEDIATION_ROOT / "integrity" / "manifest_verifier.py")


def stage01_generator() -> ModuleType:
    """The frozen Stage 01 target generator (``make_ecdsa`` / ``make_chacha``)."""
    return _load("acts_stage01_generator", STAGE01_GENERATOR_PATH)


def load_policy(policy_path: Path):
    """Build an audited ``IssuerPolicy`` from the frozen policy document."""
    signing = protected_signing()
    document = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    roles = {
        role: {"kinds": tuple(spec["kinds"]), "contexts": tuple(spec["contexts"])}
        for role, spec in document["roles"].items()
    }
    return signing.IssuerPolicy(roles=roles), document


def public_key_for_role(bundle_path: Path, role: str):
    """Return the Ed25519 public key object for *role* from the public bundle."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    bundle = json.loads(Path(bundle_path).read_text(encoding="utf-8"))
    for issuer in bundle["issuers"]:
        if issuer["role"] == role:
            return Ed25519PublicKey.from_public_bytes(bytes.fromhex(issuer["public_key_hex"]))
    raise KeyError(f"no issuer with role {role!r} in {bundle_path}")
