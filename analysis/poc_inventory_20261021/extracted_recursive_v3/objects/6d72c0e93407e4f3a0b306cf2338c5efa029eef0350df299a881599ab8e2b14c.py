import sys, json, base64, time
ct_hex = "83679b10525a6878558e2c8dd4c2e75004624a7baac05327e3fe9e0df1523136d28882b3a315f688a6ec50b9857d164757ce803c58cde52554fd52d0f6f5681ae772eba7cb6c543b0048b9573bb536ad"
iv_hex = "d026215840190e7066e27c739f3ba211"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
ct_blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prev_blocks = [iv] + ct_blocks[:-1]
# we need first 4 blocks (64 bytes message); ct has 5 blocks, last is padding
targets = ct_blocks[:4]
prevs = prev_blocks[:4]

def oracle(forged_prev: bytes, target: bytes) -> bool:
    payload = base64.b64encode(forged_prev + target).decode()
    sys.stdout.write(json.dumps({"q": payload}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise EOFError("no reply from oracle")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def recover_intermediate(target: bytes) -> bytes:
    I = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        found = None
        for guess in range(256):
            forged = bytearray(16)
            for j in range(pos+1, 16):
                forged[j] = I[j] ^ pad
            forged[pos] = guess
            # prefix 0..pos-1 stays zero
            try:
                ok = oracle(bytes(forged), target)
            except EOFError:
                raise
            if ok:
                if pos == 15:
                    # disambiguate 0x01 vs longer padding: flip byte 14
                    forged2 = bytearray(forged)
                    forged2[14] ^= 1
                    ok2 = oracle(bytes(forged2), target)
                    if not ok2:
                        continue
                found = guess
                break
        if found is None:
            raise RuntimeError(f"failed to recover byte {pos}")
        I[pos] = found ^ pad
    return bytes(I)

plaintext_blocks = []
for idx, (tgt, prv) in enumerate(zip(targets, prevs)):
    inter = recover_intermediate(tgt)
    pt = bytes(a ^ b for a, b in zip(inter, prv))
    plaintext_blocks.append(pt)

t0 = time.monotonic_ns()
plaintext = b"".join(plaintext_blocks)
t1 = time.monotonic_ns()
sys.stdout.write(f"OPSPAN_NS:{t1-t0}\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": plaintext.hex()}) + "\n")
sys.stdout.flush()