import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith('-----')]
key_b64 = ''.join(lines)
key_der = base64.b64decode(key_b64)

# parse modulus N from SubjectPublicKeyInfo (RSAPublicKey, INTEGER N, INTEGER e)
idx = key_der.index(0x03)  # BIT STRING header
payload = key_der[idx+1:]
assert payload[0] == 0
payload = payload[1:]
assert payload[0] == 0x30  # SEQUENCE
payload = payload[1:]
assert payload[0] == 0x02  # INTEGER N
n_len = payload[1]
n_bytes = payload[2:2+n_len]
N = int.from_bytes(n_bytes, 'big')
assert N.bit_length() == 1536

e = 3

with open('key.enc') as f:
    Y = int(f.read().strip())
with open('file.enc') as f:
    C_b64 = f.read().strip()
C = base64.b64decode(C_b64)

# Y + N = K^3
K3 = Y + N
K = round(K3 ** (1/3))
while K**3 < K3:
    K += 1
while K**3 > K3:
    K -= 1
assert K**3 == K3

Y_bytes = K.to_bytes(192, 'big')
assert len(Y_bytes) == 192

flag = bytes(a ^ b for a, b in zip(Y_bytes, C))
print(flag.decode('utf-8', errors='replace'))
