import base64
import math

with open("pubkey.pem") as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith("-----")]
key_b64 = "".join(lines)
key_der = base64.b64decode(key_b64)

# Parse SubjectPublicKeyInfo to extract modulus N
def parse_integer(data, offset):
    if data[offset] != 0x02:
        raise ValueError("expected INTEGER")
    offset += 1
    length = data[offset]
    offset += 1
    if length > 127:
        raise ValueError("unsupported INTEGER length")
    value = int.from_bytes(data[offset:offset+length], "big")
    return value, offset+length

offset = 0
# SEQUENCE
assert data[offset] == 0x30
offset += 1
seq_len = data[offset]
offset += 1
# SEQUENCE (algorithm identifier)
assert data[offset] == 0x30
offset += 1
alg_len = data[offset]
offset += 1 + alg_len
# INTEGER e
e, offset = parse_integer(data, offset)
# INTEGER N
N, offset = parse_integer(data, offset)

with open("key.enc") as f:
    y_str = f.read().strip()
Y = int(y_str)

with open("file.enc") as f:
    c_b64 = f.read().strip()
C = base64.b64decode(c_b64)

# Y + N is a perfect cube; K = cbrt(Y + N)
val = Y + N
K = round(val ** (1/3))
while K**3 < val:
    K += 1
while K**3 > val:
    K -= 1
assert K**3 == val, "Y+N is not a perfect cube"

# Y = K^e mod N = K^3 mod N; reconstruct full Y
Y_full = K**3
Y_bytes = Y_full.to_bytes((Y_full.bit_length() + 7) // 8, "big")

# C = Y_bytes XOR S; pad/truncate to match
S = bytes(a ^ b for a, b in zip(C, (Y_bytes * ((len(C) // len(Y_bytes)) + 1))[:len(C)]))

print(S.decode("utf-8", errors="replace"))
