import sys
import json
import base64
import time
ct_hex = '0bc75d95fe2fe3b9e1feb1f0055ac54707d97e2ee7047ab2231c99989c87863fcb38a303735eabe45f290daca391e12a9835b119fc67aeff84f2132119c894d87ce3ab47ea5ea6f8661ee21e525f97db'
iv_hex = 'b7b3bb5d750f25a72ea603313b243455'
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
nblocks = len(ct) // 16
blocks = [ct[i*16:(i+1)*16] for i in range(nblocks)]
prevs = [iv] + blocks[:-1]
def query(forged_prev, target):
  data = forged_prev + target
  b64 = base64.b64encode(data).decode('ascii')
  sys.stdout.write(json.dumps({'q': b64}) + chr(10))
  sys.stdout.flush()
  line = sys.stdin.readline()
  obj = json.loads(line)
  return bool(obj.get('pad_ok', False))
intermediates = []
t0 = time.monotonic_ns()
for bi in range(nblocks):
  target = blocks[bi]
  inter = bytearray(16)
  forged = bytearray(16)
  for pad_len in range(1, 17):
    for k in range(1, pad_len):
      forged[16-k] = inter[16-k] ^ pad_len
    pos = 16 - pad_len
    found = None
    for guess in range(256):
      forged[pos] = guess
      ok = query(bytes(forged), target)
      if ok:
        if pad_len == 1:
          forged2 = bytearray(forged)
          forged2[14] ^= 1
          data2 = bytes(forged2) + target
          b642 = base64.b64encode(data2).decode('ascii')
          sys.stdout.write(json.dumps({'q': b642}) + chr(10))
          sys.stdout.flush()
          line2 = sys.stdin.readline()
          obj2 = json.loads(line2)
          ok2 = bool(obj2.get('pad_ok', False))
          if ok2:
            found = guess
            break
          else:
            continue
        else:
          found = guess
          break
    inter[pos] = found ^ pad_len
  intermediates.append(bytes(inter))
t1 = time.monotonic_ns()
pt = b''.join([bytes([intermediates[i][j] ^ prevs[i][j] for j in range(16)]) for i in range(nblocks)])
pad_len = pt[-1]
if 1 <= pad_len <= 16 and pt[-pad_len:] == bytes([pad_len]) * pad_len:
  pt_unpadded = pt[:-pad_len]
else:
  pt_unpadded = pt
pt_hex = pt_unpadded.hex()
sys.stdout.write('OPSPAN_NS:' + str(t1 - t0) + chr(10))
sys.stdout.flush()
sys.stdout.write('CLAIM:' + json.dumps({'plaintext_hex': pt_hex}) + chr(10))
sys.stdout.flush()