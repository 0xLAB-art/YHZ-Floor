import sys

with open('encrypted', 'rb') as f:
    data = f.read().strip()

buf = bytearray.fromhex(data.decode('ascii').strip())

# Find the XOR key by locating the known CTF flag prefix "flag{"
key = bytearray(256)
for i in range(5):
    key[buf[i] ^ ord('flag{')[i]] = buf[i] ^ ord('flag{')[i]

# Verify key consistency and recover full key
key = bytearray(256)
for i in range(len(buf)):
    c = buf[i]
    p = chr(c ^ key[c])
    if key[c] == 0 and not (p.isprintable() or p in '\n\r'):
        # tentative
        pass

# Simpler: derive key from known plaintext "flag{"
key = [0] * 256
for i in range(5):
    key[buf[i]] = buf[i] ^ ord('flag{')[i]

# Extend key using known structure: after flag{ comes the flag content, then "}"
# Try to find closing brace
result = bytearray()
for i in range(len(buf)):
    k = key[buf[i]]
    if k == 0:
        # derive from context
        k = buf[i] ^ ord('}') if i == len(buf) - 1 else buf[i] ^ ord('}')
    result.append(buf[i] ^ k)

print(result.decode('ascii'))
