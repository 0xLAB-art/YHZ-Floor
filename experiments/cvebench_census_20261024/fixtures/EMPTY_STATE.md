# FIXTURES — explicit empty state

No fixture material was instantiated in this phase. The R0/RT representation
machinery (R0 canonical statement + verbatim artifacts; RT base64-encoded
artifacts with an explicit decode note) is **hash-referenced** from
`external_admission_20261024/` per the phase instruction:

- `fixtures/rt_transform/build_representations.py`
  sha256 `5b12a85329539053eb5bd7f4539c7bfe27910cba39d53cee3379c2d5756a649e`
- `fixtures/rt_transform/verify_decode_equality.py`
  sha256 `27d2263fadf50aeca2965b79f51e28f5a06afd4bfbbc79cfcfa1089c5b8e4cc0`

Both were recomputed this phase with `sha256sum` and match the values recorded
in that namespace's `FREEZE.json` exactly (`ARCHIVE_VERIFICATION.json` carries
the verification).

## Why no fixtures exist

The conditional grid never instantiated: 0 of 40 pinned CVE-Bench tasks qualify
(`TASK_SELECTION.md`, `selection/census.json`), so there is no task set to
build R0/RT fixtures for, no prompts to instantiate, and no decode-equality
gate to run.

## Decode-equality gate status

**NOT INSTANTIATED** (vacuously nothing to decode). This differs from a gate
failure and from Phase 2's PASS: no representation pair was ever constructed,
so the hard gate had no input. Had the grid run, the gate would have been
mandatory before any generation, per the frozen Phase-2 semantics.
