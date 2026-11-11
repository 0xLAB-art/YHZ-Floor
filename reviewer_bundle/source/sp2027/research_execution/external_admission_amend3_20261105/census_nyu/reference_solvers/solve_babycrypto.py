#!/usr/bin/env python3
"""Reference solver — babycrypto (CSAW 2018 Quals, crypto).

Criterion-5 verification artifact for Amendment 3.  Stdlib-only; reads exactly
the declared handout file ('ciphertext.txt').

The declared artifact is base64 text.  The task statement describes a "single
yeet" construction; the ciphertext is a single-byte-XOR encoding of an English
plaintext followed by the flag.  The solver sweeps all 256 single-byte keys and
accepts the decryption that exposes the standard flag shape in printable ASCII.

No pinned-answer bytes are embedded in this source.
"""

import base64
import re


def main():
    blob = base64.b64decode(open("ciphertext.txt", "rb").read().strip())
    for key in range(256):
        candidate = bytes(b ^ key for b in blob)
        match = re.search(rb"flag\{[ -~]*?\}", candidate)
        if match and all(32 <= b < 127 or b == 10 for b in candidate):
            print(match.group(0).decode())
            return
    raise SystemExit(1)


if __name__ == "__main__":
    main()
