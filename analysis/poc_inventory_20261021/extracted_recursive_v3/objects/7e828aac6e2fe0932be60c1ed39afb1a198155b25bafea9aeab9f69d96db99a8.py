import sys
import json
import base64
import time
ct_hex = 'c5a9f76cdf6d777cf8270c08b230696fe4a7c46ad244182061b8e29639c835339f90e9c0cd01ccff1e5f384a2f2a606a8b73736bee8cf80fb6c239602f0e751bd6a841c5d4779f5f4f747a65bb711e0a'
iv_hex = 'efd6f1db6c0c2623f75f8d4b586b4c16'
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
def oracle_q(fprev, targ):
    b64 = base64.b64encode(fprev + targ).decode()
    print(json.dumps({'q': b64}, separators=(',', ':')), flush=True)
    line = sys.stdin.readline()
    obj = json.loads(line)
    return bool(obj.get('pad_ok'))
t0 = time.monotonic_ns()
rec = bytearray()
for bi in range(len(blocks)):
    targ = blocks[bi]
    inter = bytearray(16)
    forged = bytearray(16)
    for i in range(15, -1, -1):
        pad = 16 - i
        for j in range(i+1, 16):
            forged[j] = inter[j] ^ pad
        found = None
        for g in range(256):
            forged[i] = g
            ok = oracle_q(bytes(forged), targ)
            if ok:
                if pad == 1:
                    chk = bytearray(forged)
                    chk[14] ^= 1
                    b64c = base64.b64encode(bytes(chk) + targ).decode()
                    print(json.dumps({'q': b64c}, separators=(',', ':')), flush=True)
                    line2 = sys.stdin.readline()
                    ok2 = bool(json.loads(line2).get('pad_ok'))
                    if not ok2:
                        continue
                found = g
                break
        inter[i] = found ^ pad
    prev = prevs[bi]
    pb = bytes(inter[k] ^ prev[k] for k in range(16))
    rec.extend(pb)
t1 = time.monotonic_ns()
print('OPSPAN_NS:' + str(t1 - t0), flush=True)
print('CLAIM:' + json.dumps({'plaintext_hex': rec.hex()}, separators=(',', ':')), flush=True)