import sys
   c1_hex = '45f3f611...'
   c2_hex = 'b040918e...'
   c1 = bytes.fromhex(c1_hex)
   c2 = bytes.fromhex(c2_hex)
   p1 = bytes(a ^ b for a, b in zip(c1, c2))
   plaintext2_hex = p1.hex()
   print('CLAIM:{\"plaintext2_hex\": \"' + plaintext2_hex + '\"}')
   sys.stdout.flush()