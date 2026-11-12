c1_hex = '3bccdac58b4484551ec6e85371dd192cc448798916ff148c6615f21c9cf33575effa9895103f93c9654c957c15a33bb67d2d38cfcc243e1fcb29ef7d64d2bd2'
c2_hex = '5c3f294e823421e8e656781786b59db6d9928e2716aaed5497828ce65f3279f1c36dc4091f5250c59a47a68a5da498eb917da41cb5ee6b56f4b4cc744ef8d4'
print(f'c1 len: {len(c1_hex)}, c2 len: {len(c2_hex)}')
# Try all possibilities for missing hex digits
import string
readable = set(string.printable.encode())
for i in range(16):  # missing nibble for c1
    c1_try = c1_hex + format(i, 'x')
    c1 = bytes.fromhex(c1_try)
    for j in range(256):  # missing byte for c2
        c2_try = c2_hex + format(j, '02x')
        try:
            c2 = bytes.fromhex(c2_try)
            p1 = bytes(a ^ b for a, b in zip(c1, c2))
            if all(32 <= b < 127 or b in (10, 13, 9) for b in p1):
                print(f'Found: i={i}, j={j}')
                print(f'P1: {p1}')
                print(f'P1 hex: {p1.hex()}')
        except:
            pass