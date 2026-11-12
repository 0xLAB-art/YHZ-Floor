import base64, json, sys, time

CT_HEX = "391849ee90cbef2316ca4a504973e8b4740ac32aa3c69f657a1ffda2f0d96559e0022169fce3c30e53ba5ae1c2f2383e8cdf603aec161f8043d9d8616c49a6186096b35a40acb403a4dad700ae52cb74"
IV_HEX = "2fcdd90ddbbf0a0f5fe661b5cd7b981b"

ct = bytes.fromhex(CT_HEX)
iv = bytes.fromhex(IV_HEX)

stdin = sys.stdin
stdout = sys.stdout

def ask(data32):
    stdout.write(json.dumps({"q": base64.b64encode(data32).decode()}) + "\n")
    stdout.flush()
    line = stdin.readline()
    if not line:
        raise SystemExit("verifier closed connection")
    line = line.strip()
    if not line:
        return False
    try:
        obj = json.loads(line)
    except Exception:
        return False
    return bool(obj.get("pad_ok", False))

n = len(ct) // 16
plain = bytearray()

t0 = time.monotonic_ns()

for idx in range(n - 1, -1, -1):
    target = ct[idx * 16:(idx + 1) * 16]
    prev = iv if idx == 0 else ct[(idx - 1) * 16:idx * 16]
    d = bytearray(16)
    for pad in range(1, 17):
        base = bytearray(16)
        for k in range(16):
            if k >= 16 - pad:
                base[k] = d[k] ^ pad
            else:
                base[k] = 0x41
        c = 0
        found = False
        while c < 256:
            cand = bytearray(base)
            cand[16 - pad] = c
            if ask(bytes(prev) + bytes(cand)):
                d[16 - pad] = c ^ pad
                found = True
                break
            c += 1
        if not found:
            raise SystemExit("failed to recover block %d pad %d" % (idx, pad))
    plain.extend(bytes(d[k] ^ prev[k] for k in range(16)))

opspan = time.monotonic_ns() - t0

stdout.write("OPSPAN_NS:%d\n" % opspan)
stdout.write("CLAIM:" + json.dumps({"plaintext_hex": bytes(plain).hex()}) + "\n")
stdout.flush()