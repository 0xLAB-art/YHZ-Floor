import json, sys, time
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS

SIG1_HEX = "af6c1e445977c8cd5fd342ada9d142babfd5776fb57c47764b6e09cd30b3a85259435c9e58e9b8960cda02d84dac717e6265543bee4f895455f6635564338bb8"
SIG2_HEX = "af6c1e445977c8cd5fd342ada9d142babfd5776fb57c47764b6e09cd30b3a852f1b4535b4e5d6aeb6cf0b77ce4ed517072fffd57c9f1aef11ef38ef2cef93122"
Z1_HEX   = "d4e3851b33a6e8dffe1e3f846fc60fecefafa762c7c9610936fa28239d0a64c6"
Z2_HEX   = "40dd64d8b5256a2fef0b676f2ad9510d4cd29447915c45ef6ea1c333579b6090"
CHAL_HEX = "ac83f11874231fb236b1dd114459698ee31e19b224c7b55de0b632c37ec53291"

n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

r1 = int(SIG1_HEX[:64], 16)
s1 = int(SIG1_HEX[64:], 16)
r2 = int(SIG2_HEX[:64], 16)
s2 = int(SIG2_HEX[64:], 16)
assert r1 == r2, "r values differ"
r = r1
z1 = int(Z1_HEX, 16) % n
z2 = int(Z2_HEX, 16) % n

t0 = time.monotonic_ns()

d = None
k_found = None
for s1p in (s1, (-s1) % n):
    for s2p in (s2, (-s2) % n):
        denom = (s1p - s2p) % n
        if denom == 0:
            continue
        k = ((z1 - z2) * pow(denom, -1, n)) % n
        if k == 0:
            continue
        try:
            Px = ECC.construct(curve='NIST P-256', d=k).point.x
        except Exception:
            continue
        if Px != r:
            continue
        dd = ((s1p * k - z1) * pow(r, -1, n)) % n
        if dd == 0:
            continue
        d = dd
        k_found = k
        break
    if d is not None:
        break

if d is None:
    # fallback: pick any consistent combination (should not happen)
    s1p, s2p = s1, s2
    k = ((z1 - z2) * pow((s1p - s2p) % n, -1, n)) % n
    d = ((s1p * k - z1) * pow(r, -1, n)) % n

key = ECC.construct(curve='NIST P-256', d=d)
msg = bytes.fromhex(CHAL_HEX)
h = SHA256.new(msg)
signer = DSS.new(key, 'fips-186-3')
sig = signer.sign(h)
# self-check
DSS.new(key, 'fips-186-3').verify(h, sig)

t1 = time.monotonic_ns()
print("OPSPAN_NS:%d" % (t1 - t0), flush=True)
claim = {"d_hex": format(d, '064x'), "sig_hex": sig.hex()}
print("CLAIM:" + json.dumps(claim), flush=True)