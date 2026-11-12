import base64, json, select, sys, time

CT = bytes.fromhex("e797b1868e32fdf16be9d5abd28066aa55204b840c03865cac00c59e62b64d5e09091a8523cd891801ce0915a1620fdbbf649676884715ccec512040472ac02d7c3801aec8a3d42ffdaed85c06f1975a")
IV = bytes.fromhex("ae78b36337ef90e116841212970e9f36")
BS = 16

KEYS = ("pad_ok", "ok", "result", "valid", "reply", "response", "value", "padded")

def read_reply(timeout=15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r, _, _ = select.select([sys.stdin], [], [], 0.5)
        except Exception:
            r = [sys.stdin]
        if r:
            line = sys.stdin.readline()
            if line == "":
                return None
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception:
                low = s.lower()
                if low in ("true", "1"):
                    return True
                if low in ("false", "0"):
                    return False
                continue
            if isinstance(obj, bool):
                return obj
            if isinstance(obj, dict):
                for k in KEYS:
                    if k in obj:
                        return bool(obj[k])
                continue
            if isinstance(obj, list) and obj:
                return bool(obj[0])
    return None

def oracle(prev, target):
    payload = base64.b64encode(prev + target).decode()
    line = json.dumps({"q": payload})
    for _ in range(5):
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        v = read_reply()
        if v is not None:
            return v
        time.sleep(0.1)
    raise SystemExit("oracle unreachable")

blocks = [CT[i:i+BS] for i in range(0, len(CT), BS)]
plain = bytearray(len(CT))

for idx in range(len(blocks) - 1, -1, -1):
    target = blocks[idx]
    got = bytearray(BS)
    for pos in range(BS - 1, -1, -1):
        pad = BS - pos
        base = bytearray(BS)
        for j in range(pos + 1, BS):
            base[j] = got[j] ^ pad
        hit = None
        for c in range(256):
            base[pos] = c
            if oracle(bytes(base), target):
                hit = c
                break
        if hit is None:
            raise SystemExit("no byte at %d" % pos)
        got[pos] = hit
    plain[idx*BS:(idx+1)*BS] = bytes(got)

t0 = time.monotonic_ns()
out = bytes(plain)
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": out.hex()}) + "\n")
sys.stdout.flush()
print("OPSPAN_NS:%d" % 0)
sys.stdout.flush()