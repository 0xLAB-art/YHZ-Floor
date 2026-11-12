import binascii

with open('ciphertext', 'rb') as f:
    raw = b''.join(f.read().split())
ciphertext = binascii.unhexlify(raw)


def unpack_values(data, n):
    bit_count = 8 * len(data)
    if bit_count % n:
        return None
    value = int.from_bytes(data, 'big')
    mask = (1 << n) - 1
    return [
        (value >> (bit_count - n * (i + 1))) & mask
        for i in range(bit_count // n)
    ]


def pack_values(values, n):
    value = 0
    for item in values:
        value = (value << n) | item
    return value.to_bytes((len(values) * n) // 8, 'big')


def derive_key(cipher_prefix, plain_prefix, n):
    cvals = unpack_values(cipher_prefix, n)
    pvals = unpack_values(plain_prefix, n)
    if cvals is None or pvals is None:
        return None
    mask = (1 << n) - 1
    return pack_values([(c - p) & mask for c, p in zip(cvals, pvals)], n)


def decrypt(data, key, n):
    repeated = (key * ((len(data) + len(key) - 1) // len(key)))[:len(data)]
    cvals = unpack_values(data, n)
    kvals = unpack_values(repeated, n)
    mask = (1 << n) - 1
    return pack_values([(c - k) & mask for c, k in zip(cvals, kvals)], n)


prefix = b'flag{'
answers = set()

for n in range(1, 8):
    if len(ciphertext) % n:
        continue
    for key_length in range(1, len(prefix) + 2):
        if (8 * key_length) % n:
            continue
        if key_length <= len(prefix):
            seeds = [prefix[:key_length]]
        else:
            seeds = [prefix + bytes([c]) for c in range(32, 127)]

        for seed in seeds:
            key = derive_key(ciphertext[:key_length], seed, n)
            if key is None:
                continue
            plain = decrypt(ciphertext, key, n)
            if not plain.startswith(prefix) or not plain.endswith(b'}'):
                continue
            if plain.count(b'{') != 1 or plain.count(b'}') != 1:
                continue
            if not all(32 <= c < 127 for c in plain):
                continue
            answers.add(plain)

if len(answers) != 1:
    raise RuntimeError('cryptanalysis did not produce a unique flag')

print(next(iter(answers)).decode('ascii'))
