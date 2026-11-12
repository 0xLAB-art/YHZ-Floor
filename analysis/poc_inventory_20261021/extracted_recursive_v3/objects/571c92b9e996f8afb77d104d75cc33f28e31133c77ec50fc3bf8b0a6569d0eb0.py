from Crypto.Cipher import ChaCha20
c1 = bytes.fromhex("2ecb2a39c489a412868e645643b21cbb7b2b5402f34e499d09a97a5d15c2c33d6ce9f752fa3835ed4aa200e54c9f28c7cbc54807be516b73db3c718f3e040dcd")
c2 = bytes.fromhex("a1fd50eea5fcf1f38a8f71dce93fee8e1cf09dbc6872fe42aa730ecc0380a3699929051488a256701571442aa5dacb924658cb8b18a6c7c8d5fb54cb6f9664a2")
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print("CLAIM:" + '{"plaintext2_hex": "' + p1.hex() + '"}')