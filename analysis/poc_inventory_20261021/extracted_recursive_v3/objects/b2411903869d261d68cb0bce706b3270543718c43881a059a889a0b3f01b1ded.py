import json, sys, time
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS

sig1_hex = "0a209c4e1b4841dacb627e0063cd53dae36397b46b3ee07a47c67ea7e458da930183c0c4e1ba2b3f1d22db80bdc38fd3eb73b90abb2f2bb91807984a8185ab64"
sig2_hex = "0a209c4e1b4841dacb627e0063cd53dae36397b46b3ee07a47c67ea7e458da93697afa6c706e776f7350de32d67b47d42276b675078c32893e5ac48ea6a7dd38"
z1_hex = "70685eb81afdc09e8264662fadeca141bb67e2084f3559a35237d3b812470870"
z2_hex = "91cb38c76f42f90006889009549c3d8f0058eb776da71f01f27fbcb11b9fbb4c"
challenge_msg_hex = "ce237fdabb7a928414ee06756613bc4c96cf258652346e6bab1e5d869cd3b0da"

n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

t0 = time.monotonic_ns()

assert r1 == r2, "nonce not reused (r mismatch)"
assert s1 != s2
assert (s1 - s2) % n != 0

k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
d = ((s1 * k - z1) * pow(r1, -1, n)) % n

key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
s1c = int.from_bytes(signer.sign(SHA256.new(bytes.fromhex(z1_hex))), 'big')
s2c = int.from_bytes(signer.sign(SHA256.new(bytes.fromhex(z2_hex))), 'big')

def norm(x):
    return min(x, n - x)

ok1 = norm(s1c) == norm(s1)
ok2 = norm(s2c) == norm(s2)

sig_hex = signer.sign(SHA256.new(bytes.fromhex(challenge_msg_hex))).hex()

t1 = time.monotonic_ns()
sys.stderr.write("k=%x d=%x ok1=%s ok2=%s siglen=%d\n" % (k, d, ok1, ok2, len(sig_hex)))
sys.stderr.flush()

print("OPSPAN_NS:%d" % (t1 - t0))
print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig_hex}))
sys.stdout.flush()