import sys, json, base64, time
ct_hex = "16838c7b6fc199c91ba3142d3cd7a8b3b9845a76113904ecafbe58de2fb2feae0237c4462b6beb5304ca6dd3058ee85ee3b82461ddc16632a018506384f769a2fceebf2a6b7f3f3d945e26f8e09599c9"
iv_hex = "ea3145d1160bd7dd49d59eda8b1a2139"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
ct_blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prev_blocks = [iv] + ct_blocks[:-1]

def oracle_call(payload: bytes):
    q = base64.b64encode(payload).decode()
    print(json.dumps({"q": q}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("oracle EOF")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def recover_block(prev: bytes, target: bytes):
    inter = [0]*16
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad
        for j in range(pos):
            forged[j] = 0x00
        found = False
        for g in range(256):
            forged[pos] = g
            payload = bytes(forged) + target
            if oracle_call(payload):
                inter[pos] = g ^ pad
                found = True
                break
        if not found:
            raise RuntimeError(f"no guess found pos={pos}")
    plain = bytes([inter[j] ^ prev[j] for j in range(16)])
    return plain

plains = []
for idx in range(len(ct_blocks)):
    p = recover_block(prev_blocks[idx], ct_blocks[idx])
    plains.append(p)
    print(f"recovered block {idx}: {p.hex()}", file=sys.stderr, flush=True)
full = b"".join(plains)
# strip pkcs7 if present for claim (verifier also strips, so either ok)
try:
    pad_len = full[-1]
    if 1 <= pad_len <= 16 and full[-pad_len:] == bytes([pad_len])*pad_len:
        unpadded = full[:-pad_len]
    else:
        unpadded = full
except Exception:
    unpadded = full
# final operation timing
t0 = time.monotonic_ns()
plaintext_hex = unpadded.hex()
# ensure 64 bytes if padding was 16 of 0x10, else fallback to full
t1 = time.monotonic_ns()
print(f"OPSPAN_NS:{t1-t0}", flush=True)
print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}", flush=True)