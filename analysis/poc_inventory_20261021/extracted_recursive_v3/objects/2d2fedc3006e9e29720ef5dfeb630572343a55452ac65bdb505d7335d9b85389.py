import json
import hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
sig1_hex = "ca418aaa18a3c452e927aa7d028c3ef3a0030c7f46cbb6502ffa3438a1ee805391672fae340c611c8ac6151f84bd54448edd31d4a0ee28edb6c2ce48c9d71528"
sig2_hex = "ca418aaa18a3c452e927aa7d028c3ef3a0030c7f46cbb6502ffa3438a1ee8053c5f55b838ef555cbb52b36a34a9c447f6b31642635eb7f4d842951600510dc89"
z1_hex = "0c481c5ff7ed31ae8c54ff72f30011496feb93035d87f93750fc808685d609d3"
z2_hex = "ff15e38634cceec3aad851b25b11d1cd651fc1026d481486ec2e54f7b72afe6b"
challenge_msg_hex = "f4d75c03dfcb2970071fbf46cb2e1c47cc619ccf1479675fc81b289f08d5488f"

# Curve order for NIST P-256
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

def h2i(h):
    return int(h, 16)

r1 = h2i(sig1_hex[:64])
s1 = h2i(sig1_hex[64:])
r2 = h2i(sig2_hex[:64])
s2 = h2i(sig2_hex[64:])
assert r1 == r2, "r values differ"
r = r1
z1 = h2i(z1_hex)
z2 = h2i(z2_hex)

# Compute k
num = (z1 - z2) % n
den = (s1 - s2) % n
k = num * pow(den, -1, n) % n

# Compute d
d = ((s1 * k - z1) % n) * pow(r, -1, n) % n
assert 0 < d < n

d_hex = format(d, '064x')

# Create key and sign
key = ECC.construct(curve='NIST P-256', d=d)
msg = bytes.fromhex(challenge_msg_hex)
hash_obj = SHA256.new(msg)
signer = DSS.new(key, 'fips-186-3')
sig_der = signer.sign(hash_obj)

# Parse DER to get r and s
def der_to_rs(sig_der):
    # Expects SEQUENCE
    if sig_der[0] != 0x30:
        raise ValueError("Invalid DER: not a SEQUENCE")
    length = sig_der[1]
    if length & 0x80:
        # long form
        num_len = length & 0x7f
        length = int.from_bytes(sig_der[2:2+num_len], 'big')
        pos = 2 + num_len
    else:
        pos = 2
    # First INTEGER
    if sig_der[pos] != 0x02:
        raise ValueError("Expected INTEGER for r")
    pos += 1
    r_len = sig_der[pos]
    pos += 1
    r_bytes = sig_der[pos:pos+r_len]
    pos += r_len
    # Second INTEGER
    if sig_der[pos] != 0x02:
        raise ValueError("Expected INTEGER for s")
    pos += 1
    s_len = sig_der[pos]
    pos += 1
    s_bytes = sig_der[pos:pos+s_len]
    # Remove leading zeros if any, then pad to 32 bytes
    r = int.from_bytes(r_bytes, 'big')
    s = int.from_bytes(s_bytes, 'big')
    # Ensure low s (if s > n/2, use n - s)
    if s > n // 2:
        s = n - s
    # Convert to 32-byte big-endian
    r_bytes = r.to_bytes(32, 'big')
    s_bytes = s.to_bytes(32, 'big')
    return r_bytes + s_bytes

sig_raw = der_to_rs(sig_der)
sig_hex = sig_raw.hex()

# Output claim
print(f'CLAIM:{{"d_hex": "{d_hex}", "sig_hex": "{sig_hex}"}}')
"
}

```
{