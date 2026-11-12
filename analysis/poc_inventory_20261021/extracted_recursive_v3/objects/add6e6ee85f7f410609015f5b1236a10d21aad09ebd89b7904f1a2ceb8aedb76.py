import base64, json, sys, time

ct = bytes.fromhex("391849ee90cbef2316ca4a504973e8b4740ac32aa3c69f657a1ffda2f0d96559e0022169fce3c30e53ba5ae1c2f2383e8cdf603aec161f8043d9d8616c49a6186096b35a40acb403a4dad700ae52cb74")
iv = bytes.fromhex("2fcdd90ddbbf0a0f5fe661b5cd7b981b")

out = sys.stdout
inp = sys.stdin


def ask(two_blocks):
    out.write(json.dumps({"q": base64.b64encode(bytes(two_blocks)).decode()}) + "\n")
    out.flush()
    while True:
        line = inp.readline()
        if not line:
            raise SystemExit("eof")
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if "pad_ok" in obj:
            return bool(obj["pad_ok"])
        if "error" in obj:
            return False


n = len(ct) // 16
plain = bytearray()

for idx in range(n - 1, -1, -1):
    target = ct[idx * 16:(idx + 1) * 16]
    prev = iv if idx == 0 else ct[(idx - 1) * 16:idx * 16]
    d = bytearray(16)
    for pad in range(1, 17):
        base = bytearray(16)
        for k in range(16):
            base[k] = 0x41 if k < 16 - pad else (d[k] ^ pad)
        found = False
        for c in range(256):
            cand = bytearray(base)
            cand[16 - pad] = c
            if ask(bytes(prev) + bytes(cand)):
                d[16 - pad] = (c ^ pad) & 0xFF
                found = True
                break
        if not found:
            found2 = False
            for c in range(256):
                cand = bytearray(base)
                cand[16 - pad] = c
                if ask(bytes(prev) + bytes(cand)):
                    d[16 - pad] = (c ^ pad) & 0xFF
                    found2 = True
                    break
            if not found2:
                raise SystemExit("fail")
    plain.extend(bytes((d[k] ^ prev[k]) & 0xFF for k in range(16)))

out.write("OPSPAN_NS:%d\n" % time.monotonic_ns())
out.write("CLAIM:" + json.dumps({"plaintext_hex": bytes(plain).hex()}) + "\n")
out.flush()