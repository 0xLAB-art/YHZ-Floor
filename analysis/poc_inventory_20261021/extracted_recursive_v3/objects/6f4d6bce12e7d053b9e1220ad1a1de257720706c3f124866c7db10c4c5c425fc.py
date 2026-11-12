import json

c1_hex = 'caa9fa01c342f1348d1c18bd7ad9ad498c554e23bd5d6615122cdff2b651960fc7f2f97e2119f2e69ab459b2597e141530f2b5bedbff2528db514ba23b9624f1'
c2_hex = 'a78d18457695e09190b9e22c5bc50433dff2b14b0cb480d1cc419f2692981f25f5d682604de464e33a521a4e8e298cd828bb6be1e8f7052ca41e9826d9bd5b6c'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1 = bytes(a ^ b for a, b in zip(c1, c2))
p1_hex = p1.hex()

claim = {'plaintext_hex': p1_hex}
print(f'CLAIM:{json.dumps(claim)}')