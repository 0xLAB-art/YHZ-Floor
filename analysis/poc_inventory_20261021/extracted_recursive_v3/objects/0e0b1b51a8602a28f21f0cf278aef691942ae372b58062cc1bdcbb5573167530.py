import sys, json, binascii

def main():
    # Read the provisioned JSON from stdin
    prov_data = sys.stdin.read()
    if not prov_data:
        return
    prov = json.loads(prov_data)
    c1 = binascii.unhexlify(prov['c1_hex'])
    c2 = binascii.unhexlify(prov['c2_hex'])
    # c2 is the keystream (RC4 encryption of all-zero plaintext)
    keystream = c2
    # Recover plaintext P1 by XORing ciphertext with keystream
    p1 = bytes(a ^ b for a, b in zip(c1, keystream))
    plaintext_hex = binascii.hexlify(p1).decode()
    claim = {"plaintext_hex": plaintext_hex}
    # Output the final claim line (must be the last line printed)
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()