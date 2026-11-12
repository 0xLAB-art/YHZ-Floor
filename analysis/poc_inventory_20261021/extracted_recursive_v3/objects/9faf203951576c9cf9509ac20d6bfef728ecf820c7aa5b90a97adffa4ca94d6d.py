import sys

c1_hex = 'fe5b436abd24ffbec5118d8f31007dd4b443dc4322aec1567d409cae67a66bef156e3220fba2615b94cd1be69345823df819ee50514c7e6bebe33445b83d449e'
c2_hex = '03c5c71126809b3ab172ebf20dfcea05537d4085bca7979b81578a17b4ce23857df6ba8892d749dd82c982ac53a8deec21e20f8eec7cd9beb4f70be07125162a'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# keystream = c2 (since second plaintext is all zeros), so P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))
p1_hex = p1.hex()

claim = f'CLAIM:{{"plaintext2_hex": "{p1_hex}"}}'
print(claim)
sys.stdout.flush()