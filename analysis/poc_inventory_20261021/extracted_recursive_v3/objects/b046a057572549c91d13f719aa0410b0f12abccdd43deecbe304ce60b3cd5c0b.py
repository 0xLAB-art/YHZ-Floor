import sys, json, base64
ct_hex="3fd10a5301fdf0c7f97105fe5046690a454fb42401259a652039b9683964d767830156ca732df66cb548da2c9739f1ce4312a7b3cc276cb19b6fe282a16a5c495defdbb12d744dc85dcf3fd27db9f55e"
iv_hex="2a15ae00d02ea4dda961715820d4f345"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]

def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    payload = bytes(forged_prev) + bytes(target)
    b64 = base64.b64encode(payload).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("no response from oracle")
    obj = json.loads(line)
    return bool(obj.get("pad_ok"))

def decrypt_block(target: bytes) -> bytes:
    inter = [0]*16
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for k in range(pos+1, 16):
            forged[k] = inter[k] ^ pad
        found = False
        for guess in range(256):
            forged[pos] = guess
            ok = oracle_query(bytes(forged), target)
            if ok:
                if pos == 15:
                    orig14 = forged[14]
                    forged[14] ^= 1
                    still = oracle_query(bytes(forged), target)
                    forged[14] = orig14
                    if not still:
                        continue
                inter[pos] = guess ^ pad
                found = True
                break
        if not found:
            raise RuntimeError(f"failed pos {pos}")
    return bytes(inter)

pt = b""
for idx, tgt in enumerate(blocks):
    sys.stderr.write(f"decrypting block {idx}\n")
    sys.stderr.flush()
    inter = decrypt_block(tgt)
    prev = iv if idx == 0 else blocks[idx-1]
    pblk = bytes(a ^ b for a, b in zip(inter, prev))
    pt += pblk
pt_hex = pt.hex()
sys.stderr.write(f"recovered {pt_hex}\n")
sys.stderr.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": pt_hex}) + "\n")
sys.stdout.flush()