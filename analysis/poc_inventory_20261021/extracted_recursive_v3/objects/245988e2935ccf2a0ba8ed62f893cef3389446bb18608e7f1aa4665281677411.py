import json
c1 = bytes.fromhex('92e106d64584487bdbbd52c9231bc7489c08d5d4492d22a4c39847cc6dee58ddaa30b189b63a13b9da0fe976acb3de32b8a14b081d979280c8041a1ecc6a7c87')
c2 = bytes.fromhex('8ea583008a6b287026b439e57526e9eb077a539f393d86a98d6bdf7b7231968f270a826f2b3c294720f6c925c8f166324fb7fd7a4b4137977de4d530e63a1f60')
t0 = __import__('time').monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
t1 = __import__('time').monotonic_ns()
print('OPSPAN_NS:%d' % (t1 - t0), flush=True)
print('CLAIM:' + json.dumps({'plaintext_hex': p1.hex()}), flush=True)