import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith('-----')]
der = ''.join(lines)
N = int(der, 16)

with open('key.enc') as f:
    Y = int(f.read().strip())

with open('file.enc') as f:
    C = base64.b64decode(f.read().strip())

K = round((Y + N) ** (1/3))
if K**3 != Y + N:
    for cand in (K-1, K, K+1):
        if cand**3 == Y + N:
            K = cand
            break

Y_bytes = Y.to_bytes((Y.bit_length() + 7) // 8, 'big')
S = bytes(a ^ b for a, b in zip(Y_bytes, C))
print(S.decode('utf-8', errors='replace'))