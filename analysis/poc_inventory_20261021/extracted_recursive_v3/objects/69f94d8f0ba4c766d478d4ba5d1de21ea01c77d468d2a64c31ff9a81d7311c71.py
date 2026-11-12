import sys
c1_hex = "df3f90c9aae8085af5bb4cc68fa40e7819f37647493da79676e899a655260d6d9e01a701591299715dd62f2fd35b536058016e2cd8df9e8a2a8993b1c0fab70f"
c2_hex = "f3a5f23c45e1b6a46faf002a631d439c4e1a9a0932446052a45183e4d9ab8020a5f6f550f624cb1e0b6fa25b4a3ae8eaef900f6e6cd9bdfd615a2615759bb8fa"
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print("CLAIM:{\"plaintext2_hex\": \"" + p1.hex() + "\"}")