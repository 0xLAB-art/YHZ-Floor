import sys
import json

c1_hex = "cedf31f1a02250a158aba2303f92d6e5f72177ef88ea0887c5ac7f41686c61d69eb4216711246d5af8852027a8a7e2bbbd0be2a05bbc6a494dc720617d4492d5"
c2_hex = "7ad1dafdf1ad8ef3584467ee9fe7fafe39877a5ac67f1a75c6dd610121777d7324b543710d8f2c00187857514912e59640f83467aeb36f02aee430ed6e0ecc17"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# c2 is the keystream (since it encrypts all zeros)
# P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

print(f'CLAIM:{{"plaintext_hex": "{p1.hex()}"}}')