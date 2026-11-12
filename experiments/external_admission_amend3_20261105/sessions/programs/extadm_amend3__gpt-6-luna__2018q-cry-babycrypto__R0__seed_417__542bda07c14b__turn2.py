import base64

ciphertext = open("ciphertext.txt").read().strip()

# The flag is encoded in the ciphertext using a simple XOR with a repeating key.
# The key is "yeet" repeated.
key = b"yeet"

# Decode base64
try:
    data = base64.b64decode(ciphertext)
except Exception:
    data = binascii.a2b_base64(ciphertext)

# XOR decrypt
flag = b""
for i, byte in enumerate(data):
    flag += bytes([byte ^ key[i % len(key)]])

print(flag.decode("utf-8", errors="replace"))