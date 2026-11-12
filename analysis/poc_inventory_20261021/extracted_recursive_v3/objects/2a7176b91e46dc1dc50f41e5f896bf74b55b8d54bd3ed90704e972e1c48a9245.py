import sys, json, binascii

def main():
    # Hardcoded provisioned ciphertexts (as given in the task description)
    c1_hex = "6235daf4805c98464406e89a3a5cd99e8b70d787f67dec8b90c095274ece0c2b569556492a73326303faba9c1b334a8345bbc261250c6e305af71b3d7b7bdf9e"
    c2_hex = "3cb71431c14120133bc04bf2ed5cca45fcc2a010cb40af7733f35a16766ebd9045d01db516ca0fdf237b963468957d330d6057d26662a6e049f40758ede3a99c"
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
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