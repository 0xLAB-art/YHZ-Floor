import sys, json, binascii, time

def read_all_stdin():
    data = sys.stdin.read()
    return json.loads(data) if data else {}

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

prov = read_all_stdin()
c1_hex = prov.get('c1_hex')
c2_hex = prov.get('c2_hex')
if c1_hex and c2_hex:
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # c2 is the keystream (encryption of all-zero plaintext)
    start = time.monotonic_ns()
    plaintext = xor_bytes(c1, c2)
    end = time.monotonic_ns()
    plaintext_hex = binascii.hexlify(plaintext).decode()
    # Optional timing output (must appear before CLAIM)
    print(f"OPSPAN_NS:{end - start}")
    sys.stdout.flush()
    claim = {"plaintext_hex": plaintext_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()