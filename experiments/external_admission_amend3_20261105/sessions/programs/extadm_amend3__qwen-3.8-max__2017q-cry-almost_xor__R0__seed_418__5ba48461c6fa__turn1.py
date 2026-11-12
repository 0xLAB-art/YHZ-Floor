import json

with open('ciphertext') as f:
    ct = f.read().strip().replace('\n', '')

with open('almostxor.py') as f:
    src = f.read()

ns = [1, 2, 3, 4, 5, 6, 7]
for n in ns:
    try:
        exec(src, g := {})
        encr = g['encrypt']
        for key_len in range(1, 13):
            for k in range(256 ** key_len):
                key = ''.join(chr((k >> (8 * i)) & 0xff) for i in range(key_len))
                try:
                    c = encr(key, ct, n)
                    if c == ct:
                        print('FOUND', n, repr(key))
                except Exception:
                    pass
    except Exception:
        pass
