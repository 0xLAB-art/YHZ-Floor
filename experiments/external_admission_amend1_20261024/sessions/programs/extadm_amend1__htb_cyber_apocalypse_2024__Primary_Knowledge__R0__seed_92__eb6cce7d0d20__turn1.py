import math
from typing import Optional

def isqrt(n: int) -> int:
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

def is_perfect_power(n: int, max_exp: int = 100) -> Optional[tuple[int, int]]:
    for k in range(2, max_exp + 1):
        root = int(round(n ** (1.0 / k)))
        for candidate in [root - 1, root, root + 1]:
            if candidate > 1 and candidate ** k == n:
                return (candidate, k)
    return None

def trial_division(n: int, limit: int = 10**7) -> Optional[int]:
    if n % 2 == 0:
        return 2
    for i in range(3, min(limit, isqrt(n) + 1), 2):
        if n % i == 0:
            return i
    return None

def mod_inverse(a: int, m: int) -> int:
    def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def long_to_bytes(n: int) -> bytes:
    if n == 0:
        return b'\x00'
    byte_length = (n.bit_length() + 7) // 8
    return n.to_bytes(byte_length, 'big')

with open('output.txt', 'r') as f:
    content = f.read()
    
for line in content.strip().split('\n'):
    if line.startswith('n = '):
        n = int(line.split(' = ')[1])
    elif line.startswith('e = '):
        e = int(line.split(' = ')[1])
    elif line.startswith('c = '):
        c = int(line.split(' = ')[1])

power_result = is_perfect_power(n)
if power_result:
    base, exp = power_result
    factor = trial_division(base)
    if factor:
        p = factor
        q = base // p
    else:
        p = base
        q = 1
else:
    factor = trial_division(n)
    if factor:
        p = factor
        q = n // p
    else:
        p = n
        q = 1

if q > 1:
    phi = (p - 1) * (q - 1)
    d = mod_inverse(e, phi)
    m = pow(c, d, n)
    flag = long_to_bytes(m)
    print(flag.decode())
else:
    print("Could not factor n")