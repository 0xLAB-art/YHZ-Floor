import time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex = "c7fdbb1e737577244f19d608a04e12f3e9b1e38f732d7c56d494c64eec4750096f091c4e52853ebc216e8244126b6b0e41ac035eff88a47146cae198cc035708"
sig2_hex = "c7fdbb1e737577244f19d608a04e12f3e9b1e38f732d7c56d494c64eec47500999728293b962da017303c1faefa4a5ec4e0b938553afc26254befb0c479de10a"
z1_hex = "e339518ec077d68b61ff868b51869dc8e7337a5dc27c4606075992fa8ddae7dc"
z2_hex = "7bf82a72193ed94794e534b195d94d3d39441ce73b892d62d5e942460c5cb8c6"
challenge_msg_hex = "08e22bef26c5879283807cba27ce16e0775bfb42cf481eae902120bb2f47c822"

t0 = time.monotonic_ns()

sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)
r1 = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
r2 = int.from_bytes(sig2[:32], 'big')
s2 = int.from_bytes(sig2[32:], 'big')
z1 = int.fromhex(z1_hex)
z2 = int.fromhex(z2_hex)

n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
assert r1 == r2, "r mismatch"

ds = (s1 - s2) % n
dz = (z1 - z2) % n
k = (dz * pow(ds, -1, n)) % n
d = ((s1 * k - z1) * pow(r1, -1, n)) % n

# sanity: verify recovered key reproduces sig1 on message 1
key = ECC.construct(curve='NIST P-256', d=d)
DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(z1_hex)), sig1)
DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(z2_hex)), sig2)

sig3 = DSS.new(key, 'fips-186-3').sign(SHA256.new(bytes.fromhex(challenge_msg_hex)))
DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig3)

d_hex = '%064x' % d
sig_hex = sig3.hex()

t1 = time.monotonic_ns()
print('OPSPAN_NS:%d' % (t1 - t0))
print('CLAIM:' + '{"d_hex": "%s", "sig_hex": "%s"}' % (d_hex, sig_hex))
import sys
sys.stdout.flush()