import sys, json, base64, time
ct_hex = "ee0b7104daa977e1e0a569e8d0cd3fab6f1d615090b7a2a5b08cf2e37874cd6d45390a1f0816ab2685c8e224248343d5c3467daa8dba078f8415d0eeb59e968bb619d0a6a9dd7de14208fd731876eff4"
iv_hex = "22da83b7a1b1ffca86c9858602190b37"
start_ns = time.monotonic_ns()
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]

def ask(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("EOF from oracle")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def decrypt_target(target: bytes) -> bytes:
    inter = bytearray(16)
    forged = bytearray(16)
    for pad in range(1, 17):
        pos = 16 - pad
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad
        for j in range(pos):
            forged[j] = 0x00
        found = False
        for g in range(256):
            forged[pos] = g
            ok = ask(bytes(forged), target)
            if ok:
                inter[pos] = g ^ pad
                found = True
                break
        if not found:
            raise RuntimeError(f"no valid guess for pad {pad}")
    return bytes(inter)

pt_blocks = []
for tgt, prv in zip(blocks, prevs):
    inter = decrypt_target(tgt)
    pt = bytes(a ^ b for a, b in zip(inter, prv))
    pt_blocks.append(pt)
padded = b"".join(pt_blocks)
plaintext_hex = padded.hex()
end_ns = time.monotonic_ns()
try:
    sys.stdout.write(f"OPSPAN_NS:{end_ns - start_ns}\n")
    sys.stdout.flush()
except Exception:
    pass
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": plaintext_hex}) + "\n")
sys.stdout.flush()