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

def factor_fermat(n):
    a = isqrt(n)
    if a * a == n:
        return a, a
    while True:
        a += 1
        b2 = a * a - n
        b = isqrt(b2)
        if b * b == b2:
            return a - b, a + b

def mod_inverse(e, phi):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd_val, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd_val, x, y
    
    _, x, _ = extended_gcd(e, phi)
    return (x % phi + phi) % phi

def long_to_bytes(n):
    if n == 0:
        return b'\x00'
    bytes_list = []
    while n > 0:
        bytes_list.append(n & 0xff)
        n >>= 8
    return bytes(reversed(bytes_list))

# Read values
with open('output.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    n = int(lines[0].split(' = ')[1])
    e = int(lines[1].split(' = ')[1])
    c = int(lines[2].split(' = ')[1])

# The source shows 2**0 = 1 prime is generated, so n is just a single prime
# This means RSA is broken - we can't factor n into p*q because it IS prime
# However, for a prime modulus, phi(n) = n - 1
# So we can compute d = e^-1 mod (n-1)

phi = n - 1
d = mod_inverse(e, phi)
m = pow(c, d, n)
flag = long_to_bytes(m)
print(flag.decode())