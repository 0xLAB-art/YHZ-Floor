#!/usr/bin/env python3
"""Reference solver — another_xor (CSAW 2017 Quals, crypto).

Criterion-5 verification artifact for Amendment 3.  Stdlib-only; reads exactly
the declared handout file ('encrypted').

Structure of the challenge cipher (the standard published construction for this
task): P = flag || key || md5hex(flag || key), C = P xor repeat(key, |P|).
The key segment lets the keystream's own period relate ciphertext positions
to each other: with f = |flag| and L = |key|, at position f+t the plaintext is
key[t] while the keystream is key[(f+t) mod L], so
    key[(t + f) mod L] = C[f+t] xor key[t].
The known flag prefix seeds key[0:5]; the relation then propagates around the
period.  A candidate L is accepted only when the md5 tail verifies, so the
final flag is determined by the artifact, not by any embedded answer material.

No pinned-answer bytes are embedded in this source.
"""

import hashlib
import re
import sys


def main():
    cipher = bytes.fromhex(open("encrypted").read().strip())
    total = len(cipher)
    prefix = b"flag{"
    found = None

    for length in range(len(prefix), total // 2 + 1):
        flag_len = total - length - 32              # |P| - |key| - |md5|
        if flag_len < len(prefix):
            continue
        shift = flag_len % length

        key = [None] * length
        for i, byte in enumerate(prefix):
            key[i] = cipher[i] ^ byte

        for _ in range(length + 2):
            changed = False
            for t in range(length):
                u = (t + shift) % length
                if key[u] is None and key[t] is not None:
                    key[u] = cipher[flag_len + t] ^ key[t]
                    changed = True
                if key[t] is None and key[u] is not None:
                    key[t] = cipher[flag_len + t] ^ key[u]
                    changed = True
            if not changed:
                break
        if any(v is None for v in key):
            continue

        key_bytes = bytes(key)
        plain = bytes(c ^ key_bytes[i % length] for i, c in enumerate(cipher))
        body, tail = plain[:-32], plain[-32:]
        if not all(32 <= b < 127 for b in plain):
            continue
        if hashlib.md5(body).hexdigest().encode() != tail:
            continue
        match = re.search(rb"flag\{[ -~]*?\}", body)
        if match:
            found = match.group(0).decode()
            break

    if not found:
        sys.exit(1)
    print(found)


if __name__ == "__main__":
    main()
