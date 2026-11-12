import sys, json, base64, time
ct_hex = "6ec59a3da460be879c121d4645164ab9baf55839546451f26a5029fe28ea8bc99c0559be9d4bfdb6c9d1cd6cf731359aee1f9347530e39d2ec064a3c0e951d54cc622dc350f25f02e594e1a320412870"
iv_hex = "2df9046dfe1791d1a4199c280ffc3601"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [iv] + [ct[i:i+16] for i in range(0, len(ct), 16)]
def oracle(forged_prev, target):
    payload = base64.b64encode(forged_prev + target).decode()
    print(json.dumps({"q": payload}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("oracle EOF")
    return bool(json.loads(line).get("pad_ok"))
def recover_intermediate(target):
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
            raise RuntimeError("fail")
    return bytes(inter)
t_start = time.monotonic_ns()
pt_blocks = []
for idx in range(1, len(blocks)):
    inter = recover_intermediate(blocks[idx])
    pt = bytes(a ^ b for a, b in zip(inter, blocks[idx-1]))
    pt_blocks.append(pt)
t_end = time.monotonic_ns()
padded = b"".join(pt_blocks)
pad = padded[-1]
if 1 <= pad <= 16 and padded[-pad:] == bytes([pad])*pad:
    unpadded = padded[:-pad]
else:
    unpadded = padded
out_hex = unpadded.hex() if len(unpadded) == 64 else padded.hex()
if len(bytes.fromhex(out_hex)) not in (64, 80):
    out_hex = padded.hex()
print("OPSPAN_NS:" + str(t_end - t_start), flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": out_hex}), flush=True)