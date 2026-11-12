import sys, json, time

c1_hex = 'e82e47de7b0991f88dee05bc1eb55639457454db3ccbd5ca5ed4eb559951ff4b959a200be4a596fea5f69b126efc7c71bcd50162a421bce2f4b80860f074f59b'
c2_hex = '002b07a49ba394e38dd122d83d508ad7c0c13cafcaf3ac5db44f603c433dcd347adc1529ac83edb9dba6965cd158e8231be3b39284d8e6670617ab5d9403dd14'

b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)

# keystream is c2 because plaintext is all zeros
ks = b2
p1 = bytes(a ^ b for a, b in zip(b1, ks))

p1_hex = p1.hex()
claim = json.dumps({"plaintext2_hex": p1_hex})
print(f'CLAIM:{claim}', flush=True)