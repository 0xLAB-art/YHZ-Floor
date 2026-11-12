import sys, json, base64, time
ct_hex = '53cb980e70073ec2c7da3e57fc165269dc635e455beba23450cfb72baddd325d3d896c262aff5c1e554f50ebeb53540b7894489e01f58b8445d4b02493a77c0cfad35e725296e60e9573f24db03de94e'
iv_hex = '58dab86d2d546641e47a0239a4ab6951'
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [iv] + [ct[i:i+16] for i in range(0, len(ct), 16)]
def oracle(fp, tgt):
    q = base64.b64encode(fp+tgt).decode()
    print(json.dumps({'q': q}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError('oracle no reply')
    return bool(json.loads(line).get('pad_ok'))
def dec_block(tgt):
    inter = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad
        hit = False
        for g in range(256):
            forged[pos] = g
            if oracle(bytes(forged), tgt):
                if pos == 15:
                    tmp = bytearray(forged)
                    tmp[14] ^= 1
                    if not oracle(bytes(tmp), tgt):
                        continue
                inter[pos] = g ^ pad
                hit = True
                break
        if not hit:
            raise RuntimeError('decrypt failed')
    return bytes(inter)
t0 = time.monotonic_ns()
pt_blocks = []
for idx in range(1, len(blocks)):
    tgt = blocks[idx]
    prev = blocks[idx-1]
    inter = dec_block(tgt)
    pt = bytes(a ^ b for a, b in zip(inter, prev))
    pt_blocks.append(pt)
t1 = time.monotonic_ns()
full = b''.join(pt_blocks)
padlen = full[-1]
if 1 <= padlen <= 16 and full[-padlen:] == bytes([padlen])*padlen:
    plain = full[:-padlen]
else:
    plain = full
print(f'OPSPAN_NS:{t1-t0}', flush=True)
print('CLAIM:' + json.dumps({'plaintext_hex': plain.hex()}), flush=True)