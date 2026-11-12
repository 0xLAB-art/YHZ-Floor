import sys, json, base64
ct_hex = "e5e86daa50de8d13c759ae9c1a41f19214615b824dc277c772b7acff3f02c012228642fd995ab7f9a5d61869e3ad962e8b9a0464a185204692fa99c1b5af830b29485773aa7c59d6fcd82f58de3fe3ab"
iv_hex = "8e97e21ea8cc23e00f3b24caff6e14ad"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]

def query(forged_prev, target):
    payload = base64.b64encode(forged_prev + target).decode()
    print(json.dumps({"q": payload}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("oracle EOF")
    return json.loads(line).get("pad_ok") is True

def decrypt_block(target):
    I = [0]*16
    pos = 15
    found = None
    for guess in range(256):
        f = bytearray(16)
        f[pos] = guess
        if query(bytes(f), target):
            f2 = bytearray(f)
            f2[14] ^= 1
            if query(bytes(f2), target):
                found = guess
                break
            else:
                continue
    if found is None:
        raise RuntimeError("failed last byte")
    I[15] = found ^ 0x01
    for pad_len in range(2, 17):
        pos = 16 - pad_len
        found2 = None
        for guess in range(256):
            f = bytearray(16)
            for k in range(pos+1, 16):
                f[k] = I[k] ^ pad_len
            f[pos] = guess
            if query(bytes(f), target):
                found2 = guess
                break
        if found2 is None:
            raise RuntimeError(f"failed pos {pos}")
        I[pos] = found2 ^ pad_len
    return bytes(I)

intermediates = []
for t in blocks:
    intermediates.append(decrypt_block(t))
pt_padded = b"".join(bytes(a ^ b for a, b in zip(inter, prev)) for inter, prev in zip(intermediates, prevs))
pad = pt_padded[-1]
if 1 <= pad <= 16 and pt_padded[-pad:] == bytes([pad])*pad:
    pt = pt_padded[:-pad]
else:
    pt = pt_padded
print("CLAIM:" + json.dumps({"plaintext_hex": pt.hex()}), flush=True)