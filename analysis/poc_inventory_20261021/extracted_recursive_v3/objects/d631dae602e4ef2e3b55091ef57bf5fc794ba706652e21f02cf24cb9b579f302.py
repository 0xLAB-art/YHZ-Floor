import sys
import json
import hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
sig1_hex = "b80617c1e579cff479b5e78304b396fcc0bc1aac76dbf9c355d41ddbed9c336129eddcf0cd25b1d5840742a1d589bc1dcf9c165b29c59c40bb46d97c9ef75774"
sig2_hex = "b80617c1e579cff479b5e78304b396fcc0bc1aac76dbf9c355d41ddbed9c33615298c26e00f90c89518ab43bf21fb938c1ca087f82764dceb3530036d78da82e"
z1_hex = "98a72e4b0feff8ec55759d07457734f5b573db5faf57e749f3c228a0aaafa9c2"
z2_hex = "2a1a961289c341255f4d38d459460db4d2b3bc3f075344317ff2eb0bbdd3bdee"
challenge_msg_hex = "5ce18abe351986726945f20e159a53fdd6cca416f961a0b71f4a247ae475dbeb"

# NIST P-256 order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Parse signatures (64 bytes = r || s, each 32 bytes)
sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)

r = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
s2 = int.from_bytes(sig2[32:], 'big')

z1 = int.from_bytes(bytes.fromhex(z1_hex), 'big')
z2 = int.from_bytes(bytes.fromhex(z2_hex), 'big')

# Verify r is the same for both signatures (it should be since same nonce)
assert r == int.from_bytes(sig2[:32], 'big'), "r values differ!"

# Recover nonce k
# s1 = k^-1 * (z1 + r*d) mod n
# s2 = k^-1 * (z2 + r*d) mod n
# s1 - s2 = k^-1 * (z1 - z2) mod n
# k = (z1 - z2) * (s1 - s2)^-1 mod n
s1_minus_s2 = (s1 - s2) % n
z1_minus_z2 = (z1 - z2) % n

# Modular inverse of (s1 - s2)
inv_s1_minus_s2 = pow(s1_minus_s2, -1, n)
k = (z1_minus_z2 * inv_s1_minus_s2) % n

# Recover private key d
# s1 = k^-1 * (z1 + r*d) mod n
# s1 * k = z1 + r*d mod n
# r*d = s1*k - z1 mod n
# d = (s1*k - z1) * r^-1 mod n
inv_r = pow(r, -1, n)
d = ((s1 * k - z1) % n) * inv_r % n

# Verify by computing d from second signature as well
d2 = ((s2 * k - z2) % n) * inv_r % n
assert d == d2, "Private key mismatch!"

# Create signature for challenge message
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
challenge_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig = signer.sign(challenge_hash)
sig_hex = sig.hex()

d_hex = format(d, '064x')

print(f"CLAIM:{{\"d_hex\": \"{d_hex}\", \"sig_hex\": \"{sig_hex}\"}}")
sys.stdout.flush()