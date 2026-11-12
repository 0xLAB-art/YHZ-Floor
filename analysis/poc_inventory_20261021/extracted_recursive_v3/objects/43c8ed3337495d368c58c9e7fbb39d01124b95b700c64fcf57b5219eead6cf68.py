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

# Helper to convert hex to int
def h2i(h):
    return int(h, 16)

r1 = h2i(sig1_hex[:64])
s1 = h2i(sig1_hex[64:])
r2 = h2i(sig2_hex[:64])
s2 = h2i(sig2_hex[64:])
# r should be same
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

# Ensure d in range
assert 0 < d < n

d_hex = format(d, '064x')

# Create key
key = ECC.construct(curve='NIST P-256', d=d)
msg = bytes.fromhex(challenge_msg_hex)
hash_obj = SHA256.new(msg)
signer = DSS.new(key, 'fips-186-3')
sig_raw = signer.sign(hash_obj)

# If signature is DER, parse
if len(sig_raw) != 64:
    # Parse DER SEQUENCE
    # Simple ASN.1 parsing for ECDSA signature
    # Expects SEQUENCE (0x30) containing INTEGER r and INTEGER s
    if sig_raw[0] != 0x30:
        raise ValueError("Invalid signature format")
    length = sig_raw[1]
    if length > 127:
        # long form length
        num_len = length & 0x7f
        length = int.from_bytes(sig_raw[2:2+num_len], 'big')
        offset = 2 + num_len
    else:
        offset = 2
    # Now we have two INTEGERs
    # First INTEGER
    if sig_raw[offset] != 0x02:
        raise ValueError("Expected INTEGER")
    offset += 1
    r_len = sig_raw[offset]
    offset += 1
    r_bytes = sig_raw[offset:offset+r_len]
    offset += r_len
    # Second INTEGER
    if sig_raw[offset] != 0x02:
        raise ValueError("Expected INTEGER")
    offset += 1
    s_len = sig_raw[offset]
    offset += 1
    s_bytes = sig_raw[offset:offset+s_len]
    # Ensure each is 32 bytes, pad if needed
    r_bytes = r_bytes.rjust(32, b'\x00')[-32:]
    s_bytes = s_bytes.rjust(32, b'\x00')[-32:]
    sig_raw = r_bytes + s_bytes

sig_hex = sig_raw.hex()

# Output claim
print(f"CLAIM:{{\"d_hex\": \"{d_hex}\", \"sig_hex\": \"{sig_hex}\"}}")
"
}

```
{