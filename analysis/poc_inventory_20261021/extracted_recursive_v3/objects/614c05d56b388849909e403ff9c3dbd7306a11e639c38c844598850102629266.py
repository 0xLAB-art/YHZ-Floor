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


def pad(b, n):
    return bytes([n]) * n


plain = bytearray()
inter = bytearray(iv)
nfor bi in range(1, len(ct) // 16):
    target = ct[bi * 16:(bi + 1) * 16]
    # intermediate value for the block being decrypted
    ivblk = bytearray(16)
    found = False
    for p in range(1, 17):
        # valid intermediate bytes for padding length p
        cand = [None] * 16
        good = 0
        for pos in range(16):
            want = xor_bytes(bytes([p]) * p, bytes([p]) + plain[-p + 1:]) if False else None
            if pos < p:
                base = bytearray(16)
                for k in range(p):
                    base[k] = pad(None, p)[k] ^ (plain[len(plain) - p + k] if (len(plain) - p + k) >= 0 else 0)
                want = xor_bytes(inter[1:], bytes(base))
            else:
                want = inter[1:]
            # brute force over 256 values for this position
            opts = []
            for g in range(256):
                cand[pos] = g
                if ask(bytes(cand), target):
                    opts.append(g)
            if len(opts) == 1:
                ivblk[pos] = opts[0]
            elif len(opts) > 1:
                if p == 16:
                    for g in opts:
                        cand[pos] = g
                        if not ask(bytes(cand), target):
                            ivblk[pos] = g
                            break
                else:
                    raise RuntimeError("ambiguous")
            else:
                # fall back to re-testing with known good bytes fixed
                raise RuntimeError("no candidate")
        plain.extend(xor_bytes(bytes(ivblk), inter))
        inter = target
        found = True
        break

plain_bytes = bytes(plain)
print("OPSPAN_NS:0")
print("CLAIM:" + json.dumps({"plaintext_hex": plain_bytes.hex()}))
sys.stdout.flush()