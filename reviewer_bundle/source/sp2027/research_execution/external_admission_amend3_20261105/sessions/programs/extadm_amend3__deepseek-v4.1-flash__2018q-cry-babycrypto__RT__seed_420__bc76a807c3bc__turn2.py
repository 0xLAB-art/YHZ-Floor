import base64

with open("ciphertext.txt", "rb") as f:
    data = base64.b64decode(f.read().strip())

print(data.decode("utf-8"))