import base64

cipher = open("ciphertext.txt").read().strip()
data = base64.b64decode(cipher)

# The ciphertext is a ROT13 of the flag (base64-decoded data is ROT13-encoded ASCII)
flag = ''.join(chr((ord(c) - 65 + 13) % 26 + 65) if c.isupper() else
              chr((ord(c) - 97 + 13) % 26 + 97) if c.islower() else c
              for c in data.decode())

print(flag)
