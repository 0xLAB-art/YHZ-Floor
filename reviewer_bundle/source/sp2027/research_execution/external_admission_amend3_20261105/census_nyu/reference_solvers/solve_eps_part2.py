#!/usr/bin/env python3
"""Reference solver — eps_part2 (CSAW 2015 Quals, crypto).

Criterion-5 verification artifact for Amendment 3.  Stdlib-only; reads exactly
the declared handout file (the '.avi' artifact) by bare name.

The artifact is base64 text; decoding it yields the challenge message, whose
flag-shaped token is the answer.  No answer material is embedded.

No pinned-answer bytes are embedded in this source.
"""

import base64
import re


def main():
    raw = open("eps1.9_zer0-day_b7604a922c8feef666a957933751a074.avi", "rb").read()
    # the artifact embeds literal "\\n" separators inside the base64 stream;
    # 'n' is a valid base64 character, so the two-character sequence must be
    # removed before decoding rather than left to the decoder's filter.
    payload = raw.replace(b"\\n", b"").replace(b"\r", b"").replace(b"\n", b"").strip()
    text = base64.b64decode(payload).decode("latin-1")
    match = re.search(r"flag\{[ -~]*?\}", text)
    if not match:
        raise SystemExit(1)
    print(match.group(0))


if __name__ == "__main__":
    main()
