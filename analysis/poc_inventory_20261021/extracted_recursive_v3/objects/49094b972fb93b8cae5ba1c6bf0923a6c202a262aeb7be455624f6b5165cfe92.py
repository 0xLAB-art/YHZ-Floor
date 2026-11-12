import sys, json

c1_hex = '3215b30c03b6ba3034980012d2f66224cff7a83c671ae4acb1c58febf8f7aa8175082624ea7d0a5676d97ca4dc7e172d7faed34568bd58977a64320840db75cf'
c2_hex = '27ffb6cc305e5c96290ca0b761ba0a4fd9e2081ee988f308937217b4082e3c409d81b3d4881e54a439444ceda989cbf64a703c3fb0bcfdcbd03c679b394b9ce6'

def xor_hex(a, b):
    ba = bytes.fromhex(a)
    bb = bytes.fromhex(b)
    return bytes(x ^ y for x, y in zip(ba, bb)).hex()

p1_hex = xor_hex(c1_hex, c2_hex)
claim = {'plaintext_hex': p1_hex}
print('CLAIM:' + json.dumps(claim))
sys.stdout.flush()