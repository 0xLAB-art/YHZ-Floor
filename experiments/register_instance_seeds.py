#!/usr/bin/env python3
"""Draw instance seeds from the OS CSPRNG and write a verifiable, append-only receipt.

Why this exists
---------------
Every prior cohort used a hand-declared contiguous block (401-416, 601-616,
701-716, ...). That is a registered *allocation*, not a random draw, so a
reviewer can say the instances were arbitrary and the reps are one instance
repeated. This tool draws seeds from `secrets.randbits` (the OS CSPRNG),
refuses to overwrite an earlier draw, and records a hash over the drawn values
so the draw can be checked after the fact without trusting the log.

Usage
-----
  python3 register_instance_seeds.py --count 24
  python3 register_instance_seeds.py --count 24 --out /tmp/seeds.json
  python3 register_instance_seeds.py --verify seeds_random_20261102T120000Z.json

Contract
--------
* One draw per file. The file name carries the UTC draw time; existing files are
  never overwritten.
* `draw_order` is the order values were produced; `seeds_sorted` is for lookup.
  Cohorts consume the first N of `draw_order`. No reordering, no substitution
  after the first provider call.
* `seeds_sha256` covers `seeds_sorted` canonically, so the receipt can be
  re-verified without the script.
* Disjointness is checked against every `seeds` array already present under
  `research_execution/**/_REGISTRATION.json` and `_LAUNCH.json` — the exclusion
  list is discovered from the record, not hardcoded here.
"""
import argparse
import hashlib
import json
import secrets
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_BITS = 63
RECEIPT_VERSION = "ACTS-INSTANCE-SEED-DRAW-v1"


def canonical(values):
    return json.dumps(sorted(values), separators=(",", ":")).encode()


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def prior_seeds():
    """Every seed already declared in the record, with the file it came from."""
    found, sources = set(), []
    for pattern in ("_REGISTRATION.json", "_LAUNCH.json"):
        for path in HERE.rglob(pattern):
            try:
                doc = json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            seeds = doc.get("seeds")
            if isinstance(seeds, list) and all(isinstance(s, int) for s in seeds):
                found.update(seeds)
                sources.append({
                    "path": str(path.relative_to(HERE)),
                    "count": len(seeds),
                    "min": min(seeds),
                    "max": max(seeds),
                })
    return found, sorted(sources, key=lambda r: r["path"])


def draw(count, bits):
    seen, order = set(), []
    while len(order) < count:
        value = secrets.randbits(bits)
        if value in seen:
            continue
        seen.add(value)
        order.append(value)
    return order


def write_receipt(out, count, bits, order, excluded, sources):
    receipt = {
        "protocol": RECEIPT_VERSION,
        "source": "secrets.randbits (OS CSPRNG: getrandom/urandom)",
        "bit_length": bits,
        "count": count,
        "drawn_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "script": Path(__file__).name,
        "script_sha256": sha256_hex(Path(__file__).read_bytes()),
        "draw_order": order,
        "seeds_sorted": sorted(order),
        "seeds_sha256": sha256_hex(canonical(order)),
        "excluded_prior_seeds": len(excluded),
        "excluded_sources": sources,
        "usage_note": (
            "Consume the first N values of draw_order for N instances. The draw "
            "is fixed at this timestamp and is not re-drawn, reordered or "
            "extended after the first provider call."
        ),
    }
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing draw: {out}")
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def verify(path):
    doc = json.loads(Path(path).read_text())
    order = doc["draw_order"]
    problems = []
    if sorted(order) != doc.get("seeds_sorted"):
        problems.append("seeds_sorted does not match draw_order")
    if len(set(order)) != len(order):
        problems.append("duplicate values in draw_order")
    if sha256_hex(canonical(order)) != doc.get("seeds_sha256"):
        problems.append("seeds_sha256 does not match draw_order")
    excluded, _ = prior_seeds()
    hit = sorted(set(order) & excluded)
    if hit:
        problems.append(f"collides with prior registered seeds: {hit[:8]}")
    print(json.dumps({
        "receipt": str(path),
        "count": len(order),
        "seeds_sha256": doc.get("seeds_sha256"),
        "verified": not problems,
        "problems": problems,
    }, indent=2, sort_keys=True))
    return 0 if not problems else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=24)
    ap.add_argument("--bits", type=int, default=DEFAULT_BITS)
    ap.add_argument("--out", default=None)
    ap.add_argument("--verify", default=None)
    args = ap.parse_args(argv[1:])

    if args.verify:
        return verify(args.verify)

    excluded, sources = prior_seeds()
    order = draw(args.count, args.bits)
    while set(order) & excluded:  # astronomically unlikely; redraw rather than trim
        order = draw(args.count, args.bits)

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out = Path(args.out) if args.out else HERE / f"seeds_random_{stamp}.json"
    receipt = write_receipt(out, args.count, args.bits, order, excluded, sources)

    print(json.dumps({
        "receipt": str(out),
        "count": receipt["count"],
        "bit_length": receipt["bit_length"],
        "seeds_sha256": receipt["seeds_sha256"],
        "first_in_draw_order": receipt["draw_order"][0],
        "prior_seeds_excluded": receipt["excluded_prior_seeds"],
        "prior_sources": len(receipt["excluded_sources"]),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
