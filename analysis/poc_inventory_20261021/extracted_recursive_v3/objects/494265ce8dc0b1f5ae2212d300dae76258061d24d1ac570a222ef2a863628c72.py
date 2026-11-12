import time
c1 = bytes.fromhex("c8638d5e4de2ce2b5e31f645a469e553dd529fd709397eeefeeee98be492e8955f4c6b947ec87e9bf709120e6a5d8f526f59689181f8e3141d5787076bb0ce6b")
c2 = bytes.fromhex("aed134254169d0e2e42651dc9bfcb6a861445e5c360ff71c8078e05dc8af5fe2f34202eb0bfc66e8d5bb21445ee213138cdb8b63685800e6ea814dbcb6dfb7d5")
assert len(c1) == 64 and len(c2) == 64
t0 = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print("P1 =", p1)
print("P1 hex =", p1.hex())
print("OPSPAN_NS:" + str(time.monotonic_ns() - t0))
print('CLAIM:{"plaintext_hex": "' + p1.hex() + '"}')