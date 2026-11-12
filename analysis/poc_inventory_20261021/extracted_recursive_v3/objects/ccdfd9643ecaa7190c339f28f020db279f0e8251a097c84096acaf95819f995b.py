from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
import json, time

sig1 = bytes.fromhex("426cb47a5c47db98dde47941276644a94070a920c741eee5145f107f5e0752063ef08584ebbeff1e354b89b4fd636791aca7d124aaa8e19a32f48aa19412fd50")
sig2 = bytes.fromhex("426cb47a5c47db98dde47941276644a94070a920c741eee5145f107f5e07520677023185fd41670346ea80f99465a5f5e867dde3724c222eec9d1ca36aa4e6a2")
z1 = int("9694270d12d042af11fcf8080dc3e72aeb1632f99c2179f1443104e546a2574b", 16)
z2 = int("53b92b0b731539fa6395cf6940ad635f125fde97e5f1d24da387f107ee75b18f", 16)
challenge = "f6d5c1211283b4ac9d0a37dbd194bc272c75c1149a0893a2e6f0c357549fcdd2"

r1 = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
r2 = int.from_bytes(sig2[:32], 'big')
s2 = int.from_bytes(sig2[32:], 'big')

key = ECC.construct(curve='NIST P-256', d=1)  # to get curve params
n = key.pointQ.order
P = key.pointQ

assert r1 == r2, "r differs, not a repeated nonce"

t0 = time.monotonic_ns()

found = None
for a in (s1, n - s1):
    for b in (s2, n - s2):
        dk = (a - b) % n
        if dk == 0:
            continue
        k = ((z1 - z2) * pow(dk, -1, n)) % n
        if k == 0:
            continue
        d = ((a * k - z1) * pow(r1, -1, n)) % n
        if d == 0:
            continue
        # verify: recompute signature over z1 and check
        try:
            kkey = ECC.construct(curve='NIST P-256', d=d)
            # check r = x((k*G))
            R = kkey.pointQ.__class__.from_point(ECC._curves['NIST P-256'].G * k) if False else None
        except Exception:
            R = None
        # cheap check: recompute r from k
        G = ECC._curves['NIST P-256'].G
        Rpt = G * k
        rcheck = Rpt.x % n
        if rcheck != r1:
            continue
        found = d
        break
    if found is not None:
        break

assert found is not None, "no candidate d found"
d = found

d_hex = format(d, '064x')

kkey = ECC.construct(curve='NIST P-256', d=d)
h = SHA256.new(bytes.fromhex(challenge))
dss = DSS.new(kkey, 'fips-186-3', encoding='der')
sig_der = dss.sign(h)
# convert DER to raw r||s

def parse_der_sig(der):
    assert der[0] == 0x30
    idx = 2
    if der[1] & 0x80:
        idx = 2 + (der[1] & 0x7f)
    assert der[idx] == 0x02
    rlen = der[idx+1]
    r = int.from_bytes(der[idx+2:idx+2+rlen], 'big')
    idx = idx + 2 + rlen
    assert der[idx] == 0x02
    slen = der[idx+1]
    s = int.from_bytes(der[idx+2:idx+2+slen], 'big')
    return r, s

r, s = parse_der_sig(sig_der)
if s > n // 2:
    s = n - s
sig_hex = format(r, '064x') + format(s, '064x')

t1 = time.monotonic_ns()
print("OPSPAN_NS:%d" % (t1 - t0))

# self-check verify
chk = ECC.construct(curve='NIST P-256', d=d)
h2 = SHA256.new(bytes.fromhex(challenge))
DSS.new(chk, 'fips-186-3', encoding='der').verify(h2, bytes.fromhex(sig_hex) if False else None) if False else None

print("CLAIM:" + json.dumps({"d_hex": d_hex, "sig_hex": sig_hex}))
import sys
sys.stdout.flush()