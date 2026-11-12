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
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_nonce_and_key(r, s1, z1, s2, z2, n):
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s1 * k - z1) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    return d, k

with open(sys.argv[1]) as f:
    data = json.load(f)

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

r = int(data['signature_1']['r'], 16)
s1 = int(data['signature_1']['s'], 16)
z1 = int(data['signature_1']['z'], 16)
s2 = int(data['signature_2']['s'], 16)
z2 = int(data['signature_2']['z'], 16)

d, k = recover_nonce_and_key(r, s1, z1, s2, z2, n)

print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))