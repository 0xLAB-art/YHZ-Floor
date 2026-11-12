import sys, json, binascii

def main():
    # Provisioned ciphertexts (hardcoded from task description)
    c1_hex = "41dffe240702bc3b7fdc816cb313bfa50a573dccd0e869471e8c325809d2ff2178b8d17f08a4018528d81e19fc34b44f20e2daa5d10bfd5c01a5fe1a1a89bdea"
    c2_hex = "179e3d04af66c306951d54ca3d268e74f5697b5f21afdeb51dcbbb9fa76647104a2b2055d3d1faa85d4924a164e9e7b488bafc2947e8307b972522c3352579e7"
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # Recover plaintext: c1 = keystream XOR P1, c2 = keystream (since plaintext was zeros)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    p1_hex = binascii.hexlify(p1).decode()
    claim = {"plaintext2_hex": p1_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()