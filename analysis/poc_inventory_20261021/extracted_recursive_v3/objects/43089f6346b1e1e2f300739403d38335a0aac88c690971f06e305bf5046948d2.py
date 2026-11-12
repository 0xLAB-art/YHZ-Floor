import json, time

c1_hex = 'fff41bc28b358300895274c4dbd529f054d378c1092ca4d131f9f74d34964add85cc78a8e3155193d872917c6c1092244c9daaa467f18c3fe3e2456378fbf5f1'
c2_hex = '1849c10989cf53ad1bb18d65aea831b940b7d52de329c898fcf4614b7df55a66fc2a93dfa754e5f52c94dd3b6c6018d32491126153e957664fd634221951df15'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

pt = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = pt.hex()

t0 = time.monotonic_ns()
_ = pt.hex()
t1 = time.monotonic_ns()
opsan = t1 - t0

print(f'OPSPAN_NS:{opsan}', flush=True)
print(f'CLAIM:{{\"plaintext_hex\": \"{plaintext_hex}\"}}', flush=True)