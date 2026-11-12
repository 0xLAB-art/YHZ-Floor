import sys, json, binascii, time

def main():
    # Read provisioned JSON from stdin (may be multiple lines)
    data = sys.stdin.read()
    if not data:
        return
    prov = json.loads(data)
    c1_hex = prov['c1_hex']
    c2_hex = prov['c2_hex']
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # RC4 keystream is c2 (encryption of all-zero plaintext)
    keystream = c2
    # Recover plaintext P1 = c1 XOR keystream
    p1 = bytes(a ^ b for a, b in zip(c1, keystream))
    plaintext_hex = binascii.hexlify(p1).decode()
    claim = {"plaintext_hex": plaintext_hex}
    # Output claim as required
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    start = time.monotonic_ns()
    main()
    # Optional timing output
    print(f"OPSPAN_NS:{time.monotonic_ns() - start}")
    sys.stdout.flush()