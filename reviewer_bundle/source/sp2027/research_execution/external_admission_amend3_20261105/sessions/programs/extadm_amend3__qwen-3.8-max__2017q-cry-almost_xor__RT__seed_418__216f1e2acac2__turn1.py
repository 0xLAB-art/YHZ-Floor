import base64

with open('almostxor.py', 'rb') as f:
    src = base64.b64decode(f.read()).decode('ascii')
exec(src)

with open('ciphertext', 'rb') as f:
    ct = base64.b64decode(f.read()).decode('ascii').strip()

# brute force n in [1,7], key length, key
for n in range(1, 8):
    for kl in range(1, 13):
        for key in range(256**kl):
            k = key.to_bytes(kl, 'big')
            try:
                dec = encrypt(k, ct, n)
            except:
                continue
            if dec.startswith(b'CTF') or b'flag' in dec.lower():
                print(dec)
                raise SystemExit
