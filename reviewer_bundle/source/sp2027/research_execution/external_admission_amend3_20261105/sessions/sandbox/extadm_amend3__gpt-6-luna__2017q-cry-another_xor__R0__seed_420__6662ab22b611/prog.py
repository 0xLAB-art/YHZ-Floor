import binascii

data = binascii.unhexlify(open('encrypted', 'rb').read().strip())

# The ciphertext is a sequence of length-prefixed records.
# Each record: [len_byte][data_bytes]
records = []
i = 0
while i < len(data):
    length = data[i]
    i += 1
    records.append(data[i:i+length])
    i += length

# Each record is XORed with a repeating key derived from its position.
# The key pattern: key = bytes([ (i % 256) ^ 0x5A ])
# Try XOR with key based on record index.

for idx, rec in enumerate(records):
    key = bytes([(idx + j) % 256 for j in range(len(rec))])
    decrypted = bytes([a ^ b for a, b in zip(rec, key)])
    print(idx, decrypted)
