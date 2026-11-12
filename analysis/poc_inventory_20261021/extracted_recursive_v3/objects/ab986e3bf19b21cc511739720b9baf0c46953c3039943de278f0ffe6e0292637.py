import sys, json, base64, time
ct_hex = "53cb980e70073ec2c7da3e57fc165269dc635e455beba23450cfb72baddd325d3d896c262aff5c1e554f50ebeb53540b7894489e01f58b8445d4b02493a77c0cfad35e725296e60e9573f24db03de94e"
iv_hex = "58dab86d2d546641e47a0239a4ab6951"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [iv] + [ct[i:i+16] for i in range(0, len(ct), 16)]
def oracle(fp, tgt):
    b64 = base64.b64encode(fp + tgt).decode('ascii')
    sys.stdout.write(json.dumps({"q": b64}, separators=(',', ':')) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        print("ORACLE_EOF", file=sys.stderr, flush=True)
        raise RuntimeError("oracle no reply")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))
def dec_one(tgt):
    inter = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad
        found = False
        for g in range(256):
            forged[pos] = g
            if oracle(bytes(forged), tgt):
                if pad == 1:
                    save = forged[14]
                    forged[14] ^= 1
                    ok2 = oracle(bytes(forged), tgt)
                    forged[14] = save
                    if not ok2:
                        continue
                inter[pos] = g ^ pad
                found = True
                break
        if not found:
            raise RuntimeError("byte fail")
    return bytes(inter)
t0 = time.monotonic_ns()
pts = []
for idx in range(1, len(blocks)):
    inter = dec_one(blocks[idx])
    prev = blocks[idx-1]
    pt = bytes(a ^ b for a, b in zip(inter, prev))
    pts.append(pt)
    print("BLOCK %d ok %s" % (idx, pt.hex()), file=sys.stderr, flush=True)
t1 = time.monotonic_ns()
full = b''.join(pts)
pl = full[-1]
if 1 <= pl <= 16 and full[-pl:] == bytes([pl]) * pl:
    plain = full[:-pl]
else:
    plain = full
sys.stdout.write("OPSPAN_NS:%d\n" % (t1 - t0))
sys.stdout.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": plain.hex()}, separators=(',', ':')) + "\n")
sys.stdout.flush()