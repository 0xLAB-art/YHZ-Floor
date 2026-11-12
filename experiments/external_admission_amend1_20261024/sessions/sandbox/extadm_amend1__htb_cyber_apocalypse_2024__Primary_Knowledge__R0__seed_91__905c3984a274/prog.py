import math
from functools import reduce

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

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def egcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd_val, x1, y1 = egcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd_val, x, y

def mod_inv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

# Read output.txt
with open('output.txt', 'r') as f:
    lines = f.readlines()
    n = int(lines[0].split(' = ')[1])
    e = int(lines[1].split(' = ')[1])
    c = int(lines[2].split(' = ')[1])

# The source.py shows: n = math.prod([getPrime(1024) for _ in range(2**0)])
# 2**0 = 1, so only ONE prime is generated
# This means n is just a single prime p, not a product of two primes
# RSA with n = p (prime) is broken because phi(p) = p - 1

# Since n is prime, phi(n) = n - 1
phi = n - 1

# Calculate d, the private exponent
d = mod_inv(e, phi)

# Decrypt the ciphertext
m = pow(c, d, n)

# Convert to bytes and print
flag_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
print(flag_bytes.decode('ascii'))