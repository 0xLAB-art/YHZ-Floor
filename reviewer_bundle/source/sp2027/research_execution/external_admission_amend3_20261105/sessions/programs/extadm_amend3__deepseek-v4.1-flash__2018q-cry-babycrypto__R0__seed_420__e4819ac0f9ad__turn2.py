import base64

cipher = open("ciphertext.txt").read().strip()
data = base64.b64decode(cipher)
print(data.decode("utf-8"))