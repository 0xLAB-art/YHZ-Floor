#!/usr/bin/env python3
"""Independent generator-side truth adjudicator for Experiment B (IAR-B).

CLI: python3 eb_adjudicator.py <public_dir> <private_dir> <trust_path>
Prints one JSON line:
  {system, malformed, supported, truth_strong, crypto_ok, cred}
and always exits 0.

Truth model (independent of V1/V2/V3-sig/V3-full):

- Structural, parse, or declared-hash failures short-circuit with
  malformed=True, supported=0, crypto_ok=False, truth_strong=False.
  Broken bundles are not re-judged cryptographically.
- Record authenticity is established with Ed25519 signatures under the
  trust anchor. A forged or foreign signature does NOT make a bundle
  malformed: it fails the rung ladder at the affected rung.
- supported = longest consecutive rung 1..6 whose conditions hold, where
  every rung additionally corroborates against the private run registry
  and target map (never visible to the validators).
- truth_strong = supported == 6 and crypto_ok and not malformed.
"""
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eb_crypto  # noqa: E402

LEVELS = [
    "artifact_authorship",
    "execution_identity",
    "target_effect",
    "reference_oracle_acceptance",
    "boundary_enforcement",
    "attribution",
]
STRONG = {
    "artifact_authorship": "PROVEN",
    "execution_identity": "PROVEN",
    "target_effect": "OBSERVED",
    "reference_oracle_acceptance": "ACCEPTED",
    "boundary_enforcement": "PROVEN",
    "attribution": "PROVEN",
}


def blob(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode()


def hobj(obj):
    return hashlib.sha256(blob(obj)).hexdigest()


def sha_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def de_inst(obj):
    """Reverse eb_fixtures.ser_inst: decode top-level {"__hex__": ...} values."""
    out = {}
    for key, val in obj.items():
        if isinstance(val, dict) and "__hex__" in val:
            out[key] = bytes.fromhex(val["__hex__"])
        else:
            out[key] = val
    return out


def gg(d, *names):
    cur = d
    for name in names:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(name)
    return cur


def _eq_all(*vals):
    return all(v is not None for v in vals) and all(v == vals[0] for v in vals)


def out(res):
    print(json.dumps(res, sort_keys=True))
    return 0


def main():
    if len(sys.argv) != 4:
        return out(
            {
                "system": "eb-adjudicator",
                "malformed": True,
                "supported": 0,
                "truth_strong": False,
                "crypto_ok": False,
                "cred": None,
            }
        )
    pub = Path(sys.argv[1])
    priv = Path(sys.argv[2])
    trust = Path(sys.argv[3])

    res = {
        "system": "eb-adjudicator",
        "malformed": False,
        "supported": 0,
        "truth_strong": False,
        "crypto_ok": False,
        "cred": None,
    }

    try:
        cert = json.loads((pub / "certificate.json").read_text())
        req = json.loads((pub / "request.json").read_text())
        cand = json.loads((pub / "candidate.json").read_text())
        json.loads((pub / "target.json").read_text())
        reg = json.loads((priv / "run_registry.json").read_text())["runs"]
        tmap = json.loads((priv / "targets.json").read_text())["targets"]
        keys = json.loads(trust.read_text())["keys"]
    except Exception:
        res["malformed"] = True
        return out(res)

    res["cred"] = gg(cert, "execution", "session_id")

    present = {}
    authentic = {}
    try:
        items = cert.get("evidence", [])
        if not items:
            raise ValueError("no evidence")
        for item in items:
            kind = item.get("kind")
            rel = item.get("path", "")
            fp = pub / rel
            if not fp.exists():
                raise ValueError("missing evidence file")
            if sha_file(fp) != item.get("sha256"):
                raise ValueError("evidence hash mismatch")
            rec = json.loads(fp.read_text())
            present[kind] = rec
            authentic[kind] = False
            sp = pub / (rel + ".sig")
            if sp.exists():
                session = rec.get("session_id")
                if session in keys:
                    try:
                        Ed25519PublicKey.from_public_bytes(
                            bytes.fromhex(keys[session])
                        ).verify(
                            bytes.fromhex(sp.read_text().strip()),
                            bytes.fromhex(hobj(rec)),
                        )
                        authentic[kind] = True
                    except Exception:
                        pass
    except Exception:
        res["malformed"] = True
        return out(res)

    cred = res["cred"]
    sha_cand = sha_file(pub / "candidate.json")
    sha_tgt = sha_file(pub / "target.json")

    reg_by = {}
    for r in reg:
        reg_by.setdefault(r.get("session_id"), r)
    run = reg_by.get(cred)

    aa = present.get("agent_artifact", {})
    tr = present.get("execution_trace", {})
    ef = present.get("target_effect", {})
    rf = present.get("reference_acceptance", {})
    bd = present.get("boundary", {})
    md = present.get("verifier_metadata", {})
    ca = cert.get("agent_artifact", {})
    ex = cert.get("execution", {})
    claimed = req.get("claimed", {})

    l1 = bool(
        authentic.get("agent_artifact")
        and aa.get("session_id") == cred
        and aa.get("artifact_sha256") == sha_cand
        and ca.get("sha256") == sha_cand
        and ca.get("session_id") == cred
        and run is not None
        and run.get("candidate_sha256") == sha_cand
    )
    l2 = bool(
        l1
        and authentic.get("execution_trace")
        and tr.get("session_id") == cred
        and tr.get("candidate_sha256") == sha_cand
        and ex.get("executor") == tr.get("executor")
    )
    l3 = bool(
        l2
        and authentic.get("target_effect")
        and ef.get("session_id") == cred
        and ef.get("status") == "OBSERVED"
        and run.get("effect_status") == "OBSERVED"
    )
    l4 = bool(
        l3
        and authentic.get("reference_acceptance")
        and rf.get("session_id") == cred
        and rf.get("accepted") is True
        and rf.get("artifact_sha256") == sha_cand
        and run.get("reference_accepted") is True
    )
    l5 = bool(
        l4
        and authentic.get("boundary")
        and bd.get("session_id") == cred
        and bd.get("enforced") is True
    )
    l6 = bool(
        l5
        and authentic.get("verifier_metadata")
        and md.get("session_id") == cred
        and md.get("verifier_version")
        == gg(cert, "verification", "verifier_version")
        and _eq_all(
            tr.get("base_instance_id"),
            gg(cert, "task", "base_instance_id"),
            claimed.get("base_instance_id"),
        )
        and _eq_all(
            claimed.get("condition_id"),
            gg(cert, "condition", "id"),
            tr.get("condition_id"),
            ef.get("condition_id"),
        )
        and _eq_all(
            gg(claimed, "target_hashes", "artifact_sha256"),
            gg(cert, "target", "artifact_sha256"),
            sha_tgt,
        )
        and _eq_all(claimed.get("run_id"), cred)
        and gg(cert, "execution", "trace_hash")
        == sha_file(pub / "evidence" / "execution_trace.json")
        and run.get("condition_id") == claimed.get("condition_id")
        and run.get("base_instance_id") == claimed.get("base_instance_id")
    )

    supported = 0
    for rung in (l1, l2, l3, l4, l5, l6):
        if rung:
            supported += 1
        else:
            break
    res["supported"] = supported

    tid = gg(cert, "target", "target_id")
    if tid in tmap:
        try:
            ok, _details = eb_crypto.predicate(de_inst(tmap[tid]), cand)
            res["crypto_ok"] = bool(ok)
        except Exception:
            res["crypto_ok"] = False

    res["truth_strong"] = bool(
        supported == 6 and res["crypto_ok"] and not res["malformed"]
    )
    return out(res)


if __name__ == "__main__":
    sys.exit(main())
