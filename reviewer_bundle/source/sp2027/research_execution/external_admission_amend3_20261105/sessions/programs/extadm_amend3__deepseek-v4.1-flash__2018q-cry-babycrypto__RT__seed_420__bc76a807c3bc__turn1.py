import base64

with open("ciphertext.txt", "rb") as f:
    data = base64.b64decode(f.read())

# The ciphertext is a ROT13 of the flag (each letter shifted by 13).
# Verify: decode and check that result is a readable flag.
flag = data.decode("ascii").translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"))

print(flag)