import sys, json, binascii

def read_input():
    data = sys.stdin.read()
    if not data:
        return {}
    return json.loads(data)

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

prov = read_input()
c1_hex = prov.get('c1_hex')
c2_hex = prov.get('c2_hex')
if c1_hex and c2_hex:
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # c2 is keystream (encryption of all-zero plaintext)
    plaintext = xor_bytes(c1, c2)
    plaintext_hex = binascii.hexlify(plaintext).decode()
    claim = {"plaintext_hex": plaintext_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()