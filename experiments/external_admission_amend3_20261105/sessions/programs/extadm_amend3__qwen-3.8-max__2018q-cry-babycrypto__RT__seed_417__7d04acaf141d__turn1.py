import base64

with open("ciphertext.txt", "rb") as f:
    data = f.read()

cipher = base64.b64decode(data).decode("utf-8")

# The ciphertext is a ROT13 of the flag
flag = "".join(chr((ord(c) - 97 + 13) % 26 + 97) if c.islower() else c for c in cipher)

print(flag)