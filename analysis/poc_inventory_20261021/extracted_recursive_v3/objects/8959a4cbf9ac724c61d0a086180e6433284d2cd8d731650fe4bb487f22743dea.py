import sys, json, binascii, time

def main():
    # Read the provisioned JSON from stdin
    prov_raw = sys.stdin.read()
    if not prov_raw:
        return
    prov = json.loads(prov_raw)
    c1 = binascii.unhexlify(prov['c1_hex'])
    c2 = binascii.unhexlify(prov['c2_hex'])
    # c2 is RC4 keystream XORed with all-zero plaintext, so it equals the keystream
    keystream = c2
    # Recover plaintext P1 by XORing c1 with keystream
    p1 = bytes(a ^ b for a, b in zip(c1, keystream))
    plaintext_hex = binascii.hexlify(p1).decode()
    claim = {"plaintext_hex": plaintext_hex}
    # Output optional timing before the final claim
    print(f"OPSPAN_NS:{time.monotonic_ns()}")
    # Final claim line (must be last line)
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()