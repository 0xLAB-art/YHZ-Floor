import sys, json, binascii, time

def read_input():
    data = sys.stdin.read()
    if not data:
        return {}
    return json.loads(data)

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    start = time.monotonic_ns()
    prov = read_input()
    c1_hex = prov.get('c1_hex')
    c2_hex = prov.get('c2_hex')
    if not c1_hex or not c2_hex:
        # No provisioned data; just exit
        return
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # RC4 keystream is c2 (since plaintext was all zeros)
    keystream = c2
    plaintext = xor_bytes(c1, keystream)
    plaintext_hex = binascii.hexlify(plaintext).decode()
    # Output claim
    claim = {"plaintext_hex": plaintext_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    # Optionally output timing
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end - start}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()