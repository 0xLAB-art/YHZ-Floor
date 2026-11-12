import base64
import json
import sys
import time
ct_hex = '0a8ae66fe7e41260fd3a025a0dfb31ecf544d2e0f141bb0a4b71ef5fb138d28ec89513425b868f13ebb10c8a9158af4bd119c5f3e0b14ac7fadb3805012e1bfa18da0dbcf3cffae17ec0466896bf7326'
iv_hex = '0892f9219c7c1fbb4e7ed41697b63342'
def ask(fb, tb):
    data = bytes(fb) + bytes(tb)
    b = base64.b64encode(data).decode('ascii')
    print(json.dumps({'q': b}), flush=True)
    ln = sys.stdin.readline()
    if ln == '':
        print('eof', file=sys.stderr, flush=True)
        raise RuntimeError('eof-no-reply')
    return bool(json.loads(ln).get('pad_ok'))
def recover(tb):
    inter = bytearray(16)
    fb = bytearray(16)
    for plen in range(1, 17):
        pos = 16 - plen
        for j in range(pos+1, 16):
            fb[j] = inter[j] ^ plen
        for j in range(pos):
            fb[j] = 0
        hit = -1
        for c in range(256):
            fb[pos] = c
            if ask(fb, tb):
                if plen == 1:
                    sv = fb[pos-1]
                    fb[pos-1] = sv ^ 1
                    ok2 = ask(fb, tb)
                    fb[pos-1] = sv
                    fb[pos] = c
                    if not ok2:
                        continue
                inter[pos] = c ^ plen
                hit = c
                break
        if hit < 0:
            raise RuntimeError('no-cand')
    return bytes(inter)
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
t0 = time.monotonic_ns()
out = b''
for idx, tgt in enumerate(blocks):
    print('block-start', file=sys.stderr, flush=True)
    ii = recover(tgt)
    print('block-done', file=sys.stderr, flush=True)
    out = out + bytes(ii[k] ^ prevs[idx][k] for k in range(16))
n = out[-1]
if 1 <= n <= 16:
    chk = bytes([n]) * n
    if out[-n:] == chk:
        out = out[:-n]
t1 = time.monotonic_ns()
print('OPSPAN_NS:' + str(t1 - t0), flush=True)
print('CLAIM:' + json.dumps({'plaintext_hex': out.hex()}), flush=True)