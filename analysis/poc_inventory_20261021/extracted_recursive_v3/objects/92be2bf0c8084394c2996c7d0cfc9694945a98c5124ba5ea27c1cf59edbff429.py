import sys, json, base64, time
ct = bytes.fromhex('1f183c1a58d29333f0a5212c74339c348364861f54bde3f0c64797e9b96609a776e072356f6ee8d40e3b68bd0533113ab194df815b01bc1dbf13717cbeb710d79b1bdb0599aa16a0373e967d8453d560')
iv = bytes.fromhex('c5eeb0ec979b517217fdb6fcfae12d9f')
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
def ask(fp, tg):
  s = base64.b64encode(fp + tg).decode()
  sys.stdout.write(json.dumps({'q': s}) + chr(10))
  sys.stdout.flush()
  ln = sys.stdin.readline()
  if not ln:
    raise RuntimeError('eof')
  return bool(json.loads(ln).get('pad_ok'))
def dec(tg):
  inter = bytearray(16)
  fg = bytearray(16)
  for pl in range(1, 17):
    idx = 16 - pl
    for j in range(idx+1, 16):
      fg[j] = inter[j] ^ pl
    okd = -1
    for g in range(256):
      fg[idx] = g
      if ask(bytes(fg), tg):
        if pl == 1:
          sv = fg[idx-1]
          fg[idx-1] ^= 1
          st = ask(bytes(fg), tg)
          fg[idx-1] = sv
          if not st:
            continue
        okd = g
        break
    if okd < 0:
      raise RuntimeError('nof')
    inter[idx] = okd ^ pl
  return bytes(inter)
t0 = time.monotonic_ns()
pt = b''
for k, tg in enumerate(blocks):
  im = dec(tg)
  pr = prevs[k]
  pt += bytes(a ^ b for a, b in zip(im, pr))
t1 = time.monotonic_ns()
sys.stdout.write('OPSPAN_NS:' + str(t1-t0) + chr(10))
sys.stdout.flush()
sys.stdout.write('CLAIM:' + json.dumps({'plaintext_hex': pt.hex()}) + chr(10))
sys.stdout.flush()