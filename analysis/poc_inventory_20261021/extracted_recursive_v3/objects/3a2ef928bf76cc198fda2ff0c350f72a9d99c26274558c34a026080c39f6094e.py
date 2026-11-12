import sys, json, base64, time
ct_hex = "4d990f713daecefb2c4903086fe0fff719a639e6e3d8f8bf43e3b8ec0e5cf4466bc2ab9753c2d2e6760791a5df802e316c7f677cbc2adf6135f91b0ba68298ab37d076f68629e1ba1fca8ee3e64b148a"
iv_hex = "ea5130a66a4e3d81a66fdc5a83d956f5"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prev_blocks = [iv] + blocks[:-1]
targets = blocks

def query(forged_prev: bytes, target: bytes):
    payload = forged_prev + target
    q = base64.b64encode(payload).decode()
    sys.stdout.write(json.dumps({"q": q}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("EOF from oracle")
    resp = json.loads(line)
    return bool(resp.get("pad_ok"))

def recover_intermediate(target: bytes):
    I = bytearray(16)
    forged = bytearray(16)
    # initialize to zeros
    for pos in range(15, -1, -1):
        n = 16 - pos
        for j in range(pos+1, 16):
            forged[j] = I[j] ^ n
        found = False
        for guess in range(256):
            forged[pos] = guess
            ok = query(bytes(forged), target)
            if ok:
                if n == 1:
                    # disambiguate: flip byte 14 (or byte 0 if pos==14, but pos==15 here)
                    check_idx = 14 if pos == 15 else 15
                    # ensure check_idx != pos
                    if check_idx == pos:
                        check_idx = 0
                    saved = forged[check_idx]
                    forged[check_idx] ^= 1
                    ok2 = query(bytes(forged), target)
                    forged[check_idx] = saved
                    if not ok2:
                        # false positive due to longer padding, continue searching
                        continue
                I[pos] = guess ^ n
                found = True
                break
        if not found:
            raise RuntimeError(f"failed pos {pos}")
    return bytes(I)

t0 = time.monotonic_ns()
intermediates = []
for tgt in targets:
    Im = recover_intermediate(tgt)
    intermediates.append(Im)
t1 = time.monotonic_ns()
# decrypt
padded = b"".join(bytes(a ^ b for a, b in zip(Im, pb)) for Im, pb in zip(intermediates, prev_blocks))
# validate/strip PKCS7
pad_len = padded[-1]
if 1 <= pad_len <= 16 and padded[-pad_len:] == bytes([pad_len])*pad_len:
    unpadded = padded[:-pad_len]
else:
    unpadded = padded
sys.stdout.write(f"OPSPAN_NS:{(t1-t0)}\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": unpadded.hex()}) + "\n")
sys.stdout.flush()