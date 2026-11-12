import re

data = open('encrypted').read().strip()

# The ciphertext is a hex string. Decode it to bytes.
raw = bytes.fromhex(data)

# The pattern: each byte is XORed with a repeating key derived from a simple
# counter / position. Let's try XOR with a repeating key based on position.
# First, try a simple repeating key of increasing values.

# Let's analyze: try XOR with key = position % n for various n, or a fixed key.

# Try XOR with a single byte key first
for key in range(256):
    dec = bytes(b ^ key for b in raw)
    try:
        s = dec.decode('ascii')
        if 'flag' in s.lower() or 'CTF' in s or all(c.isprintable() for c in s):
            print('single key:', key, repr(s))
    except:
        pass

# Try repeating key of length 2..16
for klen in range(1, 17):
    best = None
    for key in range(256 ** min(klen, 4)):
        pass

# More practical: try known-plaintext style. The message likely starts with "flag" or similar.
# Try XOR with key derived from position: key[i] = i % 256 etc.
for klen in range(1, 33):
    for start in range(256):
        key = bytes((start + i) % 256 for i in range(klen))
        dec = bytes(raw[i] ^ key[i % klen] for i in range(len(raw)))
        try:
            s = dec.decode('ascii')
            if all(c.isprintable() for c in s) and ('flag' in s.lower() or 'CTF' in s or 'secret' in s.lower()):
                print('seq key', klen, start, repr(s))
        except:
            pass

# Try repeating key where key[i] = (i * a + b) % 256
for a in range(1, 256):
    for b in range(256):
        key = bytes((a * i + b) % 256 for i in range(len(raw)))
        dec = bytes(raw[i] ^ key[i] for i in range(len(raw)))
        try:
            s = dec.decode('ascii')
            if all(c.isprintable() for c in s) and ('flag' in s.lower() or 'CTF' in s):
                print('linear key', a, b, repr(s))
        except:
            pass
