import re

data = open('encrypted').read().strip()

# The ciphertext is a hex string. Interpret it as bytes.
raw = bytes.fromhex(data)

# The data appears to be a sequence of length-prefixed records.
# Each record: 1 byte length, then `length` bytes of payload.
records = []
i = 0
while i < len(raw):
    length = raw[i]
    i += 1
    if i + length > len(raw):
        break
    records.append(raw[i:i+length])
    i += length

# Find the record containing the flag-like string "FLAG"
for rec in records:
    try:
        text = rec.decode('ascii')
    except UnicodeDecodeError:
        continue
    if 'FLAG' in text:
        # Extract the flag portion
        m = re.search(r'FLAG\{[^}]*\}', text)
        if m:
            print(m.group(0))
            break
else:
    # Fallback: print all records that look like they contain the flag
    for rec in records:
        try:
            text = rec.decode('ascii')
            if 'FLAG' in text:
                print(text)
        except UnicodeDecodeError:
            pass