#!/usr/bin/env python3
"""Reference solver — eps (CSAW 2015 Quals, crypto).

Criterion-5 verification artifact for Amendment 3.  Stdlib-only; reads exactly
the declared handout file (the '.mpeg' artifact) by bare name.

The artifact is a whitespace-separated bit string: every 8 bits spell one ASCII
character.  Decoding it yields the challenge text, whose first flag-shaped
token is the answer.  No answer material is embedded.

No pinned-answer bytes are embedded in this source.
"""

import re


def main():
    raw = open("eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg", "r").read()
    bits = "".join(raw.split())
    if set(bits) - {"0", "1"}:
        raise SystemExit(1)
    text = "".join(chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits) - 7, 8))
    match = re.search(r"flag\{[ -~]*?\}", text)
    if not match:
        raise SystemExit(1)
    print(match.group(0))


if __name__ == "__main__":
    main()
