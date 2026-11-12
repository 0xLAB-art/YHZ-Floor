import sys, json, time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

SIG1 = "ac98a7678c1eff79b9dbe135bbbf71ba995c776b982c7fba6638d74f9f3105a4ea8089d7b2950d4e41fe94c24d81a658d94ff20e6f6e19e1f1e7268cd48d70a1"
SIG2 = "ac98a7678c1eff79b9dbe135bbbf71ba995c776b982c7fba6638d74f9f3105a46d7d3e745a3cc69a21721b469a6aa6047ac92b93424ebed1117e3379921732ae"
Z1 = "9b8c3525873fe8c4d2ee56d3df7f4a1f8ff61b14c3aacd53cbd6db9c3ab157ed"
Z2 = "080e1b6f687388402e73f6574237914dbbce931f696ba93e865b04c935b1eea5"
CH = "78c8b3188007208146815e728960a111b13459f19585965b1ba7332d4dcc9eb2"

n = ECC._curves['NIST P-256'].q
G = ECC._curves['NIST P-256'].point

sig1 = bytes.fromhex(SIG1)
sig2 = bytes.fromhex(SIG2)
r1 = int.from_bytes(sig1[0:32], 'big')
s1 = int.from_bytes(sig1[32:64], 'big')
r2 = int.from_bytes(sig2[0:32], 'big')
s2 = int.from_bytes(sig2[32:64], 'big')
z1 = int.from_bytes(bytes.fromhex(Z1), 'big')
z2 = int.from_bytes(bytes.fromhex(Z2), 'big')

t0 = time.monotonic_ns()

found = None
for e1 in (1, -1):
    for e2 in (1, -1):
        a1 = (e1 * s1) % n
        a2 = (e2 * s2) % n
        den = (a1 * r2 - a2 * r1) % n
        if den == 0:
            continue
        try:
            k = ((r2 * z1 - r1 * z2) * pow(den, -1, n)) % n
        except Exception:
            continue
        if k == 0:
            continue
        # consistency: x(k*G) must equal r (mod n)
        try:
            kgx = ECC.construct(curve='NIST P-256', k=k).point.x
        except Exception:
            continue
        if kgx % n != r1 % n:
            continue
        dd = ((a1 * k - z1) * pow(r1, -1, n)) % n
        if dd == 0 or dd >= n:
            continue
        found = (dd, k, e1, e2)
        break
    if found:
        break

if found is None:
    # fall back: try without the k-consistency check
    for e1 in (1, -1):
        for e2 in (1, -1):
            a1 = (e1 * s1) % n
            a2 = (e2 * s2) % n
            den = (a1 * r2 - a2 * r1) % n
            if den == 0:
                continue
            k = ((r2 * z1 - r1 * z2) * pow(den, -1, n)) % n
            dd = ((a1 * k - z1) * pow(r1, -1, n)) % n
            if dd != 0 and dd < n:
                found = (dd, k, e1, e2)
                break
        if found:
            break

d, k, e1, e2 = found

key = ECC.construct(curve='NIST P-256', d=d)
h1 = SHA256.new(bytes.fromhex(Z1))
h2 = SHA256.new(bytes.fromhex(Z2))
ok1 = DSS.new(key, 'fips-186-3').verify(h1, sig1)
ok2 = DSS.new(key, 'fips-186-3').verify(h2, sig2)

new_sig = DSS.new(key, 'fips-186-3').sign(SHA256.new(bytes.fromhex(CH)))

vok = DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(CH)), new_sig)

t1 = time.monotonic_ns()

print("verify_both", ok1, ok2, "new_sig_ok", vok)
print("CLAIM:" + json.dumps({"d_hex": format(d, '064x'), "sig_hex": new_sig.hex()}, separators=(',', ':')))
print("OPSPAN_NS:" + str(t1 - t0))
sys.stdout.flush()