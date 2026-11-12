import json
import sys
import hashlib

P = 2**255 - 19
A24 = 121665


def decode_scalar(k):
    k = bytearray(k)
    k[0] &= 248
    k[31] &= 127
    k[31] |= 64
    return int.from_bytes(bytes(k), 'little')


def decode_u(u):
    u = bytearray(u)
    u[31] &= 127
    return int.from_bytes(bytes(u), 'little') % P


def cswap(swap, x2, x3):
    dummy = swap * ((x2 - x3) % P)
    x2n = (x2 - dummy) % P
    x3n = (x3 + dummy) % P
    return x2n, x3n


def x25519(k, u):
    x1 = decode_u(u)
    ksc = decode_scalar(k)
    x2, z2, x3, z3, swap = 1 % P, 0, x1, 1 % P, 0
    for t in range(254, -1, -1):
        kt = (ksc >> t) & 1
        swap ^= kt
        x2, x3 = cswap(swap, x2, x3)
        z2, z3 = cswap(swap, z2, z3)
        swap = kt
        A = (x2 + z2) % P
        AA = (A * A) % P
        B = (x2 - z2) % P
        BB = (B * B) % P
        E = (AA - BB) % P
        C = (x3 + z3) % P
        D = (x3 - z3) % P
        DA = (D * A) % P
        CB = (C * B) % P
        x3 = (DA + CB) % P
        x3 = (x3 * x3) % P
        z3 = (DA - CB) % P
        z3 = (x1 * z3) % P
        z3 = (z3 * z3) % P
        x2 = (AA * BB) % P
        z2 = (E * ((AA + (A24 * E) % P) % P)) % P
    x2, x3 = cswap(swap, x2, x3)
    z2, z3 = cswap(swap, z2, z3)
    inv_z2 = pow(z2, P - 2, P)
    s = (x2 * inv_z2) % P
    return s.to_bytes(32, 'little')


def pubkey_from_priv(priv):
    base = (9).to_bytes(32, 'little')
    return x25519(priv, base)


prov = {}
if len(sys.argv) > 1 and sys.argv[1]:
    try:
        prov = json.loads(sys.argv[1])
    except Exception:
        prov = {}

weak_pub_hex = None
if isinstance(prov, dict):
    for k in ("weak_pub_hex", "peer_pub_hex", "server_pub_hex", "weak_pub", "pub_hex"):
        if k in prov and prov[k]:
            weak_pub_hex = str(prov[k])
            break

if not weak_pub_hex:
    weak_pub_hex = "1ce108f300b77d29cd7a399fc0d8791031c9c0ca83f219a7d0bf8481ebdd1d1e"

weak_pub = bytes.fromhex(weak_pub_hex)

client_priv = bytes.fromhex("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a")
client_pub = pubkey_from_priv(client_priv)

label = "TLS_RSA_WITH_AES_128_CBC_SHA"
shared = x25519(client_priv, weak_pub)
proof = hashlib.sha256(label.encode('ascii') + shared).digest()

claim = {
    "proof_hex": proof.hex(),
    "label": label,
    "client_pub_hex": client_pub.hex(),
}

sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
sys.stdout.flush()