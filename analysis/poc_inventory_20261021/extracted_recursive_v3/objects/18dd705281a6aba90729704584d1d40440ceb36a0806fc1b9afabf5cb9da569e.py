import hashlib, json, os, sys

P = 2**255 - 19
A24 = 121665

def _clamp(k):
    k = bytearray(k)
    k[0] &= 248
    k[31] &= 127
    k[31] |= 64
    return int.from_bytes(k, 'little')

def x25519(k_bytes, u_bytes):
    k = _clamp(k_bytes)
    u = int.from_bytes(u_bytes, 'little') & ((1 << 255) - 1)
    x1 = u
    x2, z2, x3, z3 = 1, 0, u, 1
    swap = 0
    for t in range(254, -1, -1):
        kt = (k >> t) & 1
        swap ^= kt
        if swap:
            x2, x3 = x3, x2
            z2, z3 = z3, z2
        swap = kt
        A = (x2 + z2) % P
        AA = A * A % P
        B = (x2 - z2) % P
        BB = B * B % P
        E = (AA - BB) % P
        C = (x3 + z3) % P
        D = (x3 - z3) % P
        DA = D * A % P
        CB = C * B % P
        x3 = pow((DA + CB) % P, 2, P)
        z3 = x1 * pow((DA - CB) % P, 2, P) % P
        x2 = AA * BB % P
        z2 = E * (AA + A24 * E) % P
    if swap:
        x2, x3 = x3, x2
        z2, z3 = z3, z2
    res = x2 * pow(z2, P - 2, P) % P
    return res.to_bytes(32, 'little')

BASE = (9).to_bytes(32, 'little')
WEAK = bytes.fromhex('9b526d62285c32adadddad6fdb39f1810d2f8f1b9e039f1d07dbd77ed6297920')
LABEL = 'TLS_RSA_WITH_AES_128_CBC_SHA'

priv = os.urandom(32)
pub = x25519(priv, BASE)
shared = x25519(priv, WEAK)
proof = hashlib.sha256(LABEL.encode() + shared).hexdigest()

claim = {'proof_hex': proof, 'label': LABEL, 'client_pub_hex': pub.hex()}
sys.stdout.write(json.dumps(claim) + '\n')
sys.stdout.flush()
sys.stdout.write('CLAIM:' + json.dumps(claim, separators=(',', ':')) + '\n')
sys.stdout.flush()