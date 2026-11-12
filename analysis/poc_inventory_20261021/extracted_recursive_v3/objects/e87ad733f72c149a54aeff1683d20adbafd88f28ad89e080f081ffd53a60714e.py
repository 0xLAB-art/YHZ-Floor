import sys, json, base64, time

ct_hex = "c00208c31a649ac32260916a7da8e5d3a29c25a70f6bd4dc2c69ff23e71a6581becb8776f1d27cab264e56e9c7e40f20dbd01feb05060f61bf77204eb3f2d7f84e3e080bb5d770849327c8075fbe5ecc"
iv_hex = "6d2d5a2e2c6fd5dac9493555d560120d"

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]

def oracle(forged_prev: bytes, target: bytes) -> bool:
    payload = base64.b64encode(forged_prev + target).decode()
    print(json.dumps({"q": payload}), flush=True)
    while True:
        line = sys.stdin.readline()
        if not line:
            raise RuntimeError("EOF from oracle")
        line=line.strip()
        if not line:
            continue
        obj = json.loads(line)
        return bool(obj.get("pad_ok"))

def recover_intermediate(target: bytes) -> bytes:
    I = bytearray(16)
    forged = bytearray(16)
    for pad_len in range(1, 17):
        pos = 16 - pad_len
        for j in range(pos+1, 16):
            forged[j] = I[j] ^ pad_len
        for j in range(0, pos):
            forged[j] = 0x00
        found = False
        for guess in range(256):
            forged[pos] = guess
            ok = oracle(bytes(forged), target)
            if ok:
                if pad_len == 1:
                    forged_verify = bytearray(forged)
                    forged_verify[14] ^= 1
                    ok2 = oracle(bytes(forged_verify), target)
                    if not ok2:
                        continue
                I[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f"failed pad_len {pad_len}")
    return bytes(I)

t0 = time.monotonic_ns()
intermediates = []
for tgt in blocks:
    intermediates.append(recover_intermediate(tgt))
t1 = time.monotonic_ns()
# reconstruct padded plaintext
pt = bytearray()
prev = iv
for idx, I in enumerate(intermediates):
    pblock = bytes(a ^ b for a, b in zip(I, prev))
    pt.extend(pblock)
    prev = blocks[idx]
print(f"OPSPAN_NS:{t1-t0}", flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": bytes(pt).hex()}), flush=True)