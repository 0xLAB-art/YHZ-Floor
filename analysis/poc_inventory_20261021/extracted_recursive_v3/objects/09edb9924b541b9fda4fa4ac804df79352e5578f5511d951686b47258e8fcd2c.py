import sys, json, base64
ct_hex = "0f3aef70198362f9a3603480f7e11b85771e419a9e5831ad4431557f75b7882ec6a77ac14a11688540b6378aebb4f429abf379283d7250f9cf52524c903e8471093ddb097f6bbe023b41740c90dbb4f2"
iv_hex = "9fe33b554fa7ce8d7abe63247508bc91"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
qcount = 0
def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    global qcount
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    qcount += 1
    while True:
        line = sys.stdin.readline()
        if not line:
            raise EOFError("oracle EOF")
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if "pad_ok" in obj:
            return bool(obj["pad_ok"])
        # ignore other lines
def decrypt_block(target: bytes) -> bytes:
    I = bytearray(16)
    F = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for k in range(pos+1, 16):
            F[k] = I[k] ^ pad
        for k in range(pos):
            F[k] = 0x00
        found = None
        for g in range(256):
            F[pos] = g
            ok = oracle_query(bytes(F), target)
            if ok:
                if pad == 1:
                    F2 = bytearray(F)
                    F2[14] ^= 0x01
                    ok2 = oracle_query(bytes(F2), target)
                    if not ok2:
                        continue
                found = g
                break
        if found is None:
            raise Exception(f"failed pos {pos}")
        I[pos] = found ^ pad
    return bytes(I)
intermediates = []
for idx, tgt in enumerate(blocks):
    ib = decrypt_block(tgt)
    intermediates.append(ib)
prev = iv
plain_blocks = []
for i, ib in enumerate(intermediates):
    c_prev = prev
    pt = bytes(a ^ b for a, b in zip(ib, c_prev))
    plain_blocks.append(pt)
    prev = blocks[i]
full = b"".join(plain_blocks)
# strip pkcs7 if present for claim (verifier also strips, either ok)
# send unpadded 64-byte message
pad_len = full[-1]
if 1 <= pad_len <= 16 and full[-pad_len:] == bytes([pad_len])*pad_len:
    unpadded = full[:-pad_len]
else:
    unpadded = full
# fallback: if full is 80 bytes with last block 0x10*16, unpadded is first 64
hex_out = unpadded.hex()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": hex_out}) + "\n")
sys.stdout.flush()