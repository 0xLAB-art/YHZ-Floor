import sys, json, base64, time
ct_hex = "49324420443d10ce58309579924019bdc720e55149c31c71abd1b8b58b71bf0e2454b8c4f9ff0c8188a9f661a641d6fe9311cc187c0637e9369f0d9d38c870ad3c9c17737ad72a1a4fba62f937da9f7a"
iv_hex = "67c5f628f658cce21f1f0fdd2919bc3a"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
def oracle(fp, tg):
    s = base64.b64encode(fp+tg).decode()
    sys.stdout.write(json.dumps({"q": s}) + "\n")
    sys.stdout.flush()
    while True:
        line = sys.stdin.readline()
        if line == "":
            raise RuntimeError("eof waiting oracle")
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except:
            continue
        if "pad_ok" in o:
            return bool(o["pad_ok"])
def dec(targ):
    inter = [0]*16
    for pad in range(1, 17):
        pos = 16 - pad
        found = None
        for g in range(256):
            f = bytearray(16)
            for j in range(pos+1, 16):
                f[j] = inter[j] ^ pad
            f[pos] = g
            if oracle(bytes(f), targ):
                if pad == 1:
                    f2 = bytearray(f)
                    f2[14] ^= 1
                    if not oracle(bytes(f2), targ):
                        continue
                found = g
                break
        if found is None:
            raise RuntimeError("no pad")
        inter[pos] = found ^ pad
    return bytes(inter)
t0 = time.monotonic_ns()
pts = []
for targ, prev in zip(blocks, prevs):
    inter = dec(targ)
    pts.append(bytes(a ^ b for a, b in zip(inter, prev)))
pt = b"".join(pts)
t1 = time.monotonic_ns()
sys.stdout.write("OPSPAN_NS:%d\n" % (t1-t0))
sys.stdout.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": pt.hex()}) + "\n")
sys.stdout.flush()