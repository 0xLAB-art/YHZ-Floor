import base64

data = open("encrypted", "rb").read().strip()
raw = bytes.fromhex(data.decode())

# The ciphertext is a XOR stream cipher with a repeating key.
# The key is the ASCII string "FLAG" repeated.
key = b"FLAG"

flag = b""
for i, b in enumerate(raw):
    flag += bytes([b ^ key[i % len(key)]])

print(flag.decode())