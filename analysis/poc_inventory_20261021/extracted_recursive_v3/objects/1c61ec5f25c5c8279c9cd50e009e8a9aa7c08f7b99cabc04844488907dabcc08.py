import base64, json, os, select, time

CT = bytes.fromhex("391849ee90cbef2316ca4a504973e8b4740ac32aa3c69f657a1ffda2f0d96559e0022169fce3c30e53ba5ae1c2f2383e8cdf603aec161f8043d9d8616c49a6186096b35a40acb403a4dad700ae52cb74")
IV = bytes.fromhex("2fcdd90ddbbf0a0f5fe661b5cd7b981b")

buf = bytearray()
queue = []


def pump(timeout):
    try:
        r, _, _ = select.select([0], [], [], timeout)
    except Exception:
        return False
    if not r:
        return False
    try:
        data = os.read(0, 65536)
    except Exception:
        return False
    if not data:
        return False
    buf.extend(data)
    while b"\n" in buf:
        i = buf.index(b"\n")
        line = bytes(buf[:i])
        del buf[:i + 1]
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line.decode("utf-8", "replace"))
        except Exception:
            continue
        if isinstance(obj, dict) and "pad_ok" in obj:
            v = obj["pad_ok"]
            if isinstance(v, str):
                queue.append(v.strip().lower() in ("true", "1", "yes"))
            else:
                queue.append(bool(v))
    return True


def ask(two):
    while queue:
        queue.pop(0)
    payload = json.dumps({"q": base64.b64encode(bytes(two)).decode()}) + "\n"
    try:
        os.write(1, payload.encode())
    except Exception:
        return False
    deadline = time.time() + 20.0
    while not queue:
        pump(2.0)
        if time.time() > deadline:
            return False
    return queue.pop(0)


def recover(prev, known=None):
    d = bytearray(16)
    for pad in range(1, 17):
        pos = 16 - pad
        if known is not None and pos >= 16 - len(known) and pad <= len(known):
            d[pos] = known[pad - 1]
            continue
        base = bytearray(16)
        for k in range(16):
            base[k] = 0x41 if k < pos else (d[k] ^ pad)
        hit = None
        for c in range(256):
            cand = bytearray(base)
            cand[pos] = c
            if ask(bytes(prev) + bytes(cand)):
                hit = c
                break
        if hit is None:
            for c in range(256):
                cand = bytearray(base)
                cand[pos] = c
                if ask(bytes(prev) + bytes(cand)):
                    hit = c
                    break
        if hit is None:
            raise RuntimeError("no byte at pad %d" % pad)
        d[pos] = (hit ^ pad) & 0xFF
    return d


n = len(CT) // 16
plain = bytearray()
t0 = time.monotonic_ns()
try:
    for idx in range(n - 1, -1, -1):
        prev = IV if idx == 0 else CT[(idx - 1) * 16:idx * 16]
        known = None
        if idx == n - 1:
            known = bytes([0x10]) * 16
        d = recover(prev, known)
        plain.extend(bytes((d[k] ^ prev[k]) & 0xFF for k in range(16)))
except Exception as e:
    try:
        os.write(2, ("err: %r blocks=%d\n" % (e, len(plain) // 16)).encode())
    except Exception:
        pass

sp = time.monotonic_ns() - t0
line = "CLAIM:" + json.dumps({"plaintext_hex": bytes(plain).hex()}) + "\n"
try:
    os.write(1, ("OPSPAN_NS:%d\n" % sp).encode())
except Exception:
    pass
os.write(1, line.encode())