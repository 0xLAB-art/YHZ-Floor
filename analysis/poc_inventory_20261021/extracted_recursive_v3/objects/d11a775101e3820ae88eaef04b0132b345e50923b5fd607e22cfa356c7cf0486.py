import base64, json, sys

CT = bytes.fromhex("7e64739f09112a4495b1ab79d25064125a2532b3ecf2ce9145a25a4265c0d2a8c26634728526186d8b58430931fa0c385751a86ebcde047455dcd11aafcbda4e07d0d6a07ba3dbd9d909f3880ff39c99")

def oracle(forged, target):
    q = base64.b64encode(forged + target).decode()
    sys.stdout.write(json.dumps({"q": q}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("no reply")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def main():
    blocks = [CT[i:i+16] for i in range(0, len(CT), 16)]
    n = len(blocks)
    recovered = [None] * n
    queries = 0
    for i in range(n, 0, -1):
        target = blocks[i]
        prev = blocks[i-1]
        inter = bytearray(16)
        for pos in range(16):
            padlen = 16 - pos
            base = bytearray(16)
            for k in range(pos):
                base[k] = inter[k] ^ padlen
            low = 0 if pos == 15 else 1
            hi = 256
            found = None
            while low < hi:
                mid = (low + hi) // 2
                test = bytearray(base)
                test[pos] = mid
                ok = oracle(bytes(test), target)
                queries += 1
                if ok:
                    hi = mid
                    found = mid
                else:
                    low = mid + 1
            if found is None:
                test = bytearray(base)
                test[pos] = 0 if pos == 15 else 1
                ok = oracle(bytes(test), target)
                queries += 1
                found = 0 if ok else 1
                while True:
                    test = bytearray(base)
                    test[pos] = found
                    if oracle(bytes(test), target):
                        break
                    queries += 1
                    found += 1
            inter[pos] = found ^ padlen
        recovered[i-1] = bytes(a ^ b for a, b in zip(inter, prev))
    pt = b"".join(recovered)
    sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": pt.hex()}) + "\n")
    sys.stdout.flush()

main()