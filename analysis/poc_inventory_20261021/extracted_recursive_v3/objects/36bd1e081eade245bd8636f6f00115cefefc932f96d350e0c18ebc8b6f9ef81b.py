import sys, json, base64, time
ct_hex = "890ed6b8106221edcf98d9fb95faa866c51840045b4431a5a922da2289333d72b3e38463c56f4dc45e4c5b7d4c813bf698b8db959247a582f6beebf24bd75cbe28a239755a1cc5e600eed4aa9f27c10a"
iv_hex = "dc03e26b8c8ea0f11e2420d44fa1ed47"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
# blocks[0..4] are ciphertext blocks, prev for blocks[0] is iv
prevs = [iv] + blocks[:-1]

def oracle_query(forged_prev: bytes, target: bytes):
    q = base64.b64encode(forged_prev + target).decode()
    sys.stdout.write(json.dumps({"q": q}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    while line is not None and line.strip() == "":
        line = sys.stdin.readline()
    if not line:
        raise RuntimeError("no oracle reply")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def recover_intermediate(target: bytes):
    inter = bytearray(16)
    forged = bytearray(16)
    # init prefix to zeros
    for b in range(16):
        forged[b] = 0
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad
        found = None
        for guess in range(256):
            forged[pos] = guess
            ok = oracle_query(bytes(forged), target)
            if ok:
                if pad == 1:
                    # disambiguate: flip byte 14 (pos 14 is prefix here)
                    # save original byte 14
                    orig14 = forged[14]
                    forged[14] = orig14 ^ 1
                    ok2 = oracle_query(bytes(forged), target)
                    forged[14] = orig14
                    if not ok2:
                        continue
                found = guess
                break
        if found is None:
            raise RuntimeError(f"no valid padding found at pos {pos}")
        inter[pos] = found ^ pad
    return bytes(inter)

t0 = time.monotonic_ns()
plaintext_blocks = []
for idx in range(len(blocks)):
    target = blocks[idx]
    prev = prevs[idx]
    inter = recover_intermediate(target)
    pt = bytes(a ^ b for a, b in zip(inter, prev))
    plaintext_blocks.append(pt)
    print(f"recovered block {idx}: {pt.hex()}", file=sys.stderr)
    sys.stderr.flush()
pt_full = b"".join(plaintext_blocks)
# strip PKCS7 if present for claim (verifier also strips, so either ok)
# keep full if last block is padding 0x10*16 -> strip to 64 bytes
n = pt_full[-1]
if 1 <= n <= 16 and pt_full[-n:] == bytes([n])*n:
    pt_unpadded = pt_full[:-n]
else:
    pt_unpadded = pt_full
# claim unpadded 64 bytes (or full if strip failed)
claim_hex = pt_unpadded.hex()
# fallback: if unpadded length != 64, claim full
if len(pt_unpadded) != 64:
    # if full is 80, claim full; verifier strips
    claim_hex = pt_full.hex()
t1 = time.monotonic_ns()
# report opspan as duration of last block recovery approx: use total
sys.stdout.write(f"OPSPAN_NS:{t1-t0}\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": claim_hex}) + "\n")
sys.stdout.flush()