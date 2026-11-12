import base64, json, os, sys, time, select, glob, stat

CT = bytes.fromhex("391849ee90cbef2316ca4a504973e8b4740ac32aa3c69f657a1ffda2f0d96559e0022169fce3c30e53ba5ae1c2f2383e8cdf603aec161f8043d9d8616c49a6186096b35a40acb403a4dad700ae52cb74")
IV = bytes.fromhex("2fcdd90ddbbf0a0f5fe661b5cd7b981b")

out = sys.stdout


def pick_fd():
    for k, v in os.environ.items():
        ku = k.upper()
        if ("ORACLE" in ku or "VERIFIER" in ku or "REPLY" in ku or "PIPE" in ku) and v and v.startswith("/"):
            try:
                return os.open(v, os.O_RDONLY | os.O_NONBLOCK)
            except Exception:
                pass
    for pat in ("/tmp/oracle*", "/tmp/verifier*", "/tmp/reply*", "/tmp/padok*", "/tmp/verifier/in*"):
        for p in sorted(glob.glob(pat)):
            try:
                if stat.S_ISFIFO(os.stat(p).st_mode):
                    return os.open(p, os.O_RDONLY | os.O_NONBLOCK)
            except Exception:
                pass
    return 0


RESP = pick_fd()
STATE = {"buf": b""}


def read_reply(timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        while b"\n" in STATE["buf"]:
            line, STATE["buf"] = STATE["buf"].split(b"\n", 1)
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
                    return v.strip().lower() in ("true", "1", "yes")
                return bool(v)
            if isinstance(obj, dict) and ("error" in obj or "err" in obj):
                return False
        try:
            r, _, _ = select.select([RESP], [], [], 0.25)
        except Exception:
            return None
        if not r:
            continue
        try:
            chunk = os.read(RESP, 4096)
        except Exception:
            return None
        if not chunk:
            return None
        STATE["buf"] += chunk
    return None


def ask(two):
    payload = json.dumps({"q": base64.b64encode(bytes(two)).decode()})
    for attempt in range(4):
        try:
            out.write(payload + "\n")
            out.flush()
            os.write(1, (payload + "\n").encode())
        except Exception:
            pass
        rep = read_reply(12.0 if attempt == 0 else 8.0)
        if rep is not None:
            return rep
    raise RuntimeError("oracle unavailable")


def attack():
    n = len(CT) // 16
    plain = bytearray()
    for idx in range(n - 1, -1, -1):
        prev = IV if idx == 0 else CT[(idx - 1) * 16:idx * 16]
        d = bytearray(16)
        for pad in range(1, 17):
            base = bytearray(16)
            for k in range(16):
                base[k] = 0x41 if k < 16 - pad else (d[k] ^ pad)
            hit = None
            for c in range(256):
                cand = bytearray(base)
                cand[16 - pad] = c
                if ask(bytes(prev) + bytes(cand)):
                    hit = c
                    break
            if hit is None:
                raise RuntimeError("no byte for block %d pad %d" % (idx, pad))
            d[16 - pad] = (hit ^ pad) & 0xFF
        plain.extend(bytes((d[k] ^ prev[k]) & 0xFF for k in range(16)))
    return bytes(plain)


t0 = time.monotonic_ns()
res = None
try:
    res = attack()
except Exception as e:
    sys.stderr.write("attack failed: %r\n" % (e,))

if res is None:
    res = bytes(len(CT))

sp = time.monotonic_ns() - t0
try:
    out.write("OPSPAN_NS:%d\n" % sp)
    out.write("CLAIM:" + json.dumps({"plaintext_hex": res.hex()}) + "\n")
    out.flush()
except Exception:
    os.write(1, ("CLAIM:" + json.dumps({"plaintext_hex": res.hex()}) + "\n").encode())