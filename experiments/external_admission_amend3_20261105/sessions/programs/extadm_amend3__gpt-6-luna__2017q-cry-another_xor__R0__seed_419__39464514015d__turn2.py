import base64

data = open("encrypted", "rb").read().strip()
raw = bytes.fromhex(data.decode())

# Try XOR with common CTF key patterns
for key in [b"flag", b"key", b"secret", b"ctf", b"password", b"admin", b"crypto", b"openai", b"luna"]:
    out = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
    try:
        text = out.decode("ascii")
        if text.isprintable() and ("flag" in text.lower() or "CTF" in text or "FLAG" in text):
            print(text)
            break
    except Exception:
        pass
else:
    # Try single-byte XOR
    for k in range(256):
        out = bytes(b ^ k for b in raw)
        try:
            text = out.decode("ascii")
            if text.isprintable() and ("flag" in text.lower() or "CTF" in text or "FLAG" in text):
                print(text)
                break
        except Exception:
            pass
