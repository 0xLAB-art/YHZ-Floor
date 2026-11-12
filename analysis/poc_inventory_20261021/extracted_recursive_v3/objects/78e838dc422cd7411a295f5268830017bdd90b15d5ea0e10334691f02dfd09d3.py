import sys, json, base64, time
ct_hex = "49324420443d10ce58309579924019bdc720e55149c31c71abd1b8b58b71bf0e2454b8c4f9ff0c8188a9f661a641d6fe9311cc187c0637e9369f0d9d38c870ad3c9c17737ad72a1a4fba62f937da9f7a"
iv_hex = "67c5f628f658cce21f1f0fdd2919bc3a"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prev_blocks = [iv] + blocks[:-1]

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
        try:
            obj = json.loads(line)
        except:
            continue
        if "pad_ok" in obj:
            return bool(obj["pad_ok"])
        # ignore other lines

def decrypt_block(target: bytes) -> bytes:
    inter = [0]*16
    for pad in range(1, 17):
        pos = 16 - pad
        # base suffix for already known bytes
        found = None
        for g in range(256):
            forged = bytearray(16)
            # suffix
            for j in range(pos+1, 16):
                forged[j] = inter[j] ^ pad
            forged[pos] = g
            # prefix bytes 0..pos-1 leave as 0
            ok = oracle(bytes(forged), target)
            if ok:
                if pad == 1:
                    # disambiguate 0x01 vs 0x02 0x02 etc: flip byte 14
                    forged2 = bytearray(forged)
                    forged2[14] ^= 0x01
                    ok2 = oracle(bytes(forged2), target)
                    if not ok2:
                        # was 02 02 style false positive, continue
                        continue
                    found = g
                    break
                else:
                    found = g
                    break
        if found is None:
            raise RuntimeError(f"no valid padding found pad={pad}")
        inter[pos] = found ^ pad
    return bytes(inter)

t0 = time.monotonic_ns()
plain_blocks = []
for idx, (targ, prev) in enumerate(zip(blocks, prev_blocks)):
    inter = decrypt_block(targ)
    pt = bytes(a ^ b for a, b in zip(inter, prev))
    plain_blocks.append(pt)
pt_full = b"".join(plain_blocks)
t1 = time.monotonic_ns()
# strip/keep: send full padded (verifier strips) - send hex of pt_full
# But also handle: just send hex
print(f"OPSPAN_NS:{t1-t0}", flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": pt_full.hex()}), flush=True)