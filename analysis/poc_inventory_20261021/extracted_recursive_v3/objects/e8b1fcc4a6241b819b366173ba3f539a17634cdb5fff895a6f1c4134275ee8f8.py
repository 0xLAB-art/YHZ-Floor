import sys, json, base64, time
ct_hex = "6ec59a3da460be879c121d4645164ab9baf55839546451f26a5029fe28ea8bc99c0559be9d4bfdb6c9d1cd6cf731359aee1f9347530e39d2ec064a3c0e951d54cc622dc350f25f02e594e1a320412870"
iv_hex = "2df9046dfe1791d1a4199c280ffc3601"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [iv] + [ct[i:i+16] for i in range(0, len(ct), 16)]
# blocks[0]=iv, blocks[1..5]=ciphertext
def oracle(forged_prev: bytes, target: bytes) -> bool:
    payload = base64.b64encode(forged_prev + target).decode()
    print(json.dumps({"q": payload}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("oracle EOF")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def recover_intermediate(target: bytes) -> bytes:
    inter = bytearray(16)
    forged = bytearray(16)
    for pad_len in range(1, 17):
        pos = 16 - pad_len
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad_len
        found = False
        for guess in range(256):
            forged[pos] = guess
            ok = oracle(bytes(forged), target)
            if ok:
                if pad_len == 1 and pos > 0:
                    forged2 = bytearray(forged)
                    forged2[pos-1] ^= 1
                    ok2 = oracle(bytes(forged2), target)
                    if not ok2:
                        continue
                inter[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f"failed pad_len {pad_len}")
    return bytes(inter)

t_start = time.monotonic_ns()
pt_blocks = []
for idx in range(1, len(blocks)):
    target = blocks[idx]
    prev = blocks[idx-1]
    inter = recover_intermediate(target)
    pt = bytes(a ^ b for a, b in zip(inter, prev))
    pt_blocks.append(pt)
    print(f"recovered block {idx}: {pt.hex()}", file=sys.stderr, flush=True)
t_end = time.monotonic_ns()
padded = b"".join(pt_blocks)
# try strip pkcs7
try:
    pad = padded[-1]
    if 1 <= pad <= 16 and padded[-pad:] == bytes([pad])*pad:
        unpadded = padded[:-pad]
    else:
        unpadded = padded
 except Exception:
    unpadded = padded
# verifier strips padding if present, so either is ok; send unpadded if length 64 else padded
out_hex = unpadded.hex() if len(unpadded)==64 else padded.hex()
# fallback: if unpadded len not 64 but padded len 80, send padded
if len(bytes.fromhex(out_hex)) not in (64,80):
    out_hex = padded.hex()
print(f"OPSPAN_NS:{t_end - t_start}", flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": out_hex}), flush=True)