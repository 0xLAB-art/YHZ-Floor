import time

t0 = time.monotonic_ns()
c1 = bytes.fromhex("137074a67e18d60e8f3bec417c93306f328591f06551ad317c0a4d88cdb606383a2e6ca41173a7bdf473d56db3454531ec51a255a0e9102da60118c174f94425")
c2 = bytes.fromhex("40d772a09e75157668e357c2ca051a8bb8f1be6e83a77024dc3fa3428c8f32bd8921873ec33b5ee583f342005957917b1fdd7d75e0aa514021d079be510c9da0")
assert len(c1) == len(c2) == 64
p1 = bytes(a ^ b for a, b in zip(c1, c2))
op = time.monotonic_ns() - t0
print(f"OPSPAN_NS:{op}", flush=True)
print("CLAIM:" + __import__('json').dumps({"plaintext_hex": p1.hex()}), flush=True)