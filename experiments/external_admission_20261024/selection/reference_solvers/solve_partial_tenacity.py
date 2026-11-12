import sys, hashlib, math
lines = open(sys.argv[1]).read().splitlines()
n = int(lines[0].split(" = ")[1]); ct = bytes.fromhex(lines[1].split(" = ")[1])
P_HINT = int(lines[2].split(" = ")[1]); Q_HINT = int(lines[3].split(" = ")[1])

def bruteforce_digit(i, n, known_prime, prime_to_check, hint_prime):
    msk = 10 ** (i + 1)
    known_prime = 10 ** i * (hint_prime % 10) + known_prime
    for d in range(10):
        test_prime = 10 ** i * d + prime_to_check
        if n % msk == known_prime * test_prime % msk:
            return known_prime, test_prime, hint_prime // 10
    raise ValueError(f"no candidate at digit {i}")

prime_len = len(str(math.isqrt(n)))
p = q = 0
hp, hq = P_HINT, Q_HINT
for i in range(prime_len):
    if (prime_len - 1 - i) % 2 == 0:
        p, q, hp = bruteforce_digit(i, n, p, q, hp)
    else:
        q, p, hq = bruteforce_digit(i, n, q, p, hq)
assert n == p * q

e = 0x10001
d = pow(e, -1, (p - 1) * (q - 1))
k = (n.bit_length() + 7) // 8
em = pow(int.from_bytes(ct, "big"), d, n).to_bytes(k, "big")
hLen = 20
def mgf1(seed, length):
    out = b""
    for c in range((length + hLen - 1) // hLen):
        out += hashlib.sha1(seed + c.to_bytes(4, "big")).digest()
    return out[:length]
lHash = hashlib.sha1(b"").digest()
maskedSeed, maskedDB = em[1:1 + hLen], em[1 + hLen:]
seed = bytes(a ^ b for a, b in zip(maskedSeed, mgf1(maskedDB, hLen)))
db = bytes(a ^ b for a, b in zip(maskedDB, mgf1(seed, len(maskedDB))))
assert db[:hLen] == lHash, "lHash mismatch"
idx = db.index(b"\x01", hLen)
print(db[idx + 1:].decode())
