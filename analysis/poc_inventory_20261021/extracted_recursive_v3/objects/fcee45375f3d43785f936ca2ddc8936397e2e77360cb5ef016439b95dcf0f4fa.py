import sys, json, binascii

def main():
    # Provisioned ciphertexts (hex strings) from the task description
    c1_hex = "b572861c61c30974565a6a02a30fdfbf7e5d3160a42b77dc1aae41f57e71b6908e858a0f203a1fa8e7d4fbd15e8e5b8a7d35e4d043f43895232f54481b85fb9c"
    c2_hex = "4828636ef2629c72ea7b290531653d21a89c35644cb6607e4906d7eae39eeaecc16a44c4454c6751bb2a02821a3ee39778aaf3a132880a0b12f6b663a2c6b3d5"
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # Recover plaintext P1 by XORing ciphertexts (c2 is the keystream for a zero plaintext)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    claim = {"plaintext2_hex": binascii.hexlify(p1).decode()}
    # Output final claim
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()