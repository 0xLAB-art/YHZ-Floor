import math
import re

with open("encrypted", "r", encoding="ascii") as f:
    ciphertext = bytes.fromhex(f.read())

n = len(ciphertext)
solutions = set()

# The plaintext record has the form flag|key|32-hex-digest, and the key
# (including its trailing separator) is used as a repeating XOR key.
for key_len in range(2, n - 32):
    key_offset = n - key_len - 32
    if key_offset < 7 or math.gcd(key_offset, key_len) != 1:
        continue

    key = [None] * key_len
    key[0] = ciphertext[0] ^ ord("f")
    j = 0
    valid = True

    for _ in range(key_len):
        nxt = (j + key_offset) % key_len
        value = key[j] ^ ciphertext[key_offset + j]
        if key[nxt] is not None and key[nxt] != value:
            valid = False
            break
        key[nxt] = value
        j = nxt

    if not valid or any(value is None for value in key):
        continue

    key_bytes = bytes(key)
    if key_bytes[-1:] != b"|" or any(value < 32 or value > 126 for value in key_bytes):
        continue

    plaintext = bytes(
        value ^ key_bytes[i % key_len] for i, value in enumerate(ciphertext)
    )
    head = plaintext[:key_offset]
    middle = plaintext[key_offset:key_offset + key_len]
    digest = plaintext[key_offset + key_len:]

    if middle != key_bytes:
        continue
    if re.fullmatch(rb"flag\{[A-Za-z0-9_]+\}\|", head) is None:
        continue
    if re.fullmatch(rb"[0-9a-f]{32}", digest) is None:
        continue

    solutions.add(head[:-1].decode("ascii"))

if len(solutions) != 1:
    raise RuntimeError("unable to determine a unique flag")

print(solutions.pop())
