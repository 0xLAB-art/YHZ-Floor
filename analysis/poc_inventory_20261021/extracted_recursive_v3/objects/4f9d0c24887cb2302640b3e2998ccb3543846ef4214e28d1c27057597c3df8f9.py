import sys, json

c1_hex = "d75e40cc10aaef78206f146dc4f5b1b3f660754801d8aaebdfcd3b42f8ddd1ae227936f79184c607b8b2ffed64e997da14e0f92535f5f0d2a981b141f31c1bf9"
c2_hex = "1746b38c1cbb540541f2db1ce03614a6fd1de7e9dbb0b9d02dc2de3b930d8e68634e16408bed057e49d1bae097f7e6520abb207562247da0c66ab0c120e6509b"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1 = bytes(a ^ b for a, b in zip(c1, c2))
p1_hex = p1.hex()

claim = {"plaintext_hex": p1_hex}
print("CLAIM:" + json.dumps(claim))
sys.stdout.flush()