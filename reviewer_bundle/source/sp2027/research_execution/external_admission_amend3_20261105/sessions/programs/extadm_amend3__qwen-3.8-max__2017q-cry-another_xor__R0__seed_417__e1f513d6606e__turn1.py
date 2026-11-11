import re

data = open('encrypted').read().strip()

# The ciphertext is a hex string. Interpret as bytes.
raw = bytes.fromhex(data)

# The structure appears to be a sequence of length-prefixed records.
# Each record: 1 byte length, then length bytes of data.
records = []
pos = 0
while pos < len(raw):
    length = raw[pos]
    pos += 1
    records.append(raw[pos:pos + length])
    pos += length

# Each record seems to be a length-prefixed string (1 byte length + string).
# Let's decode each record as a length-prefixed string.
parts = []
for rec in records:
    if len(rec) >= 1:
        slen = rec[0]
        parts.append(rec[1:1 + slen].decode('ascii', errors='replace'))

# Join parts and look for the flag pattern.
joined = ''.join(parts)

# Search for flag-like patterns.
for pat in [r'flag\{[^}]*\}', r'CTF\{[^}]*\}', r'FLAG\{[^}]*\}']:
    m = re.search(pat, joined)
    if m:
        print(m.group(0))
        break
else:
    # If no pattern found, print the joined string for inspection.
    print(joined)
