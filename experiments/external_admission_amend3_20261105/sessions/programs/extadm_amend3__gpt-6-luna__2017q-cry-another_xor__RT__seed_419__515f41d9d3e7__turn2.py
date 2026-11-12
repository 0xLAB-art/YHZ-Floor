import base64

data = base64.b64decode(open("encrypted", "rb").read())

# The ciphertext is a sequence of length-prefixed blocks.
# Each block: 1 byte length, then `length` bytes of payload.
# Payloads are XORed with a repeating key derived from the ASCII string "FLAG".

key = b"FLAG"
result = bytearray()

i = 0
while i < len(data):
    length = data[i]
    i += 1
    block = data[i:i+length]
    i += length
    # XOR block with repeating key
    decrypted = bytes(block[j] ^ key[j % len(key)] for j in range(len(block)))
    result.extend(decrypted)

print(result.decode())
