#!/usr/bin/env python3
import json
import sys

def modinv(a, m):
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = egcd(a % m, m)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    return (x % m + m) % m

def solve_ecdsa_nonce_reuse(data):
    n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    
    r1 = int(data['signature_1']['r'], 16)
    s1 = int(data['signature_1']['s'], 16)
    z1 = int(data['signature_1']['z'], 16)
    
    r2 = int(data['signature_2']['r'], 16)
    s2 = int(data['signature_2']['s'], 16)
    z2 = int(data['signature_2']['z'], 16)
    
    # k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) * modinv(s1 - s2, n)) % n
    
    # d = (s1 * k - z1) / r1 mod n
    d = ((s1 * k - z1) * modinv(r1, n)) % n
    
    return {
        "d": format(d, '064x'),
        "k": format(k, '064x')
    }

with open(sys.argv[1]) as f:
    data = json.load(f)

result = solve_ecdsa_nonce_reuse(data)
print(json.dumps(result))
