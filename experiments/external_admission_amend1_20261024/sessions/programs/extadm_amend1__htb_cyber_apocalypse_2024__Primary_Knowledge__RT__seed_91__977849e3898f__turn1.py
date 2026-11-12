import base64
import math
from functools import reduce

# Decode the files
with open('output.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    n = int(lines[0].split(' = ')[1])
    e = int(lines[1].split(' = ')[1])
    c = int(lines[2].split(' = ')[1])

# From source.py analysis:
# n = math.prod([getPrime(1024) for _ in range(2**0)])
# 2**0 = 1, so n is the product of exactly 1 prime
# This means n is prime itself!

# For RSA with n = p (a prime), phi(n) = p - 1 = n - 1
phi_n = n - 1

# Calculate d = e^(-1) mod phi(n)
def egcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = egcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def modinv(a, m):
    gcd, x, y = egcd(a, m)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    return (x % m + m) % m

d = modinv(e, phi_n)

# Decrypt: m = c^d mod n
m = pow(c, d, n)

# Convert to bytes
def long_to_bytes(n):
    if n == 0:
        return b'\x00'
    byte_list = []
    while n > 0:
        byte_list.append(n & 0xff)
        n >>= 8
    return bytes(reversed(byte_list))

flag_bytes = long_to_bytes(m)
flag = flag_bytes.decode('utf-8', errors='ignore')

print(flag)