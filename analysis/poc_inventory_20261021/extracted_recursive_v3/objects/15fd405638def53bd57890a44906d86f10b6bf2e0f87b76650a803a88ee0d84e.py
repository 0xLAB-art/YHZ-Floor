import sys, json, base64, time
ct = bytes.fromhex("503a132d9717d2cd67abfe0b68d00655d235ab309beccfad6ffecae446e62ed2d881ebf673b773d9e24eeed0155c2e9ba8cd2f35a6fa33182e181a72e353ad027d411c5b7b68b2c332c58f5a3356d26a")
iv = bytes.fromhex("f4ce10ffb43862b7ee606f2777954b0d")
ct_blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
# only first 4 blocks are message (64 bytes), last block is PKCS7 0x10 padding
targets = ct_blocks[:4]
orig_prevs = [iv] + ct_blocks[:3]

def oracle(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    s = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": s}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    while line is not None and line.strip() == "":
        line = sys.stdin.readline()
    if not line:
        return False
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def recover_intermediate(target: bytes):
    I = [0]*16
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for k in range(pos+1, 16):
            forged[k] = I[k] ^ pad
        for k in range(pos):
            forged[k] = 0
        found = None
        for guess in range(256):
            forged[pos] = guess
            ok = oracle(bytes(forged), target)
            if ok:
                if pos == 15:
                    # verify it is really pad 01, not longer pad 02..: flip byte 14
                    saved14 = forged[14]
                    forged[14] = saved14 ^ 1
                    ok2 = oracle(bytes(forged), target)
                    forged[14] = saved14
                    if ok2:
                        found = guess
                        break
                    else:
                        continue
                else:
                    found = guess
                    break
        if found is None:
            raise Exception(f"failed pos {pos}")
        I[pos] = found ^ pad
    return bytes(I)

t_start = time.monotonic_ns()
plain_blocks = []
for idx, tgt in enumerate(targets):
    Im = recover_intermediate(tgt)
    P = bytes([Im[j] ^ orig_prevs[idx][j] for j in range(16)])
    plain_blocks.append(P)
plaintext = b"".join(plain_blocks)
# build 80-byte padded version (append known padding block 0x10*16)
# to avoid ambiguity, claim the 64-byte message; verifier strips if present
t_end = time.monotonic_ns()
# also construct padded for safety: padded = plaintext + bytes([16]*16)
hex64 = plaintext.hex()
try:
    sys.stdout.write(f"OPSPAN_NS:{t_end - t_start}\n")
    sys.stdout.flush()
except Exception:
    pass
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": hex64}) + "\n")
sys.stdout.flush()