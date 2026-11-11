import base64

data = open("ciphertext.txt").read().strip()
flag = "".join(chr(int(x, 16)) for x in data.split())
print(flag)