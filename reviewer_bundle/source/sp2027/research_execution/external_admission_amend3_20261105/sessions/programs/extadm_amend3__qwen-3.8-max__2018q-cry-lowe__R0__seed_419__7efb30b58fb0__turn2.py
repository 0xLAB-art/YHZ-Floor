import base64
import math

with open("pubkey.pem") as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith("-----")]
key_b64 = "".join(lines)
key_der = base64.b64decode(key_b64)

# Parse SubjectPublicKeyInfo to extract modulus N and exponent e
def parse_n_der(data):
    idx = 1
    # SEQUENCE
    assert data[idx] == 0x30
    _, idx = _read_len(data, idx + 1)
    seq_end = idx
    # INTEGER (algorithm identifier OID skipped)
    assert data[idx] == 0x30
    _, idx = _read_len(data, idx + 1)
    oid_end = idx
    # BIT STRING
    assert data[idx] == 0x03
    _, idx = _read_len(data, idx + 1)
    assert data[idx] == 0x00
    idx += 1
    # INTEGER (public key)
    assert data[idx] == 0x02
    n_len, idx = _read_len(data, idx + 1)
    n = int.from_bytes(data[idx:idx + n_len], "big")
    return n

def _read_len(data, idx):
    first = data[idx]
    if first < 0x80:
        return first, idx + 1
    n_bytes = first & 0x7F
    length = int.from_bytes(data[idx + 1:idx + 1 + n_bytes], "big")
    return length, idx + 1 + n_bytes

N = parse_n_der(key_der)

with open("key.enc") as f:
    y = int(f.read().strip())

with open("file.enc") as f:
    c_b64 = f.read().strip()
c = bytearray(base64.b64decode(c_b64))

# Y + N is a perfect cube; root is K
k = round((y + N) ** (1 / 3))
while k ** 3 < y + N:
    k += 1
while k ** 3 > y + N:
    k -= 1
assert k ** 3 == y + N

# Y = K^e mod N, e = 3
y_mod = pow(k, 3, N)
assert y_mod == y

# C = Y xor S, so S = C xor Y
s = bytearray(len(c))
for i in range(len(c)):
    s[i] = c[i] ^ (y >> (8 * (len(c) - 1 - i))) & 0xFF

print(s.decode("latin-1"))
