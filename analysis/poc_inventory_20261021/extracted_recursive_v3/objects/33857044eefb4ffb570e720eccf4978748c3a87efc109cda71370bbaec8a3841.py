import base64, json, sys, time

CT = bytes.fromhex("437efaa2557c971a321ba4ee00865643894fea10634e9a29dfa4395c1f1877ab4cee1d16a7b6c2da5871e379b641fa54f273672442f5b803e68872c2fbda17feb89e3bbe17244a1a1e4388871b585a9e")
IV = bytes.fromhex("1714c786409b40c0e4a792bac6857f5b")


def ask(prev, target):
    payload = base64.b64encode(bytes(prev) + bytes(target)).decode()
    sys.stdout.write('{"q": "' + payload + '"}\n')
    sys.stdout.flush()
    while True:
        line = sys.stdin.readline()
        if not line:
            sys.exit(0)
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except Exception:
            continue
        if isinstance(obj, dict) and "pad_ok" in obj:
            return bool(obj["pad_ok"])


class Budget(Exception):
    pass


def recover(target, maxq=6000):
    state = {"q": maxq}
    found = []

    def dfs(I, p):
        if found:
            return
        if p > 16:
            found.append(list(I))
            return
        pos = 16 - p
        forged = bytearray(16)
        for k in range(pos + 1, 16):
            forged[k] = I[k] ^ p
        opts = []
        for g in range(256):
            forged[pos] = g
            state["q"] -= 1
            if state["q"] <= 0:
                raise Budget()
            if ask(forged, target):
                opts.append(g ^ p)
        # prefer candidate where padding is exactly p
        exact = [v for v in opts if v == p]
        rest = [v for v in opts if v != p]
        rest.sort()
        for v in exact + rest:
            I2 = list(I)
            I2[pos] = v
            dfs(I2, p + 1)
            if found:
                return

    dfs([0] * 16, 1)
    if not found:
        return None
    return bytes(found[0])


def run_all(maxq=6000):
    out = []
    prev = IV
    for i in range(1, len(CT) // 16):
        target = CT[i * 16:(i + 1) * 16]
        inter = recover(target, maxq)
        if inter is None:
            return None
        out.append(bytes(a ^ b for a, b in zip(inter, prev)))
        prev = target
    return b"".join(out)


start = time.monotonic_ns()
pt = None
try:
    pt = run_all()
except Budget:
    pt = None
except Exception:
    pt = None
elapsed = time.monotonic_ns() - start
if pt is None:
    pt = b""
sys.stdout.write('OPSPAN_NS:' + str(elapsed) + '\n')
sys.stdout.write('CLAIM:' + json.dumps({"plaintext_hex": pt.hex()}) + '\n')
sys.stdout.flush()