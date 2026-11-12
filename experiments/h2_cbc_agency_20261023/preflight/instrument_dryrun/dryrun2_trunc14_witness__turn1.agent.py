
import json, sys
public = json.load(open(sys.argv[1]))
c = bytes.fromhex(public["ciphertext_hex"])
c0 = c[:16]
d1 = bytearray(16)
def q(h):
    import oracle
    return oracle.query(h)
for pos in range(15, -1, -1):
    pad = 16 - pos
    base = bytearray(16)
    for j in range(pos + 1, 16):
        base[j] = d1[j] ^ pad
    found = None
    for g in range(256):
        probe = bytearray(base); probe[pos] = g
        if q(probe.hex()):
            if pos == 15:
                chk = bytearray(probe); chk[14] ^= 1
                if not q(chk.hex()):
                    continue
            found = g ^ pad
            break
    d1[pos] = found
p2 = bytes(a ^ b for a, b in zip(d1, c0))
print(json.dumps({"plaintext_hex": p2[:14].hex()}))
