import math
from functools import reduce

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def isqrt(n):
    if n < 0:
        raise ValueError("Square root of negative number")
    if n == 0:
        return 0
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

def bytes_to_long(s):
    return int.from_bytes(s, 'big')

def long_to_bytes(n):
    if n == 0:
        return b'\x00'
    return n.to_bytes((n.bit_length() + 7) // 8, 'big')

# Read values from output.txt
with open('output.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    n = int(lines[0].split(' = ')[1])
    e = int(lines[1].split(' = ')[1])
    c = int(lines[2].split(' = ')[1])

# Analyze source.py: n = math.prod([getPrime(1024) for _ in range(2**0)])
# 2**0 = 1, so only ONE prime is generated
# This means n is just a single prime, not a product of two primes!
# RSA with n = p (single prime) is trivially broken

# For single prime RSA:
# phi(n) = phi(p) = p - 1
phi_n = n - 1

# Calculate d = e^(-1) mod phi(n)
def modinv(a, m):
    if gcd(a, m) != 1:
        return None
    u1, u2, u3 = 1, 0, a
    v1, v2, v3 = 0, 1, m
    while v3 != 0:
        q = u3 // v3
        v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
    return u1 % m

d = modinv(e, phi_n)

# Decrypt: m = c^d mod n
m = pow(c, d, n)

# Convert to bytes and decode
flag = long_to_bytes(m).decode('ascii')

print(flag)