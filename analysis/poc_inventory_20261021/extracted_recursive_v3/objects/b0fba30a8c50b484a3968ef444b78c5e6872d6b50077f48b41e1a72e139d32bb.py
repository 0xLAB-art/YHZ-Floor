import sys
import json
import base64
import time
ct_hex = '6ec59a3da460be879c121d4645164ab9baf55839546451f26a5029fe28ea8bc99c0559be9d4bfdb6c9d1cd6cf731359aee1f9347530e39d2ec064a3c0e951d54cc622dc350f25f02e594e1a320412870'
iv_hex = '2df9046dfe1791d1a4199c280ffc3601'
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [iv]
for i in range(0, len(ct), 16):
    blocks.append(ct[i:i+16])
def oracle(fp, tgt):
    payload = base64.b64encode(fp + tgt).decode()
    sys.stdout.write(json.dumps({'q': payload}) + chr(10))
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        obj = json.loads(line)
        return bool(obj.get('pad_ok'))
    except:
        return None
def recover(tgt):
    inter = bytearray(16)
    forged = bytearray(16)
    for pad in range(1, 17):
        pos = 16 - pad
        for k in range(pos + 1, 16):
            forged[k] = inter[k] ^ pad
        found = False
        for g in range(256):
            forged[pos] = g
            r = oracle(bytes(forged), tgt)
            if r is None:
                time.sleep(0.3)
                r = oracle(bytes(forged), tgt)
                if r is None:
                    raise RuntimeError('eof')
            if r:
                if pad == 1 and pos > 0:
                    fb2 = bytearray(forged)
                    fb2[pos - 1] ^= 1
                    r2 = oracle(bytes(fb2), tgt)
                    if r2 is None:
                        raise RuntimeError('eof2')
                    if not r2:
                        continue
                inter[pos] = g ^ pad
                found = True
                break
        if not found:
            raise RuntimeError('nofind')
    return bytes(inter)
time.sleep(0.2)
t0 = time.monotonic_ns()
pts = []
for idx in range(1, len(blocks)):
    im = recover(blocks[idx])
    prev = blocks[idx - 1]
    pt = bytes([a ^ b for a, b in zip(im, prev)])
    pts.append(pt)
    sys.stderr.write('done block ')
    sys.stderr.write(str(idx))
    sys.stderr.write(chr(10))
    sys.stderr.flush()
t1 = time.monotonic_ns()
padded = b''.join(pts)
padlen = padded[len(padded) - 1]
unpadded = padded
if 1 <= padlen <= 16:
    ok = True
    for k in range(1, padlen + 1):
        if padded[len(padded) - k] != padlen:
            ok = False
    if ok:
        unpadded = padded[:len(padded) - padlen]
out_hex = unpadded.hex()
if len(unpadded) != 64 and len(unpadded) != 80:
    out_hex = padded.hex()
sys.stdout.write('OPSPAN_NS:' + str(t1 - t0) + chr(10))
sys.stdout.flush()
sys.stdout.write('CLAIM:' + json.dumps({'plaintext_hex': out_hex}) + chr(10))
sys.stdout.flush()