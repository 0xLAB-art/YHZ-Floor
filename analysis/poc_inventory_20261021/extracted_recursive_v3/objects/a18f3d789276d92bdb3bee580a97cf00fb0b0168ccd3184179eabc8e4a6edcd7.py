import sys, json, base64, time
ct = bytes.fromhex("925cca7774cccd61f712516d5a187fa6bdb83d3e282f0d4335229e4262bce0a173f1b965d01216bf5a6720bade071bc3483a0e92ce46905729ca99d7a937066009a3684364b5f36ae0273f5e42b44fec")
iv = bytes.fromhex("7ea8ee1a4835aaea44729adcbc475b60")
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
last_dt = [1]
def ask(fprev, tgt):
  p = base64.b64encode(fprev + tgt).decode()
  for _ in range(5):
    print(json.dumps({"q": p}), flush=True)
    line = sys.stdin.readline()
    if line is None or line == "":
      time.sleep(0.2)
      continue
    line = line.strip()
    if not line:
      continue
    try:
      o = json.loads(line)
    except Exception:
      continue
    if "pad_ok" in o:
      return bool(o["pad_ok"])
  raise EOFError("oracle EOF")
def recover(tgt):
  I = bytearray(16)
  f = bytearray(16)
  for pos in range(15, -1, -1):
    pl = 16 - pos
    for k in range(pos+1, 16):
      f[k] = I[k] ^ pl
    hit = None
    for g in range(256):
      f[pos] = g
      t0 = time.monotonic_ns()
      ok = ask(bytes(f), tgt)
      t1 = time.monotonic_ns()
      last_dt[0] = t1 - t0
      if ok:
        if pl == 1:
          f[14] ^= 1
          ok2 = ask(bytes(f), tgt)
          f[14] ^= 1
          if not ok2:
            continue
        hit = g
        break
    if hit is None:
      raise RuntimeError("no pad")
    I[pos] = hit ^ pl
  return bytes(I)
pt = b""
for i, tgt in enumerate(blocks):
  prev = iv if i == 0 else blocks[i-1]
  Im = recover(tgt)
  pt += bytes(a ^ b for a, b in zip(Im, prev))
print("OPSPAN_NS:" + str(int(last_dt[0])), flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": pt.hex()}), flush=True)