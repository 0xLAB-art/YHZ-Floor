import sys
import base64
import json
import time
import select
ct_hex = '503a132d9717d2cd67abfe0b68d00655d235ab309beccfad6ffecae446e62ed2d881ebf673b773d9e24eeed0155c2e9ba8cd2f35a6fa33182e181a72e353ad027d411c5b7b68b2c332c58f5a3356d26a'
iv_hex = 'f4ce10ffb43862b7ee606f2777954b0d'
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
targets = blocks[:4]
prevs = [iv] + blocks[:3]
qcount = [0]
def ask(fprev, tgt):
 s = base64.b64encode(fprev + tgt).decode()
 print(json.dumps({'q': s}), flush=True)
 qcount[0] += 1
 if qcount[0] % 500 == 0:
  print('progress ' + str(qcount[0]), file=sys.stderr)
 r, _, _ = select.select([sys.stdin], [], [], 15)
 if not r:
  print('stdin timeout', file=sys.stderr)
  raise RuntimeError('stdin timeout')
 line = sys.stdin.readline()
 if not line:
  print('eof', file=sys.stderr)
  raise RuntimeError('eof')
 o = json.loads(line)
 return bool(o.get('pad_ok'))
def recover(tgt):
 inter = [0]*16
 forged = bytearray(16)
 for pos in range(15, -1, -1):
  pad = 16 - pos
  for k in range(pos+1, 16):
   forged[k] = inter[k] ^ pad
  for k in range(pos):
   forged[k] = 0
  found = -1
  for guess in range(256):
   forged[pos] = guess
   ok = ask(bytes(forged), tgt)
   if ok:
    if pos == 15:
     saved = forged[14]
     forged[14] = saved ^ 1
     ok2 = ask(bytes(forged), tgt)
     forged[14] = saved
     if not ok2:
      continue
    inter[pos] = guess ^ pad
    found = guess
    break
  if found < 0:
   print('fail pos ' + str(pos), file=sys.stderr)
   raise RuntimeError('fail')
 return bytes(inter)
t0 = time.monotonic_ns()
pt = b''
for idx, tgt in enumerate(targets):
 print('block ' + str(idx), file=sys.stderr)
 inter = recover(tgt)
 p = bytes([inter[j] ^ prevs[idx][j] for j in range(16)])
 pt += p
 print('block done ' + p.hex(), file=sys.stderr)
t1 = time.monotonic_ns()
print('OPSPAN_NS:' + str(t1 - t0), flush=True)
print('CLAIM:' + json.dumps({'plaintext_hex': pt.hex()}), flush=True)