with open("encrypted", "r", encoding="ascii") as f:
    ciphertext = bytes.fromhex(f.read())

key = b"A quart jar of oil mixed with zinc oxide makes a very bright paint|"
plaintext = bytes(byte ^ key[i % len(key)] for i, byte in enumerate(ciphertext))
start = plaintext.index(b"flag{")
end = plaintext.index(b"}", start) + 1
print(plaintext[start:end].decode("ascii"))
