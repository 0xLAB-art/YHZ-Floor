import sys, json

c1_hex = '6e2b7cc38b3eafa1dc8d2923a24157bfab74a5d75f394a6147eb2f2fd3405e35136852bb2437bc887a0716054d184d641bbaa836b159ad785adf99db11b36bfa'
c2_hex = '41c274129b8b9784ff72bcd2ea36a3bbeab4364608c6a159fdc2a66bd5b43836112f3cea610e574faee5e37a37cebaa00c2a6e14aef85dc44c064557da930ecd'

b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)

p1 = bytes(x ^ y for x, y in zip(b1, b2))
plaintext_hex = p1.hex()

claim = json.dumps({"plaintext_hex": plaintext_hex})
print(f'CLAIM:{claim}')
sys.stdout.flush()