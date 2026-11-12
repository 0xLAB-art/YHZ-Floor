import sys, json, base64, time
ct_hex = '7feffb7fe9f6adced12896d47a5fc8eaa2a51219aa331713634f22ecc40c6a35112d4733fe30d96588df29a587c89e64d72be382807e144d1ecc2761a99c4f65b626077b5bb7caaa93183335d5f5d7fc'
iv_hex = 'b3b8aa9275f2f1dac764b728d15a1f1f'
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
n = len(ct) // 16
blocks = [ct[i*16:(i+1)*16] for i in range(n)]
def oracle(fp, tgt):
    q = base64.b64encode(bytes(fp)+bytes(tgt)).decode()
    print(json.dumps({'q': q}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError('eof')
    return json.loads(line).get('pad_ok') is True
def dec_block(tgt):
    inter = bytearray(16)
    for k in range(15, -1, -1):
        pad = 16 - k
        hit = None
        for g in range(256):
            forged = bytearray(16)
            for j in range(k+1, 16):
                forged[j] = inter[j] ^ pad
            forged[k] = g
            if oracle(forged, tgt):
                if pad == 1:
                    forged2 = bytearray(forged)
                    forged2[14] ^= 1
                    if not oracle(forged2, tgt):
                        continue
                hit = g
                break
        if hit is None:
            raise RuntimeError('fail')
        inter[k] = hit ^ pad
    return bytes(inter)
inters = [None]*n
t0 = None
t1 = None
plain = bytearray()
for idx in range(n):
    tgt = blocks[idx]
    if idx == n-1:
        t0 = time.monotonic_ns()
    inter = dec_block(tgt)
    if idx == n-1:
        t1 = time.monotonic_ns()
    inters[idx] = inter
for idx in range(n):
    prev = iv if idx == 0 else blocks[idx-1]
    inter = inters[idx]
    pblk = bytes(a ^ b for a, b in zip(inter, prev))
    plain.extend(pblk)
print(f'OPSPAN_NS:{t1-t0}', flush=True)
print('CLAIM:'+json.dumps({'plaintext_hex': bytes(plain).hex()}), flush=True)