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
    q = base64.b64encode(fprev + targ).decode()
    print(json.dumps({'q': q}), flush=True)
    line = sys.stdin.readline()
    obj = json.loads(line)
    return bool(obj.get('pad_ok'))
t_start = time.monotonic_ns()
recovered = bytearray()
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
                    ok2 = oracle_q(bytes(chk), targ)
                    if not ok2:
                        continue
                found = g
                break
        inter[i] = found ^ pad
    prev = prevs[bi]
    plain_block = bytes(inter[k] ^ prev[k] for k in range(16))
    recovered.extend(plain_block)
t_end = time.monotonic_ns()
pt_hex = recovered.hex()
print('OPSPAN_NS:' + str(t_end - t_start), flush=True)
print('CLAIM:' + json.dumps({'plaintext_hex': pt_hex}), flush=True)