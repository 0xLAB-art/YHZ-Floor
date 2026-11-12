import json, sys, time

c1_hex = 'c0348d138617d93f1bb86025152f4867fd6c5b8c601d4116db71707f62f818a12b4a239e13448cfdea1aada08111c0daf929ac41534f6ad2dd6c4558e3d99afd'
c2_hex = '268f2d2d12cc01b56482f33e22e15960a4d9b3ae5efea40ca16c97f4ccd32524ba859607708138e682d6a5089415c5788f276030bf55c1d191b89ad3e3643e40'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()

start = time.monotonic_ns()
_ = bytes(a ^ b for a, b in zip(c1, c2))
elapsed = time.monotonic_ns() - start

print(f'OPSPAN_NS:{elapsed}')
sys.stdout.flush()

claim = {'plaintext_hex': plaintext_hex}
print(f'CLAIM:{json.dumps(claim)}')
sys.stdout.flush()