import base64, json, sys, time
ct_hex = "0a8ae66fe7e41260fd3a025a0dfb31ecf544d2e0f141bb0a4b71ef5fb138d28ec89513425b868f13ebb10c8a9158af4bd119c5f3e0b14ac7fadb3805012e1bfa18da0dbcf3cffae17ec0466896bf7326"
iv_hex = "0892f9219c7c1fbb4e7ed41697b63342"

def oq(forged, target):
    data = bytes(forged) + bytes(target)
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    while True:
        line = sys.stdin.readline()
        if line == "":
            raise RuntimeError("EOF")
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if "pad_ok" in o:
            return bool(o["pad_ok"])

def rec(tgt):
    inter = bytearray(16)
    forged = bytearray(16)
    for plen in range(1, 17):
        pos = 16 - plen
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ plen
        for j in range(pos):
            forged[j] = 0
        okc = None
        for cand in range(256):
            forged[pos] = cand
            if oq(forged, tgt):
                if plen == 1:
                    sv = forged[pos-1]
                    forged[pos-1] = sv ^ 1
                    ok2 = oq(forged, tgt)
                    forged[pos-1] = sv
                    if not ok2:
                        continue
                inter[pos] = cand ^ plen
                okc = cand
                break
        if okc is None:
            raise RuntimeError("no cand")
    return bytes(inter)

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
t0 = time.monotonic_ns()
ptp = b""
for i, tgt in enumerate(blocks):
    ii = rec(tgt)
    ptp += bytes(ii[j] ^ prevs[i][j] for j in range(16))
pt = ptp
n = pt[-1]
if 1 <= n <= 16 and pt[-n:] == bytes([n])*n:
    pt = pt[:-n]
t1 = time.monotonic_ns()
sys.stdout.write("OPSPAN_NS:" + str(t1-t0) + "\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": pt.hex()}) + "\n")
sys.stdout.flush()