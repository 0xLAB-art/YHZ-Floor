#!/usr/bin/env python3
"""Extract the code block from the direct_generator transcript and hash variants
to determine which content was written to generated_agent.py before execution."""
import json, hashlib, re, sys

ROOT = "/mnt/nvme5/ACTS-Attack/sp2027/paper/capability_merge_20261016/artifact_documentation/novelty_program_20261017/surrogate_conversion_20261017_attempt3"
TARGET = "a5e8ed514c5c769b3e4e2dbbdd51ea276c852d11d8145b2f344ca7184f78e399"  # recorded pre-exec snapshot hash

txt = None
with open(f"{ROOT}/surrogate/direct_generator_transcript.jsonl") as f:
    for line in f:
        o = json.loads(line)
        if o.get("type") == "text":
            txt = o["part"]["text"]

print("raw text len:", len(txt))
print("---- RAW HEAD ----")
print(repr(txt[:200]))
print("---- RAW TAIL ----")
print(repr(txt[-200:]))

# Greedy match between CODE_BEGIN and CODE_END
m = re.search(r"CODE_BEGIN(.*?)CODE_END", txt, re.S)
inner = m.group(1) if m else None
print("inner len:", len(inner) if inner else None)

variants = {}
if inner is not None:
    # strip fences
    m2 = re.search(r"```python\n(.*?)```", inner, re.S)
    body = m2.group(1) if m2 else None
    m3 = re.search(r"```\n(.*?)```", inner, re.S)
    body_nolang = m3.group(1) if m3 else None
    if body is not None:
        variants["fence-body"] = body
        variants["fence-body+nl"] = body if body.endswith("\n") else body + "\n"
        variants["fence-body-strip"] = body.strip() + "\n"
    if body_nolang is not None:
        variants["fence-nolang-body"] = body_nolang
    variants["inner-stripped"] = inner.strip()
    variants["inner-stripped+nl"] = inner.strip() + "\n"
    variants["inner-as-is"] = inner
variants["whole-text"] = txt
variants["whole-text+nl"] = txt if txt.endswith("\n") else txt + "\n"

print()
print("TARGET (recorded snapshot):", TARGET)
found = None
for name, v in variants.items():
    h = hashlib.sha256(v.encode()).hexdigest()
    match = "  <<<< MATCH" if h == TARGET else ""
    print(f"{name:24s} {len(v):7d}  {h}{match}")
    if h == TARGET:
        found = name

print()
if found:
    print("MATCH FOUND on variant:", found)
    # write the matching content out for replay testing
    with open("/tmp/opencode/executed_candidate_reconstructed.py", "w") as f:
        f.write(variants[found])
    print("written to /tmp/opencode/executed_candidate_reconstructed.py")
else:
    print("NO VARIANT MATCHES the recorded snapshot hash.")
    # dump the fence body anyway for inspection
    if "fence-body" in variants:
        with open("/tmp/opencode/direct_gen_fence_body.py", "w") as f:
            f.write(variants["fence-body"])
        print("fence body dumped to /tmp/opencode/direct_gen_fence_body.py")

# also show the body itself for inspection if present
if "fence-body" in variants:
    print()
    print("---- FENCE BODY (first 40 lines) ----")
    for i, ln in enumerate(variants["fence-body"].splitlines()[:40], 1):
        print(f"{i:3d}: {ln}")
    print("... total lines:", len(variants["fence-body"].splitlines()))
