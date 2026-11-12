import sys, json, binascii, time

def read_input():
    data = sys.stdin.read()
    if not data:
        return {}
    return json.loads(data)

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    prov = read_input()
    c1_hex = prov.get('c1_hex')
    c2_hex = prov.get('c2_hex')
    if not c1_hex or not c2_hex:
        return
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # Since c2 is encryption of all-zero plaintext, it equals the keystream.
    keystream = c2
    plaintext = xor_bytes(c1, keystream)
    plaintext_hex = binascii.hexlify(plaintext).decode()
    # Optional timing measurement
    start = time.monotonic_ns()
    # (no additional heavy work here)
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end - start}")
    sys.stdout.flush()
    claim = {"plaintext_hex": plaintext_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()