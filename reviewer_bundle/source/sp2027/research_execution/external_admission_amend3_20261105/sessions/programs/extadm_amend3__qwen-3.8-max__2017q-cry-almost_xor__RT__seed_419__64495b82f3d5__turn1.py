import base64

with open('almostxor.py', 'rb') as f:
    src = base64.b64decode(f.read()).decode()
exec(src)

with open('ciphertext', 'rb') as f:
    ct = base64.b64decode(f.read()).decode().strip()

# brute force n in [1..7] and key length
for n in range(1, 8):
    for kl in range(1, 16):
        for k in range(256 ** kl):
            key = k.to_bytes(kl, 'big')
            try:
                dec = encrypt(key, ct, n)
            except ValueError:
                continue
            if dec.startswith(b'CTF') or b'flag' in dec.lower():
                print(dec.decode())
                raise SystemExit
