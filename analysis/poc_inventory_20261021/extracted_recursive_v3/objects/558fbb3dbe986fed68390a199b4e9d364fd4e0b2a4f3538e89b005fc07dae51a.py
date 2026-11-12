import time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex = "1c053bbbcd247a12b51273ca5a3775abe71ef5d266fe325c3aa09701c8664232836b563eac36123bbb4932f87869d941d236814224d1fd5895055e456a71a6e4"
sig2_hex = "1c053bbbcd247a12b51273ca5a3775abe71ef5d266fe325c3aa09701c8664232421d90f7eb180c43b325cb992e544b929690476f3fd303ffb050c1b4eaccc929"
z1_hex = "cda1e7f2d0ca33593058db693a5368bd984c3755c31f7794462f10bdd4842ab7"
z2_hex = "84253939f37804e4be047daf76722d11298763fadcbdb68b1103ce5249493d1c"
challenge_msg_hex = "8fe30c406c09ae6c3466fa381873253b39353e692cde2990d9e7d03d7eb5ecc4"

key = ECC.construct(curve='NIST P-256')
n = key.curve.q

s1 = int(sig1_hex[64:128], 16)
r = int(sig1_hex[0:64], 16)
s2 = int(sig2_hex[64:128], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

assert int(sig2_hex[0:64], 16) == r, "r mismatch"

# z1 + r*d = s1*k (mod n);  z2 + r*d = s2*k (mod n)
# subtract:  z1 - z2 = (s1 - s2)*k  (mod n)  -> solve for k directly
ds = (s1 - s2) % n
dz = (z1 - z2) % n
k = (dz * pow(ds, -1, n)) % n

# d = (s1*k - z1) / r  (mod n)
d = ((s1 * k - z1) % n) * pow(r, -1, n) % n

# self-check: rebuild k from d and confirm both signatures verify
k_check = ((z1 + r * d) % n) * pow(s1, -1, n) % n
assert k_check == k
k_check2 = ((z2 + r * d) % n) * pow(s2, -1, n) % n
assert k_check2 == k

t0 = time.monotonic_ns()

dkey = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(dkey, 'fips-186-3')
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig_bytes = signer.sign(h)

# verification sanity checks
try:
    DSS.new(dkey, 'fips-186-3').verify(h, sig_bytes)
    ok_challenge = True
except ValueError:
    ok_challenge = False

ver1 = ECC.construct(curve='NIST P-256', d=d)
try:
    DSS.new(ver1, 'fips-186-3').verify(SHA256.new(bytes.fromhex(z1_hex)), bytes.fromhex(sig1_hex))
    ok_sig1 = True
except ValueError:
    ok_sig1 = False

ver2 = ECC.construct(curve='NIST P-256', d=d)
try:
    DSS.new(ver2, 'fips-186-3').verify(SHA256.new(bytes.fromhex(z2_hex)), bytes.fromhex(sig2_hex))
    ok_sig2 = True
except ValueError:
    ok_sig2 = False

print("OK sig1=%s sig2=%s challenge=%s" % (ok_sig1, ok_sig2, ok_challenge))
print("OPSPAN_NS:%d" % (time.monotonic_ns() - t0))

d_hex = "%064x" % d
sig_hex = sig_bytes.hex()
print('CLAIM:{"d_hex": "%s", "sig_hex": "%s"}' % (d_hex, sig_hex))