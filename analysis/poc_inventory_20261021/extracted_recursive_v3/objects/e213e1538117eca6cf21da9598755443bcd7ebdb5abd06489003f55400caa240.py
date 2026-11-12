import sys, json, base64, time
ct = bytes.fromhex('e3099e94621290bdf325a922fede651c954ee1216dc94364b73ec124a88b47256be3f007a315bbe5b6913bb9c149c298bf61266d7302d31ae20eedf38cb6c749bf4ff0d0cba713eca0d571d51bb2f3e7')
iv = bytes.fromhex('16a5d06ec579fb053ed4fceeadaba7bc')
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
def qo(forged_prev, target):
    q = base64.b64encode(forged_prev+target).decode()
    print(json.dumps({'q': q}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError('no reply')
    return json.loads(line).get('pad_ok') is True
def decrypt_block(target):
    I = bytearray(16)
    forged = bytearray(16)
    for k in range(1, 17):
        pos = 16-k
        for j in range(pos+1, 16):
            forged[j] = I[j] ^ k
        for j in range(pos):
            forged[j] = 0
        found = False
        for g in range(256):
            forged[pos] = g
            ok = qo(bytes(forged), target)
            if not ok:
                continue
            if k == 1:
                chk = bytearray(forged)
                chk[14] ^= 1
                ok2 = qo(bytes(chk), target)
                if not ok2:
                    continue
            I[pos] = g ^ k
            found = True
            break
        if not found:
            raise RuntimeError(f'fail k={k}')
    return bytes(I)
t0 = time.monotonic_ns()
intermediates = []
for b in blocks:
    intermediates.append(decrypt_block(b))
t1 = time.monotonic_ns()
pt = b''.join(bytes(a ^ c for a, c in zip(I, p)) for I, p in zip(intermediates, prevs))
print(f'got {pt.hex()}', file=sys.stderr, flush=True)
pad = pt[-1]
if 1 <= pad <= 16 and pt[-pad:] == bytes([pad])*pad:
    pts = pt[:-pad]
else:
    pts = pt
print(f'OPSPAN_NS:{t1-t0}', flush=True)
print('CLAIM:'+json.dumps({'plaintext_hex': pts.hex()}), flush=True)