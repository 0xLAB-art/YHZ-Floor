import itertools


def symbols(data, n):
    x = int.from_bytes(data, 'big')
    mask = (1 << n) - 1
    return [(x >> shift) & mask
            for shift in range(8 * len(data) - n, -1, -n)]


def decrypt(cipher_symbols, key, n, size):
    repeated = (key * ((size + len(key) - 1) // len(key)))[:size]
    mask = (1 << n) - 1
    value = 0
    for c, k in zip(cipher_symbols, symbols(repeated, n)):
        value = (value << n) | ((c - k) & mask)
    return value.to_bytes(size, 'big')


def main():
    with open('ciphertext', 'r', encoding='ascii') as f:
        ciphertext = bytes.fromhex(f.read())
    size = len(ciphertext)
    prefix, suffix = b'flag{', b'}'

    # Known flag framing supplies modular-difference constraints on key bits.
    known_plaintext = [None] * (8 * size)
    for offset, text in ((0, prefix), (size - len(suffix), suffix)):
        for i, byte in enumerate(text):
            for bit in range(8):
                known_plaintext[8 * (offset + i) + bit] = (byte >> (7 - bit)) & 1

    cases = []
    for n in range(1, 8):
        if size % n:
            continue
        cvals = symbols(ciphertext, n)
        constraints = []
        for index, c in enumerate(cvals):
            offset = index * n
            bits = known_plaintext[offset:offset + n]
            if any(bit is None for bit in bits):
                continue
            m = 0
            for bit in bits:
                m = (m << 1) | bit
            constraints.append((offset, (c - m) & ((1 << n) - 1)))
        cases.append((n, cvals, constraints))

    # Search byte-periodic keys in increasing period, without assuming n.
    for key_length in range(1, size + 1):
        answers = set()
        period = 8 * key_length
        for n, cvals, constraints in cases:
            key_bits = [-1] * period
            consistent = True
            for offset, value in constraints:
                for bit in range(n):
                    position = (offset + bit) % period
                    required = (value >> (n - 1 - bit)) & 1
                    if key_bits[position] not in (-1, required):
                        consistent = False
                        break
                    key_bits[position] = required
                if not consistent:
                    break
            if not consistent:
                continue

            free = [i for i, bit in enumerate(key_bits) if bit == -1]
            for assignment in itertools.product((0, 1), repeat=len(free)):
                for position, bit in zip(free, assignment):
                    key_bits[position] = bit
                key_value = 0
                for bit in key_bits:
                    key_value = (key_value << 1) | bit
                key = key_value.to_bytes(key_length, 'big')
                plaintext = decrypt(cvals, key, n, size)
                if (plaintext.startswith(prefix) and plaintext.endswith(suffix)
                        and all(32 <= byte <= 126 for byte in plaintext)):
                    answers.add(plaintext)

        if answers:
            if len(answers) != 1:
                raise RuntimeError('Ambiguous minimum-period decryption')
            print(next(iter(answers)).decode('ascii'))
            return
    raise RuntimeError('No valid decryption found')


if __name__ == '__main__':
    main()
