import sys
import json
import base64
import time
ct_hex = '2d8b1cf4a1462301d00db3524eaf30099264d96a23b7c2bd66715a3f32a6fcc4605c8bb0295d378dc2a41302274f62053bfa614a884a4dd598ca28fc61ee743f52bb56f89ad884d9238b15549ee55a28'
iv_hex = '2ceef434f762d4c6ba315182c44368df'
def oracle(prev,tgt):
    payload = base64.b64encode(prev+tgt).decode()
    qline = json.dumps({'q':payload},separators=(',',':'))
    print(qline,flush=True)
    r = sys.stdin.readline()
    sys.stderr.write('got reply\n')
    sys.stderr.flush()
    if not r:
        raise RuntimeError('eof2')
    return json.loads(r).get('pad_ok') is True
def dec_block(tgt):
    inter = bytearray(16)
    forged = bytearray(16)
    for pos in range(15,-1,-1):
        pad = 16-pos
        for j in range(pos+1,16):
            forged[j] = inter[j]^pad
        hit = None
        for g in range(256):
            forged[pos] = g
            if oracle(bytes(forged),tgt):
                if pad == 1:
                    forged[14] ^= 1
                    ok2 = oracle(bytes(forged),tgt)
                    forged[14] ^= 1
                    if not ok2:
                        continue
                hit = g
                break
        if hit is None:
            raise RuntimeError('nohit')
        inter[pos] = hit^pad
    return bytes(inter)
t0 = time.monotonic_ns()
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blks = [ct[i:i+16] for i in range(0,len(ct),16)]
prevs = [iv]+blks[:-1]
pt = b''
for idx in range(len(blks)):
    I = dec_block(blks[idx])
    P = bytes(a^b for a,b in zip(I,prevs[idx]))
    pt = pt+P
t1 = time.monotonic_ns()
pad = pt[-1]
if 1 <= pad <= 16:
    ok = True
    for k in range(1,pad+1):
        if pt[-k] != pad:
            ok = False
    if ok:
        pt = pt[:-pad]
print('OPSPAN_NS:'+str(t1-t0),flush=True)
print('CLAIM:'+json.dumps({'plaintext_hex':pt.hex()},separators=(',',':')),flush=True)