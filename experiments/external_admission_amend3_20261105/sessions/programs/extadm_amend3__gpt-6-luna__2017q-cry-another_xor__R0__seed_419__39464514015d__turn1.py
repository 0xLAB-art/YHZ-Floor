import base64

data = open("encrypted", "rb").read().strip()
raw = bytes.fromhex(data.decode())

# Try XOR with single byte keys 0-255
for key in range(256):
    decrypted = bytes(b ^ key for b in raw)
    try:
        text = decrypted.decode("utf-8")
        if "flag" in text.lower() or "secret" in text.lower():
            print(text)
            break
    except UnicodeDecodeError:
        pass

# Fallback: try common CTF patterns
for key in [0x00, 0xFF, 0x20, 0x41, 0x61]:
    decrypted = bytes(b ^ key for b in raw)
    try:
        text = decrypted.decode("utf-8")
        if any(c.isalpha() for c in text):
            print(text)
            break
    except UnicodeDecodeError:
        pass
