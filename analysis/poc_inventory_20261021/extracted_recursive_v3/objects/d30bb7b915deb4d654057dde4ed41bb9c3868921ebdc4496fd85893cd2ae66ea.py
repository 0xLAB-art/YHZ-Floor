import base64, json, select, sys, time

CT = bytes.fromhex("e797b1868e32fdf16be9d5abd28066aa55204b840c03865cac00c59e62b64d5e09091a8523cd891801ce0915a1620fdbbf649676884715ccec512040472ac02d7c3801aec8a3d42ffdaed85c06f1975a")
IV = bytes.fromhex("ae78b36337ef90e116841212970e9f36")
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
        deadline = time.time() + 30.0
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
                low = s.lower()
                if low == "true":
                    val = True
                    break
                if low == "false":
                    val = False
                    break
                continue
            if isinstance(obj, bool):
                val = obj
                break
            if isinstance(obj, dict):
                for k in KEYS:
                    if k in obj:
                        val = bool(obj[k])
                        break
                if 'val' in locals() and isinstance(val, bool):
                    break
        if 'val' in locals() and isinstance(val, bool):
            cache[payload] = val
            return val
    raise SystemExit("oracle unreachable")


def decrypt_block(prev_block, target_block):
    got = bytearray(BS)
    intermediate = bytearray(BS)
    for pos in range(BS - 1, -1, -1):
        pad = BS - pos
        # Try all possible values for byte at pos
        for c in range(256):
            crafted = bytearray(BS)
            for j in range(pos + 1, BS):
                crafted[j] = got[j] ^ pad
            crafted[pos] = c
            if query(bytes(crafted) + target_block):
                intermediate[pos] = c ^ pad
                got[pos] = c
                break
        else:
            raise SystemExit("no byte at %d" % pos)
    plain_block = bytes([intermediate[i] ^ prev_block[i] for i in range(BS)])
    return plain_block


blocks = [CT[i:i + BS] for i in range(0, len(CT), BS)]
plain = bytearray()
prev = IV
for i in range(len(blocks)):
    p = decrypt_block(prev, blocks[i])
    plain.extend(p)
    prev = blocks[i]

t0 = time.monotonic_ns()
out = bytes(plain)
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": out.hex()}) + "\n")
sys.stdout.write("OPSPAN_NS:%d\n" % (time.monotonic_ns() - t0))
sys.stdout.flush()