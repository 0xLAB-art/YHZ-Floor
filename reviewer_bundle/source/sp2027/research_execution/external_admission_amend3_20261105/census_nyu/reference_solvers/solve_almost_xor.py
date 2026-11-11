#!/usr/bin/env python3
"""Reference solver — almost_xor (CSAW 2017 Quals, crypto).

Criterion-5 verification artifact for Amendment 3.  Stdlib-only; reads exactly
the declared handout files ('almostxor.py', 'ciphertext') as bare names in the
working directory, and uses only the standard flag shape ('flag{...}').

The handout's cipher is byte-group addition mod 2^n ("almost xor") with a
byte-repeated key.  The known plaintext prefix 'flag{' determines the key
chunks at offsets 0..n-1 and, for n=3, the first two chunks once the single
unknown plaintext byte in chunk 1 is swept over printable ASCII.  Candidate
key periods are derived from the recovered key material itself (no answer
material involved); a candidate is accepted only when the full decryption is
printable ASCII and contains the flag shape.

No pinned-answer bytes are embedded in this source.
"""

import re


def get_vals(chunk, n):
    x = int.from_bytes(chunk, "big")
    mask = (1 << n) - 1
    vals = []
    for _ in range(8):
        vals.append(x & mask)
        x >>= n
    vals.reverse()
    return vals


def get_chrs(vals, n):
    x = 0
    for v in vals:
        x = (x << n) | v
    return x.to_bytes(n, "big")


def known_key_chunk(cipher_chunk, plain_chunk, n):
    cv = get_vals(cipher_chunk, n)
    pv = get_vals(plain_chunk, n)
    return get_chrs([(c - p) % (1 << n) for c, p in zip(cv, pv)], n)


def decrypt_chunk(cipher_chunk, key_chunk, n):
    cv = get_vals(cipher_chunk, n)
    kv = get_vals(key_chunk, n)
    return get_chrs([(c - k) % (1 << n) for c, k in zip(cv, kv)], n)


def main():
    cipher = bytes.fromhex(open("ciphertext").read().strip())
    prefix = b"flag{"
    found = None

    for n in (2, 3):
        if len(prefix) < n:
            continue
        key0 = known_key_chunk(cipher[:n], prefix[:n], n)
        partial = prefix[n:2 * n]
        if len(partial) == n:
            guesses = [partial]
        elif len(partial) == n - 1:
            guesses = [partial + bytes([c]) for c in range(32, 127)]
        else:
            continue

        for guess in guesses:
            key = key0 + known_key_chunk(cipher[n:2 * n], guess, n)
            for length in range(1, len(key) + 1):
                if any(key[i] != key[i % length] for i in range(len(key))):
                    continue
                stream = (key[:length] * (len(cipher) // length + 1))[:len(cipher)]
                plain = b"".join(
                    decrypt_chunk(cipher[i:i + n], stream[i:i + n], n)
                    for i in range(0, len(cipher), n)
                )
                if not all(32 <= b < 127 for b in plain):
                    continue
                match = re.search(rb"flag\{[ -~]*?\}", plain)
                if match:
                    found = match.group(0).decode()
                    break
            if found:
                break
        if found:
            break

    if not found:
        raise SystemExit(1)
    print(found)


if __name__ == "__main__":
    main()
