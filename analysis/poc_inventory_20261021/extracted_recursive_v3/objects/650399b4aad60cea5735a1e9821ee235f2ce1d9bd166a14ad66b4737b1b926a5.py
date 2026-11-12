import json, time

c1_hex = '29440b99c3f60314cb22d51d62f5c08d9994c968944dfae8a70768ebbfa42a5f22ed8e5fed0e7edd8e19e2202236f3342fe87c6965a93b35954ff3b6448bea07'
c2_hex = 'efb9279492edf43c7b4fb5e543999e7114ee878e550ff57c90c9393644e0dcdc0e1cd9afce40d4224405a5439fd30bbf0aea43336a487abad5fbed20eea48328'

start = time.monotonic_ns()
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()

claim_json = json.dumps(dict(plaintext_hex=plaintext_hex))
print('CLAIM:' + claim_json)