import json, sys

c1_hex = 'f83d581c95df2282f9d552d545cb04b32e972baea1769651f16b5582d0cae27b86ffdf5104b520e34fa6ca723443717bf00b5fd2cc39ec286e302ca9842bedbf'
c2_hex = '5aa41dfce6266d8990e2ef7a0e935d8014aa95babda14fa37182234a7d8695d358d21b95087515cd69b957e98998e1d6b821179ff26cc29fa8d43b35b221ef2c'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()

claim = json.dumps({"plaintext_hex": plaintext_hex})
print(f'CLAIM:{claim}')
sys.stdout.flush()