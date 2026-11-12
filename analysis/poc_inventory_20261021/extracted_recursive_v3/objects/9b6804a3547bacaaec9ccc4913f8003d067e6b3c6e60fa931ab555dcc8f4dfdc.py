import sys, time
c1_hex = 'c72fd784795ad5b2f6f7ba92e15887eb3ecfed0f27dfa4d4d3b976da0fab47fcef60f047c789eb42d5cac2f0517b15b39518324ac167dcafe0c4e6b2a05ba50e'
c2_hex = '5f2398c6b89868055d15cfcfd8eb5810d1ee30265fd250bdb34a4ff889760401af83ee2f07c320b495f46fdee18fccd127330b818039e06bd7350d94a570af8b'
b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)
start = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(b1, b2))
elapsed = time.monotonic_ns() - start
print(f'OPSPAN_NS:{elapsed}')
sys.stdout.flush()
claim_json = '{"plaintext_hex":"' + p1.hex() + '"}'
print(f'CLAIM:{claim_json}')
sys.stdout.flush()