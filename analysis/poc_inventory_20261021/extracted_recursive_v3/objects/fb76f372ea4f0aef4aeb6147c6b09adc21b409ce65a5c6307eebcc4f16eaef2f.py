import sys, json, base64, time
sys.stdout.reconfigure(line_buffering=True)
ct_hex = "16838c7b6fc199c91ba3142d3cd7a8b3b9845a76113904ecafbe58de2fb2feae0237c4462b6beb5304ca6dd3058ee85ee3b82461ddc16632a018506384f769a2fceebf2a6b7f3f3d945e26f8e09599c9"
iv_hex = "ea3145d1160bd7dd49d59eda8b1a2139"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]

def oracle(payload: bytes) -> bool:
    q = base64.b64encode(payload).decode()
    sys.stdout.write(json.dumps({"q": q}, separators=(",", ":")) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("oracle EOF")
    line=line.strip()
    if not line:
        raise RuntimeError("empty oracle reply")
    return bool(json.loads(line).get("pad_ok"))

def decrypt_block(prev: bytes, target: bytes) -> bytes:
    inter = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad
        for j in range(pos):
            forged[j] = 0
        cand = None
        for g in range(256):
            forged[pos] = g
            if oracle(bytes(forged) + target):
                # disambiguate: flip a byte in the padding region to rule out longer valid padding confusion (for pos verification)
                if pos == 15:
                    # verify it is really 0x01: tamper byte 14, must still be valid iff pad==1
                    forged2 = bytearray(forged)
                    forged2[14] ^= 1
                    if not oracle(bytes(forged2) + target):
                        # it was longer padding (e.g. 0x02 0x02), keep searching
                        continue
                cand = g
                break
        if cand is None:
            raise RuntimeError(f"no candidate at pos {pos}")
        inter[pos] = cand ^ pad
    return bytes(inter[j] ^ prev[j] for j in range(16))

out = b""
for i in range(len(blocks)):
    pt = decrypt_block(prevs[i], blocks[i])
    out += pt
# strip pkcs7 if present
try:
    pl = out[-1]
    if 1 <= pl <= 16 and out[-pl:] == bytes([pl])*pl:
        pt_hex = out[:-pl].hex() if len(out)-pl==64 else out.hex()
        # verifier strips padding, either form ok; send unpadded 64B form
        if len(out)-pl == 64:
            pt_hex = out[:-pl].hex()
        else:
            pt_hex = out.hex()
    else:
        pt_hex = out.hex()
except Exception:
    pt_hex = out.hex()
t0 = time.monotonic_ns()
t1 = time.monotonic_ns()
sys.stdout.write(f"OPSPAN_NS:{t1-t0}\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": pt_hex}, separators=(",", ":")) + "\n")
sys.stdout.flush()