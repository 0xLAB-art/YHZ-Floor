import sys, json

c1_hex = '0a3ba82e47462caf74517b579bd00fca23b1f72fecadfeb48e2a777e31264fd950a5128383af90ff4fb33dddc94ab8b2fad891c802f2c20dbffdea6ca1f9b8d1'
c2_hex = 'bc1b43f45f599d0661a068571a7fbaafc339a877275904c502f0f9299f17db259251320b031d761fd375b4723dea129540d5111bd4d41c221164f1b3947b0fb1'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()

claim = {'plaintext_hex': plaintext_hex}
print('CLAIM:' + json.dumps(claim))