import re

data = open('encrypted').read().strip()

# Split into (len, type, payload) records
records = []
i = 0
while i < len(data):
    length = int(data[i:i+2], 16)
    typ = data[i+2:i+4]
    payload = data[i+4:i+4+length*2]
    records.append((length, typ, payload))
    i += 4 + length*2

# Find the record whose type is 'FLAG'
for length, typ, payload in records:
    if typ == 'FLAG':
        print(payload)
        break
