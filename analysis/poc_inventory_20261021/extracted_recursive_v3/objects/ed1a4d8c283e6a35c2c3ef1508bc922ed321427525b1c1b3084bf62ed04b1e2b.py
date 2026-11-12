import time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex = "1c053bbbcd247a12b51273ca5a3775abe71ef5d266fe325c3aa09701c8664232836b563eac36123bbb4932f87869d941d236814224d1fd5895055e456a71a6e4"
sig2_hex = "1c053bbbcd247a12b51273ca5a3775abe71ef5d266fe325c3aa09701c8664232421d90f7eb180c43b325cb992e544b929690476f3fd303ffb050c1b4eaccc929"
z1_hex = "cda1e7f2d0ca33593058db693a5368bd984c3755c31f7794462f10bdd4842ab7"
z2_hex = "84253939f37804e4be047daf76722d11298763fadcbdb68b1103ce5249493d1c"
challenge_msg_hex = "8fe30c406c09ae6c3466fa381873253b39353e692cde2990d9e7d03d7eb5ecc4"

n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
try:
    n = ECC._new_curve('NIST P-256').q
except Exception:
    pass

r = int(sig1_hex[0:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[0:64], 16)
s2 = int(sig2_hex[64:128], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

assert r == r2, "r mismatch"
assert (s1 * pow(s2, -1, n)) % n != 1

# z1 + r*d = s1*k  and  z2 + r*d = s2*k   (mod n)
# subtract -> k = (z1 - z2) / (s1 - s2) mod n
ds = (s1 - s2) % n
dz = (z1 - z2) % n
assert ds % n != 0
k = (dz * pow(ds, -1, n)) % n

# d = (s1*k - z1) / r  mod n
d = ((s1 * k - z1) % n) * pow(r, -1, n) % n
assert 1 <= d < n

# self-consistency
assert ((z1 + r * d) * pow(s1, -1, n)) % n == k
assert ((z2 + r * d) * pow(s2, -1, n)) % n == k

t0 = time.monotonic_ns()

dkey = ECC.construct(curve='NIST P-256', d=d)
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig_bytes = DSS.new(dkey, 'fips-186-3').sign(h)

ok_challenge = True
try:
    DSS.new(ECC.construct(curve='NIST P-256', d=d), 'fips-186-3').verify(h, sig_bytes)
except ValueError:
    ok_challenge = False

ok1 = ok2 = False
try:
    DSS.new(ECC.construct(curve='NIST P-256', d=d), 'fips-186-3').verify(SHA256.new(bytes.fromhex(z1_hex)), bytes.fromhex(sig1_hex))
    ok1 = True
except ValueError:
    ok1 = False
try:
    DSS.new(ECC.construct(curve='NIST P-256', d=d), 'fips-186-3').verify(SHA256.new(bytes.fromhex(z2_hex)), bytes.fromhex(sig2_hex))
    ok2 = True
except ValueError:
    ok2 = False

print("checks sig1=%s sig2=%s challenge=%s" % (ok1, ok2, ok_challenge))
print("OPSPAN_NS:%d" % (time.monotonic_ns() - t0))

print('CLAIM:{"d_hex": "%064x", "sig_hex": "%s"}' % (d, sig_bytes.hex()))