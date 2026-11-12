import json, sys

c1_hex = '1d893f12e519ed33d5d5ecf418245792f324ccf443d09bef6b1a3d9b79a282bd6723b711359de47af2ad86928949d97920a8975966ac051b360b581dc0c809bf'
c2_hex = '120060ea46022da42ae32301c9d39b515fde56dcd41204b09640d8a9ddf5ec80f8622d942d9da8d4463007b5390677e0f2bdd261c77a1fc15a91a0db3b6d6d35'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Same key+nonce => same keystream. c2 = keystream (since plaintext is all zeros).
# c1 = P1 XOR keystream => P1 = c1 XOR c2
P1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext2_hex = P1.hex()

claim = json.dumps({"plaintext2_hex": plaintext2_hex})
print("CLAIM:" + claim)
sys.stdout.flush()