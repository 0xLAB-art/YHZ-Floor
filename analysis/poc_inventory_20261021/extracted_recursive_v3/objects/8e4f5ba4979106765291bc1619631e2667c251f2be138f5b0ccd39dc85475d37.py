import sys, json, base64, time
ct_hex = "4a56043aafdab687b845e5e83866d3998a029d8983c19441cd5e00bdb5c608d95f9981f01256e6e889bb76e9c592bd37fd16475b77d788ff7b2e37c12831f6c7e0743350ddf0a38fc647f5d41c3dce55"
iv_hex = "84944aaacfa463714374001e6e8e5bcc"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prev_blocks = [iv] + blocks[:-1]

def query(forged_prev: bytes, target: bytes) -> bool:
    payload = base64.b64encode(forged_prev + target).decode()
    print(json.dumps({"q": payload}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("no oracle reply")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def recover_intermediate(target: bytes) -> bytes:
    inter = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for k in range(pos+1, 16):
            forged[k] = inter[k] ^ pad
        found = None
        for g in range(256):
            forged[pos] = g ^ pad
            ok = query(bytes(forged), target)
            if ok:
                if pad == 1:
                    orig = forged[pos-1]
                    forged[pos-1] = orig ^ 0x01
                    ok2 = query(bytes(forged), target)
                    forged[pos-1] = orig
                    if not ok2:
                        continue
                found = g
                break
        if found is None:
            raise RuntimeError(f"failed pos {pos}")
        inter[pos] = found
    return bytes(inter)

t0 = time.monotonic_ns()
plain_blocks = []
for idx, tgt in enumerate(blocks):
    inter = recover_intermediate(tgt)
    prev = prev_blocks[idx]
    pt = bytes(a ^ b for a, b in zip(inter, prev))
    plain_blocks.append(pt)
full = b"".join(plain_blocks)
t1 = time.monotonic_ns()
# strip pkcs7 for validation, but claim can be full or stripped; send stripped if valid
padlen = full[-1]
if 1 <= padlen <= 16 and full[-padlen:] == bytes([padlen])*padlen:
    unpadded = full[:-padlen]
else:
    unpadded = full
print(f"OPSPAN_NS:{t1-t0}", flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": unpadded.hex()}), flush=True)