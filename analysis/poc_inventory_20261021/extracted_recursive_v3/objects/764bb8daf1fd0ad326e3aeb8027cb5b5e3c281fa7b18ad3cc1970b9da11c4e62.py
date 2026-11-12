import sys, json, base64
ct_hex="4b243d54cf34c7536f17198d96afad3d1422509f96297766e141cb86ddab166476838b2ac8ff3c556284e1b1546eceada6da5afd9b95eecc4bda57c93067f324ca8ecdfdd5d84a3afa0d1cce3ab7d4b6"
iv_hex="7297416ab13274f28a4f3298675178c3"
ct=bytes.fromhex(ct_hex)
forged=bytes(16)
target=ct[0:16]
q=base64.b64encode(forged+target).decode()
sys.stdout.write(json.dumps({"q": q})+"\n")
sys.stdout.flush()
print(f"sent q len={len(forged+target)}", file=sys.stderr, flush=True)
line=sys.stdin.readline()
print(f"got line={repr(line)}", file=sys.stderr, flush=True)
if line:
  obj=json.loads(line)
  ok=bool(obj.get("pad_ok"))
  print(f"pad_ok={ok}", file=sys.stderr, flush=True)
else:
  print("EOF", file=sys.stderr, flush=True)
# dummy claim to see verdict
sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex": "00"*64})+"\n")
sys.stdout.flush()