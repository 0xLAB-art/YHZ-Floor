import sys, json, binascii

def main():
    # Read provisioned material from stdin
    data = json.load(sys.stdin)
    c1 = binascii.unhexlify(data["c1_hex"])
    c2 = binascii.unhexlify(data["c2_hex"])
    # Recover plaintext P1 by XORing ciphertexts (c2 is the keystream)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    claim = {"plaintext2_hex": binascii.hexlify(p1).decode()}
    # Output final claim
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()