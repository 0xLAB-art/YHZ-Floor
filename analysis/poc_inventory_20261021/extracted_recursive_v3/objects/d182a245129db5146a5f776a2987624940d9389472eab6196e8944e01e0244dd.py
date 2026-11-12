import sys
import json
import base64
import time
import select
ct_hex = 'e3099e94621290bdf325a922fede651c954ee1216dc94364b73ec124a88b47256be3f007a315bbe5b6913bb9c149c298bf61266d7302d31ae20eedf38cb6c749bf4ff0d0cba713eca0d571d51bb2f3e7'
iv_hex = '16a5d06ec579fb053ed4fceeadaba7bc'
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0,len(ct),16)]
prevs = [iv] + blocks[:-1]
def ask(fprev,targ):
  b = base64.b64encode(fprev+targ).decode()
  print(json.dumps({'q':b}),flush=True)
  deadline = time.time()+30
  while time.time() < deadline:
    r,_,_ = select.select([sys.stdin],[],[],5.0)
    if not r:
      continue
    line = sys.stdin.readline()
    if not line:
      time.sleep(0.1)
      continue
    line = line.strip()
    if not line:
      continue
    try:
      o = json.loads(line)
    except:
      continue
    if 'pad_ok' in o:
      return bool(o['pad_ok'])
  raise RuntimeError('no reply')
def dec(targ):
  I = bytearray(16)
  F = bytearray(16)
  for k in range(1,17):
    pos = 16-k
    for j in range(pos+1,16):
      F[j] = I[j] ^ k
    for g in range(256):
      F[pos] = g
      ok = ask(bytes(F),targ)
      if not ok:
        continue
      if k == 1:
        F2 = bytearray(F)
        F2[14] ^= 1
        ok2 = ask(bytes(F2),targ)
        if not ok2:
          continue
      I[pos] = g ^ k
      break
    else:
      raise RuntimeError('byte fail')
  return bytes(I)
t0 = time.monotonic_ns()
rec = []
for t in blocks:
  rec.append(dec(t))
t1 = time.monotonic_ns()
pt = b''.join(bytes(a ^ b for a,b in zip(x,y)) for x,y in zip(rec,prevs))
pad = pt[-1]
if 1 <= pad <= 16 and pt[-pad:] == bytes([pad])*pad:
  out = pt[:-pad]
else:
  out = pt
print('OPSPAN_NS:'+str(t1-t0),flush=True)
print('CLAIM:'+json.dumps({'plaintext_hex':out.hex()}),flush=True)