import sys, json, base64, time
ct_hex = "ee0b7104daa977e1e0a569e8d0cd3fab6f1d615090b7a2a5b08cf2e37874cd6d45390a1f0816ab2685c8e224248343d5c3467daa8dba078f8415d0eeb59e968bb619d0a6a9dd7de14208fd731876eff4"
iv_hex = "22da83b7a1b1ffca86c9858602190b37"
t0 = time.monotonic_ns()
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]

def ask(fprev, tgt):
    data = bytes(fprev) + bytes(tgt)
    b64 = base64.b64encode(data).decode()
    line = json.dumps({"q": b64}, separators=(",", ":"))
    print(line, flush=True)
    r = sys.stdin.readline()
    if not r:
        raise RuntimeError("EOF from oracle (no reply)")
    return bool(json.loads(r).get("pad_ok"))

def decrypt_target(tgt):
    inter = bytearray(16)
    forged = bytearray(16)
    for pad in range(1, 17):
        pos = 16 - pad
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad
        for j in range(pos):
            forged[j] = 0
        found = None
        for g in range(256):
            forged[pos] = g
            try:
                ok = ask(forged, tgt)
            except RuntimeError:
                raise
            if ok:
                if pad == 1:
                    # disambiguate 0x01 vs 0x02 0x02 etc: flip 2nd-last byte
                    save = forged[14]
                    forged[14] ^= 0x01
                    ok2 = ask(forged, tgt)
                    forged[14] = save
                    if not ok2:
                        continue
                found = g
                break
        if found is None:
            raise RuntimeError(f"no guess pad={pad}")
        inter[pos] = found ^ pad
    return bytes(inter)

pts = []
for tgt, prv in zip(blocks, prevs):
    inter = decrypt_target(tgt)
    pts.append(bytes(a ^ b for a, b in zip(inter, prv)))
padded = b"".join(pts)
# strip pkcs7 if present for claim (verifier also strips, either ok)
try:
    l = padded[-1]
    if 1 <= l <= 16 and padded[-l:] == bytes([l])*l:
        pass
except Exception:
    pass
t1 = time.monotonic_ns()
print(f"OPSPAN_NS:{t1-t0}", flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": padded.hex()}, separators=(",", ":")), flush=True)