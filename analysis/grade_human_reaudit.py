#!/usr/bin/env python3
"""Validate committed human rating submissions; never synthesize judgments."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RATINGS = {"yes", "partial", "no", "opaque"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO UTC string")
    timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timestamp.tzinfo is None or timestamp.utcoffset().total_seconds() != 0:
        raise ValueError("rating and commitment timestamps must be UTC")
    if timestamp > datetime.now(timezone.utc):
        raise ValueError("future-dated judgment or commitment")
    return timestamp


def load_ratings(path, declaration, packet_path, expected):
    if not isinstance(declaration, dict):
        raise ValueError("rater declaration must be a JSON object")
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["cell_id", "rating", "evidence_pointer", "rationale", "judged_utc"]:
            raise ValueError("rating CSV columns must match the frozen template")
        rows = list(reader)
    identifiers = [row.get("cell_id") for row in rows]
    if len(identifiers) != len(set(identifiers)) or set(identifiers) != set(expected):
        raise ValueError("rating inventory must contain each of the 54 packet cells exactly once")
    if len(rows) != 54:
        raise ValueError("requires exactly 54 judgments")
    judged = []
    for row in rows:
        if None in row:
            raise ValueError("unexpected CSV columns in a judgment")
        if row.get("rating") not in RATINGS:
            raise ValueError("blank or invalid rating; no agreement statistic can be computed")
        for key in ("evidence_pointer", "rationale", "judged_utc"):
            if not (row.get(key) or "").strip():
                raise ValueError("missing judgment provenance: " + key)
        judged.append(utc(row["judged_utc"]))
    if (declaration.get("rater_kind") != "human"
            or declaration.get("independently_completed") is not True
            or declaration.get("used_ai_for_judgments") is not False
            or not isinstance(declaration.get("rater_id"), str)
            or not declaration["rater_id"].strip()
            or not isinstance(declaration.get("prior_exposure"), str)
            or not declaration["prior_exposure"].strip()):
        raise ValueError("requires a completed human-rater declaration and exposure disclosure")
    if (declaration.get("ratings_sha256") != digest(path)
            or declaration.get("packet_sha256") != digest(packet_path)):
        raise ValueError("declaration is not bound to these exact rating and packet bytes")
    if utc(declaration.get("committed_utc", "")) < max(judged):
        raise ValueError("commitment precedes a judgment")
    return {row["cell_id"]: row["rating"] for row in rows}


def agreement(first, second):
    if set(first) != set(second) or not first:
        raise ValueError("agreement requires matching nonempty cell inventories")
    size = len(first)
    matched = sum(first[key] == second[key] for key in first)
    a, b = Counter(first.values()), Counter(second.values())
    observed = matched / size
    expected = sum(a[value] * b[value] for value in RATINGS) / size ** 2
    return {"cells": size, "agreements": matched, "raw_agreement": observed,
            "cohen_kappa": ((observed - expected) / (1 - expected) if expected < 1 else None),
            "kappa_undefined": expected == 1,
            "disagreements": [key for key in sorted(first) if first[key] != second[key]]}


def grade(packet_path, first_path, first_declaration, second_path, second_declaration):
    inputs = {"packet": packet_path, "ratings_A": first_path, "ratings_B": second_path,
              "declaration_A": first_declaration, "declaration_B": second_declaration}
    original_digests = {key: digest(path) for key, path in inputs.items()}
    if first_path.resolve() == second_path.resolve():
        raise ValueError("cannot treat one file as two independent submissions")
    packet = json.loads(packet_path.read_text())
    cells = packet["cells_order"]
    if len(cells) != 54 or len(set(cells)) != 54 or packet.get("n_cells") != 54:
        raise ValueError("invalid 54-cell packet")
    declarations = [json.loads(path.read_text()) for path in (first_declaration, second_declaration)]
    if any(not isinstance(item, dict) for item in declarations):
        raise ValueError("each rater declaration must be a JSON object")
    if declarations[0].get("rater_id") == declarations[1].get("rater_id"):
        raise ValueError("requires two distinct declared raters")
    first = load_ratings(first_path, declarations[0], packet_path, cells)
    second = load_ratings(second_path, declarations[1], packet_path, cells)
    if any(digest(path) != original_digests[key] for key, path in inputs.items()):
        raise ValueError("committed input changed during analysis")
    return {"schema": "committed-rating-agreement/1", "pre_adjudication": True,
            "input_sha256": original_digests,
            "statistics": agreement(first, second),
            "human_identity_and_independence_verified": False,
            "boundary": "Statistics on submitted judgments with self-declared human provenance; declarations and timestamps alone do not prove identity, blinding, or independence."}


def main():
    parser = argparse.ArgumentParser()
    for name in ("packet", "ratings-a", "declaration-a", "ratings-b", "declaration-b", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite a prior human-rating analysis")
    try:
        result = grade(args.packet, args.ratings_a, args.declaration_a, args.ratings_b, args.declaration_b)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.error(str(exc))
    with args.output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["statistics"], indent=2))


if __name__ == "__main__":
    main()
