import base64

with open("ciphertext.txt") as f:
    data = base64.b64decode(f.read().strip())

print(data.decode())