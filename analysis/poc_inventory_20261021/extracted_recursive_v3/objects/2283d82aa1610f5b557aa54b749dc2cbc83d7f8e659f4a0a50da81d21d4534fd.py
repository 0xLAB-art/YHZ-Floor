import base64, json, sys, time

ct_hex = "437efaa2557c971a321ba4ee00865643894fea10634e9a29dfa4395c1f1877ab4cee1d16a7b6c2da5871e379b641fa54f273672442f5b803e68872c2fbda17feb89e3bbe17244a1a1e4388871b585a9e"
iv_hex = "1714c786409b40c0e4a792bac6857f5b"

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)


def ask(prev, target):
    line = json.dumps({"q": base64.b64encode(prev + target).decode()})
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
    r = sys.stdin.readline()
    if not r:
        sys.exit(1)
    return json.loads(r)["pad_ok"]


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


plain = bytearray()
inter = bytearray(iv)
start = time.monotonic_ns()

for bi in range(1, len(ct) // 16):
    target = ct[bi * 16:(bi + 1) * 16]
    ivblk = bytearray(16)
    cand = bytearray(16)
    for p in range(1, 17):
        for pos in range(16):
            if pos >= p:
                cand[pos] = inter[pos]
            # build the desired intermediate for this position
            want = bytearray(16)
            for k in range(16):
                if k < p:
                    padbyte = p + 1
                    prevp = plain[len(plain) - p + k] if (len(plain) - p + k) >= 0 else 0
                    want[k] = padbyte ^ prevp
                else:
                    want[k] = inter[k]
            for g in range(256):
                cand[pos] = g
                if ask(bytes(cand), target):
                    ivblk[pos] = g
                    cand[pos] = g
                    break
            cand[pos] = want[pos] ^ (inter[pos] ^ 0) if False else cand[pos]
            cand[pos] = want[pos]
        # verify / handle ambiguity
        cur = ivblk[16 - p] ^ inter[16 - p]
        if p == 16:
            # ambiguity between pad length 15 and 16
            for g in range(256):
                cand[15] = g
                if not ask(bytes(cand), target):
                    ivblk[15] = g
                    break
    plain.extend(xor_bytes(bytes(ivblk), inter))
    inter = target

elapsed = time.monotonic_ns() - start
pb = bytes(plain)
sys.stdout.write("OPSPAN_NS:" + str(elapsed) + "\n")
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": pb.hex()}) + "\n")
sys.stdout.flush()