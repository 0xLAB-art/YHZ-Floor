import base64

cipher = open("ciphertext.txt").read().strip()
data = base64.b64decode(cipher)
flag = "".join(chr(b ^ 0x59) for b in data)
print(flag)