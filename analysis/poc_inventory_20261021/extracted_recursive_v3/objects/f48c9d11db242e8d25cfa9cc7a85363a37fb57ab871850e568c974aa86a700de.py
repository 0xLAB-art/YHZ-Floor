import sys, json, base64

CT = bytes.fromhex("13fb1ccde2ad55a96324605c12c2b363158d073b8cafbaa92d004fcba8ac53b014d908eb08b809d99d58c2a9ab77cc13dfc920050adb1eb61b328193dfad6748b86c0d9ac4424ee212f2b36c53392c9c")
IV = bytes.fromhex("2abbc2feb515e7ce0a29dcb72ca8ad6f")

def query(prev, target):
    line = json.dumps({"q": base64.b64encode(prev + target).decode()})
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
    resp = sys.stdin.readline()
    resp = resp.strip()
    if not resp:
        raise RuntimeError("no reply")
    obj = json.loads(resp)
    return bool(obj.get("pad_ok"))

blocks = [CT[i:i+16] for i in range(0, len(CT), 16)]

plain = b""
prev_block = IV

for bi in range(len(blocks)):
    target = blocks[bi]
    found = None
    for padlen in range(1, 17):
        found = None
        base = bytearray(16)
        # intermediate = P_block ^ pad bytes for known tail
        inter = bytearray(16)
        for j in range(16 - padlen, 16):
            inter[j] = plain[j] ^ padlen
        for k in range(256):
            cand = bytearray(16)
            cand[16 - padlen] = k
            for j in range(16 - padlen + 1, 16):
                cand[j] = inter[j] ^ prev_block[j]
            if query(bytes(cand), target):
                found = (bytes(cand), k)
                break
        if found:
            break
    if not found:
        raise RuntimeError("no valid pad at block %d" % bi)
    cand, k = found
    rec = bytearray(16)
    rec[16 - padlen] = k ^ padlen
    for j in range(16 - padlen + 1, 16):
        rec[j] = inter[j] ^ prev_block[j]
    plain = plain + bytes(rec)
    prev_block = target

sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": plain.hex()}) + "\n")
sys.stdout.flush()