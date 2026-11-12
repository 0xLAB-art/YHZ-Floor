import re

data = open('encrypted').read().strip()

# Split into 2-byte big-endian words
words = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]

# Find the repeating key pattern by XORing consecutive words
# The cipher appears to be a repeating XOR with a short key
# Try to detect key length via autocorrelation / repeated patterns

def find_key_length(words):
    n = len(words)
    best = None
    for k in range(1, 33):
        score = 0
        for i in range(k, n):
            if words[i] == words[i-k]:
                score += 1
        if best is None or score > best[0]:
            best = (score, k)
    return best[1]

key_len = find_key_length(words)

# Recover key by XORing words at same position mod key_len
key = []
for j in range(key_len):
    x = words[j]
    for i in range(j + key_len, len(words), key_len):
        x ^= words[i]
    key.append(x)

# Decrypt
flag = ''.join(chr(words[i] ^ key[i % key_len]) for i in range(len(words)))
print(flag)
