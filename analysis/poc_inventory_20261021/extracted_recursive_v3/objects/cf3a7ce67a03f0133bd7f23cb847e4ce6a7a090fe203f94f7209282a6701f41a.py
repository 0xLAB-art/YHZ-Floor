import sys

c1_hex = '456159180f358f61f455b517945a0d655d6b1bc87cc36e173438349f09eb01473ac24e3c74f9d4c48d181cb2a2a94e86bfa76c2388b7aac3c314043b90d937be'
c2_hex = '6235285bed6b0748a886b3f41513af6bae63d3e0c293be71d9cc13e7d78559ce36b88a6ffe7ca192ac4a448971063f69b718f77cbe3da8d524dd4e59b60cd860'

b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)
p1 = bytes(x ^ y for x, y in zip(b1, b2))
plaintext2_hex = p1.hex()

claim = 'CLAIM:{"plaintext2_hex": "' + plaintext2_hex + '"}'
sys.stdout.write(claim + '\n')
sys.stdout.flush()