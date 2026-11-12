import json

c1_hex = "ea4aedfa34be8461302727b6962b8d590ca7bf721d684ac62d6bba11f55e5b25ffdb54507944d7fd6e1ef404a8e09b7df71a4a37a0b0025e7f19b3c0737868e2"
c2_hex = "e455f9622e6ba533ce153adbfe0e239b58f131be705e7a17310e6153969705d14a74d8e7c962af291302ded4d8fd17da663ccac29b2cbc214cc287525d637320"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Same key+nonce => same keystream. c2 = keystream XOR 0 = keystream.
# Therefore P1 = c1 XOR c2.
p1 = bytes(a ^ b for a, b in zip(c1, c2))

print("CLAIM:" + json.dumps({"plaintext2_hex": p1.hex()}))