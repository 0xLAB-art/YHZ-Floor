import base64

ciphertext = open("ciphertext.txt").read().strip()
decoded = base64.b64decode(ciphertext)
print(decoded.decode("utf-8"))