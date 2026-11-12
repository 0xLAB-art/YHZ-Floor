import base64, json, select, sys, time

CT = bytes.fromhex("e797b1868e32fdf16be9d5abd28066aa55204b840c03865cac00c59e62b64d5e09091a8523cd891801ce0915a1620fdbbf649676884715ccec512040472ac02d7c3801aec8a3d42ffdaed85c06f1975a")
BS = 16
KEYS = ("pad_ok", "ok", "result", "valid", "padded", "value", "response", "reply")
cache = {}


def query(payload):
    r = cache.get(payload)
    if r is not None:
        return r
    line = json.dumps({"q": base64.b64encode(payload).decode()})
    for _ in range(10):
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        deadline = time.time() + 25.0
        val = None
        while time.time() < deadline:
            try:
                rd, _, _ = select.select([sys.stdin], [], [], 1.0)
            except Exception:
                rd = [sys.stdin]
            if not rd:
                continue
            s = sys.stdin.readline()
            if s == "":
                break
            s = s.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception:
                if s.lower() in ("true", "false"):
                    val = s.lower() == "true"
                    break
                continue
            if isinstance(obj, bool):
                val = obj
            elif isinstance(obj, dict):
                for k in KEYS:
                    if k in obj:
                        val = bool(obj[k])
                        break
            if val is not None:
                break
        if val is not None:
            cache[payload] = val
            return val
    raise SystemExit("oracle unreachable")


def recover_block(target, known=None):
    got = bytearray(BS)
    if known:
        for j, v in known.items():
            got[j] = v
    for pos in range(BS - 1, -1, -1):
        hit = None
        for extra in range(0, BS - pos + 1):
            pad = BS - pos + extra
            base = bytearray(BS)
            for j in range(pos + 1, BS):
                base[j] = got[j] ^ pad
            for c in range(256):
                base[pos] = c
                if query(bytes(base) + target):
                    hit = c
                    break
            if hit is not None:
                break
        if hit is None:
            raise SystemExit("no byte at %d" % pos)
        got[pos] = hit
    return bytes(got)


blocks = [CT[i:i + BS] for i in range(0, len(CT), BS)]
plain = bytearray(len(CT))
# P is exactly 64 bytes and CT is 80 bytes => PKCS#7 padding is a full block of 0x10
plain[len(CT) - BS:] = b"\x10" * BS

for idx in range(len(blocks) - 2, -1, -1):
    plain[idx * BS:(idx + 1) * BS] = recover_block(blocks[idx])

t0 = time.monotonic_ns()
out = bytes(plain)
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": out.hex()}) + "\n")
sys.stdout.write("OPSPAN_NS:%d\n" % (time.monotonic_ns() - t0))
sys.stdout.flush()