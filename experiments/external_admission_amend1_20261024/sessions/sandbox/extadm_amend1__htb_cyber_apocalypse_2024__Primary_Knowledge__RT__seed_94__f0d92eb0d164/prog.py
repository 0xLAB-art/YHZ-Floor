import base64
import math
from functools import reduce

# Decode the source.py file
source_b64 = "aW1wb3J0IG1hdGgKZnJvbSBDcnlwdG8uVXRpbC5udW1iZXIgaW1wb3J0IGdldFByaW1lLCBieXRlc190b19sb25nCmZyb20gc2VjcmV0IGltcG9ydCBGTEFHCgptID0gYnl0ZXNfdG9fbG9uZyhGTEFHKQoKbiA9IG1hdGgucHJvZChbZ2V0UHJpbWUoMTAyNCkgZm9yIF8gaW4gcmFuZ2UoMioqMCldKQplID0gMHgxMDAwMQpjID0gcG93KG0sIGUsIG4pCgp3aXRoIG9wZW4oJ291dHB1dC50eHQnLCAndycpIGFzIGY6CiAgICBmLndyaXRlKGYne24gPSB9XG4nKQogICAgZi53cml0ZShmJ3tlID0gfVxuJykKICAgIGYud3JpdGUoZid7YyA9IH1cbicp"
source_text = base64.b64decode(source_b64).decode()

# Read output.txt
with open('output.txt', 'r') as f:
    output_text = f.read()

# Parse n, e, c from output.txt
lines = output_text.strip().split('\n')
n = int(lines[0].split(' = ')[1])
e = int(lines[1].split(' = ')[1])
c = int(lines[2].split(' = ')[1])

# From source.py: n = math.prod([getPrime(1024) for _ in range(2**0)])
# 2**0 = 1, so n is the product of exactly 1 prime of 1024 bits
# This means n itself is prime!

# For RSA with n being prime (not a product of two primes):
# phi(n) = n - 1 (Euler's totient for a prime)
phi_n = n - 1

# Compute d = e^(-1) mod phi(n)
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    gcd, x, _ = extended_gcd(e, phi)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    return x % phi

d = mod_inverse(e, phi_n)

# Decrypt: m = c^d mod n
m = pow(c, d, n)

# Convert m to bytes
def long_to_bytes(n):
    if n == 0:
        return b'\x00'
    bytes_array = []
    while n > 0:
        bytes_array.append(n & 0xff)
        n >>= 8
    return bytes(reversed(bytes_array))

flag_bytes = long_to_bytes(m)
flag = flag_bytes.decode('ascii')

print(flag)