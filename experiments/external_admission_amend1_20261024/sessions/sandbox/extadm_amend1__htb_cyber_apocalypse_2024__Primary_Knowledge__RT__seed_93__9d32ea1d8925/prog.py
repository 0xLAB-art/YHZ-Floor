import base64
import math
from functools import reduce

# Decode the source.py file
source_b64 = "aW1wb3J0IG1hdGgKZnJvbSBDcnlwdG8uVXRpbC5udW1iZXIgaW1wb3J0IGdldFByaW1lLCBieXRlc190b19sb25nCmZyb20gc2VjcmV0IGltcG9ydCBGTEFHCgptID0gYnl0ZXNfdG9fbG9uZyhGTEFHKQoKbiA9IG1hdGgucHJvZChbZ2V0UHJpbWUoMTAyNCkgZm9yIF8gaW4gcmFuZ2UoMioqMCldKQplID0gMHgxMDAwMQpjID0gcG93KG0sIGUsIG4pCgp3aXRoIG9wZW4oJ291dHB1dC50eHQnLCAndycpIGFzIGY6CiAgICBmLndyaXRlKGYne24gPSB9XG4nKQogICAgZi53cml0ZShmJ3tlID0gfVxuJykKICAgIGYud3JpdGUoZid7YyA9IH1cbicp"
source = base64.b64decode(source_b64).decode()

# Read output.txt
with open('output.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    n = int(lines[0].split(' = ')[1])
    e = int(lines[1].split(' = ')[1])
    c = int(lines[2].split(' = ')[1])

# From source.py: n = math.prod([getPrime(1024) for _ in range(2**0)])
# 2**0 = 1, so n is the product of exactly 1 prime
# This means n itself is prime!

# Since n is prime, phi(n) = n - 1
phi = n - 1

# Compute d, the modular inverse of e mod phi
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def modinv(a, m):
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    return (x % m + m) % m

d = modinv(e, phi)

# Decrypt: m = c^d mod n
m = pow(c, d, n)

# Convert to bytes
def long_to_bytes(n):
    if n == 0:
        return b'\x00'
    bytes_list = []
    while n > 0:
        bytes_list.append(n & 0xff)
        n >>= 8
    return bytes(reversed(bytes_list))

flag = long_to_bytes(m).decode()
print(flag)