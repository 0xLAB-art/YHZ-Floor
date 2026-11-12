import time

c1 = bytes.fromhex('6893e3257d09bf441bf6b58ff466a01887cf8b9157d96cac8ca2003689d38afa6378302dd637325207c3cabf726a3c74a78726d7a98c1cbeb996207091654860')
c2 = bytes.fromhex('ad9e9f09615762e2d00c95b1997368c95e9dd540fec59a91bbdbf7ddf0e11a33f98886934b3c17f09ee13bcac9d6fb736461d6886a7a7fef818120c98bd40503')

t0 = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
t1 = time.monotonic_ns()

print('CLAIM:' + '{"plaintext2_hex": "' + p1.hex() + '"}')
print('OPPSPAN_NS:' + str(t1 - t0))