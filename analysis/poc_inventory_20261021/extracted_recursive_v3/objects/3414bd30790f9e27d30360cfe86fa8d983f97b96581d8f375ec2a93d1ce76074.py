import time
c1 = bytes.fromhex("024857e424a62fdd9faba853305a73acdd24a2f4cd7000b37700cbbfae90e04a19e32c4bd0ceb3b46899b9fcee1f375c01467cea298d5b59ac7fffb547408875")
c2 = bytes.fromhex("fb33e99af52c0255f94826fccda0616233dc239346fa889002b2b2e27751fb5a7945a3a1c62e8aae94796fc7690b8e41410a16a4f5d1bc84980b666f7e3248bc")
t0 = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
opspan = time.monotonic_ns() - t0
print(f"OPSPAN_NS:{opspan}", flush=True)
print("CLAIM:" + __import__('json').dumps({"plaintext2_hex": p1.hex()}), flush=True)