import base64

data = open("encrypted", "rb").read()
raw = base64.b64decode(data)

# The ciphertext is a hex string; decode to bytes.
hex_bytes = bytes.fromhex(raw.decode())

# XOR with a repeating key derived from the pattern.
# The structure suggests a simple XOR with a key of length 16.
key = b"FLAG{"

# Try to find the key by analyzing the structure.
# The first part looks like a header, then the flag.
# Let's try XORing with common keys.

for k_len in range(1, 33):
    key = bytearray(k_len)
    # Use the known structure: the message likely starts with a known prefix
    # and the flag format is FLAG{...}
    # Try to derive key from the assumption that the plaintext contains 'FLAG{'
    try:
        # Assume plaintext starts with 'FLAG{' at some offset
        for i in range(k_len):
            # We don't know the exact position, so try multiple positions
            pass
    except:
        pass

# Simpler approach: the ciphertext appears to be XOR with a repeating key.
# Let's try to find the key by assuming the plaintext contains 'FLAG{'

ciphertext = hex_bytes

# Try all possible key lengths and find the one that produces 'FLAG{'
best = None
for k_len in range(1, 20):
    # Compute key by assuming plaintext contains 'FLAG{' at position 0
    # Actually, let's try to find the key by using the known plaintext 'FLAG{'
    # The flag format is FLAG{...}
    # Let's assume the plaintext starts with 'FLAG{'
    key = bytearray(k_len)
    for i in range(k_len):
        if i < len(b"FLAG{"):
            key[i] = ciphertext[i] ^ b"FLAG{"[i]
    # Verify
    plaintext = bytearray(len(ciphertext))
    for i in range(len(ciphertext)):
        plaintext[i] = ciphertext[i] ^ key[i % k_len]
    try:
        pt_str = plaintext.decode("ascii")
        if "FLAG{" in pt_str:
            best = pt_str
            break
    except:
        pass

if best:
    print(best)
else:
    # Fallback: try other known prefixes
    for prefix in [b"CTF{", b"flag{", b"{", b"secret"]:
        for k_len in range(1, 20):
            key = bytearray(k_len)
            for i in range(k_len):
                if i < len(prefix):
                    key[i] = ciphertext[i] ^ prefix[i]
            plaintext = bytearray(len(ciphertext))
            for i in range(len(ciphertext)):
                plaintext[i] = ciphertext[i] ^ key[i % k_len]
            try:
                pt_str = plaintext.decode("ascii")
                if prefix.decode() in pt_str:
                    print(pt_str)
                    break
            except:
                pass
        if best:
            break