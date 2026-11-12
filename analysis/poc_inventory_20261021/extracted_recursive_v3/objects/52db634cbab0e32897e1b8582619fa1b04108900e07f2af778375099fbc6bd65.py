import base64, json, sys, time
ct_hex = "0a8ae66fe7e41260fd3a025a0dfb31ecf544d2e0f141bb0a4b71ef5fb138d28ec89513425b868f13ebb10c8a9158af4bd119c5f3e0b14ac7fadb3805012e1bfa18da0dbcf3cffae17ec0466896bf7326"
iv_hex = "0892f9219c7c1fbb4e7ed41697b63342"

def oracle_query(forged_bytes, target_bytes):
    data = bytes(forged_bytes) + bytes(target_bytes)
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("EOF from oracle")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def recover_intermediate(target):
    inter = bytearray(16)
    forged = bytearray(16)
    for pad_len in range(1, 17):
        pos = 16 - pad_len
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad_len
        for k in range(pos):
            forged[k] = 0
        found = False
        for cand in range(256):
            forged[pos] = cand
            ok = oracle_query(forged, target)
            if ok:
                if pad_len == 1:
                    check = bytearray(forged)
                    check[pos-1] ^= 1
                    ok2 = oracle_query(check, target)
                    if not ok2:
                        continue
                inter[pos] = cand ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f"failed pad_len {pad_len}")
    return bytes(inter)

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prev_list = [iv] + blocks[:-1]
inters = []
for bidx, tgt in enumerate(blocks):
    ii = recover_intermediate(tgt)
    inters.append(ii)
t0 = time.monotonic_ns()
pt_padded = b"".join(bytes(inters[i][j] ^ prev_list[i][j] for j in range(16)) for i in range(len(blocks)))
# strip pkcs7 if present
pt = pt_padded
if len(pt) > 0:
    n = pt[-1]
    if 1 <= n <= 16 and pt[-n:] == bytes([n])*n:
        pt = pt[:-n]
t1 = time.monotonic_ns()
ops = t1 - t0
sys.stdout.write(f"OPSPAN_NS:{ops}\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": pt.hex()}) + "\n")
sys.stdout.flush()