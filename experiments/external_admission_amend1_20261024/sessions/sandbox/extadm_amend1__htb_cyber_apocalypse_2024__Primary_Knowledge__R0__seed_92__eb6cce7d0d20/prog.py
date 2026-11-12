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

with open('output.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    n = int(lines[0].split(' = ')[1])
    e = int(lines[1].split(' = ')[1])
    c = int(lines[2].split(' = ')[1])

p, q = factor_fermat(n)
phi = (p - 1) * (q - 1)
d = mod_inverse(e, phi)
m = pow(c, d, n)

flag_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
flag = flag_bytes.decode('ascii')
print(flag)