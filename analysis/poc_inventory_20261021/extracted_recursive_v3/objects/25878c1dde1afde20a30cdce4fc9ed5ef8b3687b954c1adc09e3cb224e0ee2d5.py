import json
import sys

c1_hex = '01b8f12555da2536bc8695e85303b1706ad7898e2f27dffa620466cc0a1650288f83c5aee2204b5a2a513a817bf23f8a4a051a5831194e49f15dca4d6ad1a5cc'
c2_hex = '42f389804e823f6914a7c6a96f2aadbdf874ef0c00575212cd3698ad1f4531fb5e4bb995bd7bda22242ea042b49e815e2dbdc8894155208f177d91e23e0ef5f9'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Since c2 = keystream (plaintext was all zeros)
# P1 = c1 XOR keystream = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {'plaintext2_hex': p1.hex()}
sys.stdout.write('CLAIM:' + json.dumps(claim) + '\n')
sys.stdout.flush()