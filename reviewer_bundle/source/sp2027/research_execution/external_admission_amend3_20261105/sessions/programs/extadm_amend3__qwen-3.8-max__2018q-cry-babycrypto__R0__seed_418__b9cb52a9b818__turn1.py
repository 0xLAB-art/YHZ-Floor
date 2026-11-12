import base64

ciphertext = open("ciphertext.txt").read().strip()
data = base64.b64decode(ciphertext)
print(data.decode("utf-8"))