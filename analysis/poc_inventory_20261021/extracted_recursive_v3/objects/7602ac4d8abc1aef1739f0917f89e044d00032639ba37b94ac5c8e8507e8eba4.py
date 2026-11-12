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


def recover(target, prefer_large, maxq=6000):
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
        if prefer_large:
            opts.sort(key=lambda v: (0 if v == p else 1, -v))
        else:
            opts.sort(key=lambda v: (0 if v != p else 1, v))
        for v in opts:
            I2 = list(I)
            I2[pos] = v
            dfs(I2, p + 1)
            if found:
                return

    dfs([0] * 16, 1)
    if not found:
        return None
    return bytes(found[0])


def run_all(prefer_large):
    out = []
    prev = IV
    for i in range(1, len(CT) // 16):
        target = CT[i * 16:(i + 1) * 16]
        inter = recover(target, prefer_large)
        if inter is None:
            return None
        out.append(bytes(a ^ b for a, b in zip(inter, prev)))
        prev = target
    return b"".join(out)


def ok_last(pt):
    if not pt:
        return False
    k = pt[-1]
    if k < 1 or k > 16 or k > len(pt):
        return False
    return pt[-k:] == bytes([k]) * k


start = time.monotonic_ns()
best = None
for prefer in (True, False):
    try:
        cand = run_all(prefer)
    except Budget:
        cand = None
    except Exception:
        cand = None
    if cand and (best is None or ok_last(cand)):
        best = cand
    if best is not None and ok_last(best):
        break
elapsed = time.monotonic_ns() - start
if best is None:
    best = b""
sys.stdout.write("OPSPAN_NS:" + str(elapsed) + "\n")
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": best.hex()}) + "\n")
sys.stdout.flush()