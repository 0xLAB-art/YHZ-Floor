#!/usr/bin/env python3
"""Reference solver — DES 2 Bites (CSAW 2019 Quals, crypto).

Criterion-5 verification artifact for Amendment 3.  Stdlib-only (binascii, re,
sys); reads exactly the declared handout files ('DES2Bytes.txt',
'DES2Bytes.enc', 'FLAG.enc', 'Generator.py' is inspected only as documentation)
by bare name in the working directory.

Construction (stated by the declared Generator.py):
  * two layers of DES-OFB with IV b"13371337" and two "weak" keys;
  * every resulting ciphertext byte is re-encoded as four decimal fields of
    8 characters, each field = nibble + 9133337.

Attack, derived from the artifacts and public DES weak-key material:
  * an OFB keystream depends only on (key, IV); the two-layer effective
    keystream S = OFB_k1 xor OFB_k2 is the same for the DES2Bytes pair and
    for FLAG.enc;
  * the declared known-plaintext pair therefore reveals S for 848 bytes;
  * the first OFB block is E_k(IV), so scanning the public weak-key candidate
    set for pairs with E_k1(IV) xor E_k2(IV) == S[0:8] identifies the keys,
    verified against the full 848-byte keystream;
  * regenerating S decrypts FLAG.enc; the flag is extracted by its shape.

Only public weak-key constants are embedded; no pinned-answer bytes appear in
this source.
"""

import binascii
import re
import sys

IP = [58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,
      57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7]
FP = [40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,
      36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25]
E = [32,1,2,3,4,5,4,5,6,7,8,9,8,9,10,11,12,13,12,13,14,15,16,17,16,17,18,19,20,21,
     20,21,22,23,24,25,24,25,26,27,28,29,28,29,30,31,32,1]
P = [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25]
PC1 = [57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36,
       63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,29,21,13,5,28,20,12,4]
PC2 = [14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,41,52,31,37,47,55,
       30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32]
SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]
SBOX = [
 [14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7,0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8,4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0,15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13],
 [15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10,3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5,0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15,13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9],
 [10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8,13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1,13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7,1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12],
 [7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15,13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9,10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4,3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14],
 [2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9,14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6,4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14,11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3],
 [12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11,10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8,9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6,4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13],
 [4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1,13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6,1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2,6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12],
 [13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7,1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2,7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8,2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11],
]

# Public weak / semi-weak / possibly-weak DES key classes (the task hint points
# at the public weak-key material; these constants are keys, never answers).
WEAK_KEYS = """
FEFEFEFEFEFEFEFE FFFFFFFFFFFFFFFF 1F1F1F1F0E0E0E0E E0E0E0E0F1F1F1F1
E1E1E1E1F0F0F0F0 0000000000000000 0101010101010101 1F1F1F1F1F1F1F1F
E0E0E0E0E0E0E0E0 01FE01FE01FE01FE FE01FE01FE01FE01 1FE01FE01FE01FE0
E01FE01FE01FE01F 01E001E001E001E0 E001E001E001E001 1FFE1FFE1FFE1FFE
FE1FFE1FFE1FFE1F 011F011F011F011F 1F011F011F011F01 E0FEE0FEE0FEE0FE
FEE0FEE0FEE0FEE0 1F1F01010E0E0101 E00101E0F10101F1 011F1F01010E0E01
FE1F01E0FE0E01F1 1F01011F0E01010E FE011FE0FE010EF1 01011F1F01010E0E
E01F1FE0F10E0EF1 FE0101FEFE0101FE E0E00101F1F10101 E01F01FEF10E01FE
FEFE0101FEFE0101 E0011FFEF1010EFE FEE01F01FEF10E01 FE1F1FFEFE0E0EFE
E0FE1F01F1FE0E01 FEE0011FFEF1010E 1FFE01E00EFE01F1 E0FE011FF1FE010E
01FE1FE001FE0EF1 E0E01F1FF1F10E0E 1FE001FE0EF101FE FEFE1F1FFEFE0E0E
01E01FFE01F10EFE FE1FE001FE0EF101 0101E0E00101F1F1 E01FFE01F10EFE01
1F1FE0E00E0EF1F1 FE01E01FFE01F10E 1F01FEE00E0EF1F1 E001FE1FF101FE0E
011FFEE0010EFEF1 1F01E0FE0E01F1FE 01E0E00101E1E101 011FE0FE010EF1FE
1FFEE0010EFEF001 0101FEFE0101FEFE 1FFEE0010EF1FE01 1F1FFEFE0E0EFEFE
01FEFE0101FEFE01 1FE0E0F10EF1F10E FEFEE0E0FEFEF1F1 01FEE01F01FEF10E
E0FEFEE0F1FEFEF1 01E0FE1F01F1FE0E FEE0E0FEFEF1F1FE 1FFEFE1F0EFEFE0E
E0E0FEFEF1F1FEFE F1F1F1F1E0E0E0E0 FE1FFE1FFE0EFE0E
""".split()

OFFSET = 9133337
FIELD = len(str(OFFSET)) + 1
IV = b"13371337"


def permute(value, table, nbits):
    out = 0
    for pos in table:
        out = (out << 1) | ((value >> (nbits - pos)) & 1)
    return out


def key_schedule(key):
    k = permute(int.from_bytes(key, "big"), PC1, 64)
    c, d = k >> 28, k & ((1 << 28) - 1)
    subs = []
    for shift in SHIFTS:
        c = ((c << shift) | (c >> (28 - shift))) & ((1 << 28) - 1)
        d = ((d << shift) | (d >> (28 - shift))) & ((1 << 28) - 1)
        subs.append(permute((c << 28) | d, PC2, 56))
    return subs


def des_block(block, subkeys):
    m = permute(int.from_bytes(block, "big"), IP, 64)
    left, right = m >> 32, m & 0xFFFFFFFF
    for subkey in subkeys:
        expanded = permute(right, E, 32) ^ subkey
        folded = 0
        for i in range(8):
            six = (expanded >> (42 - 6 * i)) & 0x3F
            row = ((six & 0x20) >> 4) | (six & 1)
            col = (six >> 1) & 0xF
            folded = (folded << 4) | SBOX[i][row * 16 + col]
        left, right = right, left ^ permute(folded, P, 32)
    return permute((right << 32) | left, FP, 64).to_bytes(8, "big")


def ofb_stream(key, length):
    subkeys = key_schedule(key)
    state = IV
    out = bytearray()
    while len(out) < length:
        state = des_block(state, subkeys)
        out += state
    return bytes(out[:length])


def decode_layer(text):
    out = bytearray()
    step = 2 * FIELD
    for i in range(0, len(text), step):
        chunk = text[i:i + step]
        if len(chunk) < step:
            continue
        digits = ""
        for field in (chunk[:FIELD], chunk[FIELD:]):
            value = int(field) - OFFSET
            digits += str(value) if value < 10 else "ABCDEF"[value - 11]
        out += binascii.unhexlify(digits)
    return bytes(out)


def main():
    known = open("DES2Bytes.txt", "rb").read()
    padded = known + b"_" * ((8 - len(known) % 8) % 8)
    known_cipher = binascii.unhexlify(decode_layer(open("DES2Bytes.enc").read().strip()))
    flag_cipher = binascii.unhexlify(decode_layer(open("FLAG.enc").read().strip()))
    keystream = bytes(a ^ b for a, b in zip(known_cipher, padded))

    first = {}
    for hexkey in set(WEAK_KEYS):
        key = bytes.fromhex(hexkey)
        first[key] = des_block(IV, key_schedule(key))

    pair = None
    keys = list(first)
    for i, k1 in enumerate(keys):
        for k2 in keys[i:]:
            if bytes(a ^ b for a, b in zip(first[k1], first[k2])) == keystream[:8]:
                pair = (k1, k2)
                break
        if pair:
            break
    if not pair:
        sys.exit(1)

    stream = bytes(a ^ b for a, b in zip(ofb_stream(pair[0], len(keystream)),
                                        ofb_stream(pair[1], len(keystream))))
    if stream != keystream:
        sys.exit(1)

    full_stream = bytes(a ^ b for a, b in zip(ofb_stream(pair[0], len(flag_cipher)),
                                             ofb_stream(pair[1], len(flag_cipher))))
    plain = bytes(a ^ b for a, b in zip(flag_cipher, full_stream))
    match = re.search(rb"flag\{[ -~]*?\}", plain)
    if not match:
        sys.exit(1)
    print(match.group(0).decode())


if __name__ == "__main__":
    main()
