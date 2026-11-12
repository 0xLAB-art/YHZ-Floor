import base64

ciphertext = open("ciphertext.txt").read().strip()
data = base64.b64decode(ciphertext)
flag = "".join(chr(b) for b in data)
print(flag)