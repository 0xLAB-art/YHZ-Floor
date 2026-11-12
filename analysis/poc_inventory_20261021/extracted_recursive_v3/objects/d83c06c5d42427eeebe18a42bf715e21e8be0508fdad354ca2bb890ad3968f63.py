import sys, json, time

sig1_hex="802f837077f3d284cfb128efcbfb8bada1c47bd70c1b07dd89eadbf1442f9503e4dd96a4ac952c613ed294444224911860f6b8a624e5f75a92c56469a5580712"
sig2_hex="802f837077f3d284cfb128efcbfb8bada1c47bd70c1b07dd89eadbf1442f95038090dc38803d72d63381b83eed307afe17d0290405318ab4fbbb0017f757a9a1"
z1_hex="982b18ef18708e1f97671a35e0492c4bea0a5e4ba32e02d1f21342bf43c187a0"
z2_hex="c4cae8fe0c0d716155cd43cd439f9ca70f8ec2d538389709ad4d499b46fc21f6"
msg_hex="62d1f87a708bc05c11f9e1490b02e90a76d60cdce1b2861ae22821c961945c6c"

p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = (p - 3)
n  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
G  = (Gx, Gy)

def inv(m):
    return pow(m, -1, p)

def padd(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P
    x2, y2 = Q
    if x1 % p == x2 % p:
        if (y1 + y2) % p == 0: return None
        lam = (3 * x1 * x1 + a) * inv(2 * y1 % p) % p
    else:
        lam = (y2 - y1) * inv((x2 - x1) % p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def pmul(k, P=G):
    k %= n
    R = None
    Q = P
    while k:
        if k & 1:
            R = padd(R, Q)
        Q = padd(Q, Q)
        k >>= 1
    return R

def verify(d, r, s, z):
    if not (1 <= r < n and 1 <= s < n): return False
    if d <= 0 or d >= n: return False
    Q = pmul(d)
    w = pow(s, -1, n)
    u1 = z * w % n
    u2 = r * w % n
    P = padd(pmul(u1), pmul(u2, Q))
    if P is None: return False
    return P[0] % n == r % n

b1 = bytes.fromhex(sig1_hex)
b2 = bytes.fromhex(sig2_hex)
r1 = int.from_bytes(b1[:32], 'big'); s1 = int.from_bytes(b1[32:], 'big')
r2 = int.from_bytes(b2[:32], 'big'); s2 = int.from_bytes(b2[32:], 'big')
z1 = int(z1_hex, 16); z2 = int(z2_hex, 16)

t0 = time.monotonic_ns()
d = None
for e1 in (1, -1):
    for e2 in (1, -1):
        try:
            s1e = s1 * e1 % n
            s2e = s2 * e2 % n
            kk = pow(s1e - s2e, -1, n) * (z1 - z2) % n
            dd = pow(r1, -1, n) * (s1e * kk - z1) % n
        except Exception as ex:
            continue
        if verify(dd, r1, s1, z1) and verify(dd, r2, s2, z2):
            d = dd
            sys.stderr.write('found d with signs %d %d\n' % (e1, e2))
            break
    if d is not None: break
if d is None:
    sys.stderr.write('no valid d found\n')
    sys.exit(2)
t1 = time.monotonic_ns()

# deterministic nonce signing
z = int(msg_hex, 16)
k = 0x1f2e3d4c5b6a79887766554433221100fedcba98765432100123456789abcdef % n
R = pmul(k)
r = R[0] % n
if r == 0:
    k = (k + 1) % n
    R = pmul(k)
    r = R[0] % n
s = pow(k, -1, n) * (z + r * d) % n
if s > n // 2:
    s = n - s

assert verify(d, r, s, z), 'self-verify failed'

print("OPSPAN_NS:%d" % (t1 - t0))
print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": "%064x%064x" % (r, s)}))
sys.stdout.flush()