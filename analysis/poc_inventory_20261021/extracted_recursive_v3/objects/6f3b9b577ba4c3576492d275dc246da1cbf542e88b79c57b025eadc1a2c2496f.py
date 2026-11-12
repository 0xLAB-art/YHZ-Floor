import sys
import json
import hashlib
import os

# Provision
provision = {}
if len(sys.argv) > 1:
    try:
        provision = json.loads(sys.argv[1])
    except Exception:
        provision = {}

weak_pub_hex = provision.get("weak_pub_hex", "")
proof_rule = provision.get("proof_rule", "")

# X25519 implementation (since pycryptodome is installed, but may not have X25519 directly; implement simple one)
# Simple X25519 implementation if needed
try:
    from Crypto.Cipher import ChaCha20_Poly1305
    from Crypto.Protocol.KDF import HKDF
    from Crypto.Hash import SHA256
    HAS_CRYPTO = True
except Exception:
    HAS_CRYPTO = False

# Implement minimal X25519 (basic)
# Curve25519 base point
P = 9

# Field operations
Q = (1 << 255) - 19

# Modular arithmetic
import struct


def modinv(a, p=Q):
    """Modular multiplicative inverse using Fermat's Little Theorem for prime p: a^(p-2) mod p"""
    return pow(a, p-2, p)


def point_mul(k, p=P):
    """Multiply point p by scalar k (Montgomery ladder simplified)"""
    # Simplified; for given task, just use a fixed client key if needed
    return pow(p, k, Q)

# Generate a client keypair
# For X25519, clamp scalar
import os

client_priv_bytes = os.urandom(32)
# Clamp
client_priv_bytes = bytearray(client_priv_bytes)
client_priv_bytes[0] &= 0xf8
client_priv_bytes[31] &= 0x7f
client_priv_bytes[31] |= 0x40

# Convert to int
client_priv_int = int.from_bytes(bytes(client_priv_bytes), "little")

# Compute public
# Base point 9
A = 486662
BASE = 9
Q = (1 << 255) - 19

def cswap(a,b,sw):
    sw = -sw
    t = sw & (a^b)
    a ^= t; b ^= t
    return a,b

# Montgomery ladder

def x25519(k, u):
    x1 = u
    x2 = 1
    z2 = 0
    x3 = u
    z3 = 1
    swap = 0
    for t in range(255, -1, -1):
        kt = (k >> t) & 1
        swap ^= kt
        x2, x3 = cswap(x2,x3,swap)
        z2, z3 = cswap(z2,z3,swap)
        swap = kt
        a = (x2 + z2) % Q
        aa = (a * a) % Q
        b = (x2 - z2) % Q
        bb = (b * b) % Q
        e = (aa - bb + Q) % Q
        c = (x3 + z3) % Q
        d = (x3 - z3) % Q
        da = (d * a) % Q
        cb = (c * b) % Q
        x3 = (da + cb) % Q
        x3 = (x3 * x3) % Q
        z3 = (da - cb + Q) % Q
        z3 = (z3 * z3) % Q
        z3 = (z3 * u) % Q
        x2 = (aa * bb) % Q
        z2 = (e * ((A * e) % Q + aa)) % Q
    x2, x3 = cswap(x2,x3,swap)
    z2, z3 = cswap(z2,z3,swap)
    inv_z2 = pow(z2, Q-2, Q)
    return (x2 * inv_z2) % Q

client_pub_int = x25519(client_priv_int, BASE)
client_pub_bytes = client_pub_int.to_bytes(32, "little")

weak_pub_int = int.from_bytes(bytes.fromhex(weak_pub_hex), "little")
shared_int = x25519(client_priv_int, weak_pub_int)
shared_secret = shared_int.to_bytes(32, "little")

# Compute proof: SHA256(label || shared_secret)
# Try to discover negotiated label by interacting with service
label = b"weak_tls"
# Make HTTP request to service
# Protocol: print JSON line with http request, read response
req = {"http": {"method": "GET", "path": "/", "headers": {}}}
print(json.dumps(req), flush=True)
# Try to read response
try:
    resp_line = sys.stdin.readline()
    if resp_line:
        resp = json.loads(resp_line)
        # Could extract label info from response if present
        body_b64 = resp.get("body_b64", "")
        # Try to infer label from response
        try:
            import base64
            body = base64.b64decode(body_b64) if body_b64 else b""
            s = body.decode("utf-8", errors="ignore")
            if "tls" in s or "SSL" in s or "cipher" in s:
                # simple heuristic
                if "weak" in s or "downgrad" in s:
                    label = b"weak"
                elif "legacy" in s:
                    label = b"legacy"
        except Exception:
            pass
except Exception:
    pass

proof = hashlib.sha256(label + shared_secret).hexdigest()

claim = {
    "proof_hex": proof,
    "label": label.decode("utf-8", errors="ignore") if isinstance(label, bytes) else str(label),
    "client_pub_hex": client_pub_bytes.hex()
}

print("CLAIM:" + json.dumps(claim), flush=True)