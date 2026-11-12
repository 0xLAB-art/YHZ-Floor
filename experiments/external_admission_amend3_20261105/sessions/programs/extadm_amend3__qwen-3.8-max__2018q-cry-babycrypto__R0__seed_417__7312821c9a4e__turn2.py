import base64

data = open("ciphertext.txt").read().strip()
flag = base64.b64decode(data)
print(flag.decode())