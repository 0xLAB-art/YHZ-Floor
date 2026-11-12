import json  # maybe not needed
c1_hex = "059785a3a30e6203334024b01fc6fc96c1bc33e8210f83deaee0ab87e362b4166ec35f5cb16b646a2eef3fc90b61f9a0dfc27ac8fb560db9087cf3353db22d79"
c2_hex = "7e34d4a8685e98ff4c88519f5f019bd0a0a3b5c75e4de12bbe940fd4120fafdebf5e996dd660b38ef53ed3df81aa6ca1d6233c9ea333c91d9d8d421b0b54f746"
b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)
p1 = bytes(x ^ y for x, y in zip(b1, b2))
print("CLAIM:{\"plaintext_hex\":\"" + p1.hex() + "\"}")