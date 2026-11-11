import base64

data = base64.b64decode(open("encrypted", "rb").read().strip())

# The ciphertext is a sequence of length-prefixed blocks: [len][data]
# where len is a single byte. Decode each block as ASCII.
result = []
i = 0
while i < len(data):
    length = data[i]
    i += 1
    block = data[i:i+length]
    i += length
    try:
        result.append(block.decode("ascii"))
    except UnicodeDecodeError:
        result.append(block.hex())

print("".join(result))
