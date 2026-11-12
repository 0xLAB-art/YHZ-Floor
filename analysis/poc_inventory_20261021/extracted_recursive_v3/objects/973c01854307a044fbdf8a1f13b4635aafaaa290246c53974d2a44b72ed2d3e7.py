import sys, json, base64, time
def log_err(*a):
    pass
ct = bytes.fromhex("1f183c1a58d29333f0a5212c74339c348364861f54bde3f0c64797e9b96609a776e072356f6ee8d40e3b68bd0533113ab194df815b01bc1dbf13717cbeb710d79b1bdb0599aa16a0373e967d8453d560")
iv = bytes.fromhex("c5eeb0ec979b517217fdb6fcfae12d9f")
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
# blocks = 5
def oracle_call(forged_prev: bytes, target: bytes) -> bool:
    payload = base64.b64encode(forged_prev + target).decode()
    print(json.dumps({"q": payload}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("EOF from oracle")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def decrypt_block(target: bytes) -> bytes:
    inter = bytearray(16)
    forged = bytearray(16)
    for pad_len in range(1, 17):
        idx = 16 - pad_len
        for j in range(idx+1, 16):
            forged[j] = inter[j] ^ pad_len
        found = False
        for g in range(256):
            forged[idx] = g
            ok = oracle_call(bytes(forged), target)
            if ok:
                if pad_len == 1:
                    # disambiguate 0x01 vs 0x02 0x02 etc: flip previous byte
                    saved = forged[idx-1]
                    forged[idx-1] ^= 1
                    still = oracle_call(bytes(forged), target)
                    forged[idx-1] = saved
                    if not still:
                        continue
                inter[idx] = g ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f"failed pad_len {pad_len}")
    return bytes(inter)

t0 = time.monotonic_ns()
intermediates = []
for bi, tgt in enumerate(blocks):
    im = decrypt_block(tgt)
    intermediates.append(im)
# recover plaintext
prevs = [iv] + blocks[:-1]
pt = b"".join(bytes(a ^ b for a, b in zip(im, pr)) for im, pr in zip(intermediates, prevs))
# pt should be 80 bytes with PKCS7 padding
t1 = time.monotonic_ns()
print(f"OPSPAN_NS:{t1-t0}", flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": pt.hex()}), flush=True)