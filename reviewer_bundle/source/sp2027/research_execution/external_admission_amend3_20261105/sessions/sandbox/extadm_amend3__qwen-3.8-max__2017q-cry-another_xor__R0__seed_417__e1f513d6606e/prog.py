import sys

data = open('encrypted', 'rb').read().strip()
assert all(c in b'0123456789abcdefABCDEF' for c in data)
buf = bytes.fromhex(data.decode())

# Find the longest run of bytes >= 0x80 (likely a key stream / XOR mask)
mask = b''
start = None
for i, b in enumerate(buf):
    if b >= 0x80:
        if start is None:
            start = i
    else:
        if start is not None:
            if len(buf) - start > len(mask):
                mask = buf[start:]
            start = None
if start is not None and len(buf) - start > len(mask):
    mask = buf[start:]

# XOR the whole buffer with the mask (repeating)
out = bytearray()
for i, b in enumerate(buf):
    out.append(b ^ mask[i % len(mask)])

print(out.decode('latin-1'))
