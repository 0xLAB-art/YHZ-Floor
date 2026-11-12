c1_hex = "cf1b787bc5ee3df5f06a4312bdd7b99e7f600d9ad8d7b9867be3da34f5165804f2c04d63ba6fcbc3aa98ade97751baf87524cd6a61482e54873679151b224f73"
c2_hex = "b012604a72d99e6f22a7cedd4693cd15bdac4226c4a94d86aef654e937fe822876fdd5a2b07f5103681ce9c9e433577eb5be86d575ca598aa2d53187db98cb30"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# RC4 keystream reuse: c1 = P1 XOR keystream, c2 = keystream (since plaintext is all zeros)
# Therefore P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

import json
result = {"plaintext_hex": p1.hex()}
print(json.dumps(result))
print(f"CLAIM:{json.dumps(result)}")