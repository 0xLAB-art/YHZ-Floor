import base64, json, sys, time

CT = bytes.fromhex("e797b1868e32fdf16be9d5abd28066aa55204b840c03865cac00c59e62b64d5e09091a8523cd891801ce0915a1620fdbbf649676884715ccec512040472ac02d7c3801aec8a3d42ffdaed85c06f1975a")
IV = bytes.fromhex("ae78b36337ef90e116841212970e9f36")
BS = 16

def oracle(prev, target):
    q = base64.b64encode(prev + target).decode()
    sys.stdout.write(json.dumps({"q": q}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise SystemExit("no reply")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

blocks = [CT[i:i+BS] for i in range(0, len(CT), BS)]
plain = bytearray()
prev_cipher = IV

for idx in range(len(blocks) - 1, -1, -1):
    target = blocks[idx]
    found = bytearray(BS)
    got = bytearray(BS)
    for pos in range(BS - 1, -1, -1):
        pad = BS - pos
        base = bytearray(BS)
        for j in range(pos + 1, BS):
            base[j] = got[j] ^ pad
        for c in range(256):
            base[pos] = c
            if oracle(bytes(base), target):
                found[pos] = c ^ pad
                got[pos] = c
                break
        else:
            raise SystemExit("no byte at pos %d" % pos)
    plain[idx*BS:(idx+1)*BS] = bytes(found)
    prev_cipher = target

t0 = time.monotonic_ns()
out = bytes(plain)
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": out.hex()}) + "\n")
sys.stdout.flush()