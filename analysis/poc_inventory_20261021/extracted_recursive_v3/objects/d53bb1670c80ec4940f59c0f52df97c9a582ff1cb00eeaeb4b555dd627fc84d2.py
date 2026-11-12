import sys, json, base64, time
ct_hex = '5238ac704eb3bfed250f2fcb0a2113d3ecf2217836fbfda0052b67b2ae73edaa3380757c171322848ee34e80828a926a68ecb540cbade61318d430e025bed5436f22c981291d8740f64a9a813492a455'
iv_hex = '9e78f54b81ecaf7530d4e9d9b9f1392d'
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
def ask(fprev, tgt):
    b = base64.b64encode(bytes(fprev) + bytes(tgt)).decode()
    print(json.dumps({'q': b}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError('eof')
    return json.loads(line).get('pad_ok') is True
n = len(blocks)
res = []
inters = []
for bi in range(n):
    tgt = blocks[bi]
    inter = bytearray(16)
    for pad_len in range(1, 17):
        pos = 16 - pad_len
        hit = False
        for trial in range(256):
            forged = bytearray(16)
            for k in range(pos + 1, 16):
                forged[k] = inter[k] ^ pad_len
            forged[pos] = trial
            ok = ask(forged, tgt)
            if ok:
                if pad_len == 1:
                    chk = bytearray(forged)
                    chk[14] = chk[14] ^ 1
                    ok2 = ask(chk, tgt)
                    if not ok2:
                        continue
                inter[pos] = trial ^ pad_len
                hit = True
                break
        if not hit:
            raise RuntimeError('nf')
    inters.append(bytes(inter))
    pt = bytes([inters[bi][j] ^ prevs[bi][j] for j in range(16)])
    res.append(pt)
t0 = time.monotonic_ns()
full = b''.join(res)
h = full.hex()
t1 = time.monotonic_ns()
print('OPSPAN_NS:' + str(t1 - t0), flush=True)
print('CLAIM:' + json.dumps({'plaintext_hex': h}), flush=True)