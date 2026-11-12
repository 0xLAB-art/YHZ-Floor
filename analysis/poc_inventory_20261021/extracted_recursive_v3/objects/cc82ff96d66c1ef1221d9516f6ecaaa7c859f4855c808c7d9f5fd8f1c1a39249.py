from Crypto.Util.number import *
import time
c1 = bytes.fromhex("92bc62866b14551af966c6a362bf1b14b89c674a32bbd6314756dd218dcbe955cb86e2729af6751bc982ec318c0b996ce93662a685987dcf8164941459987150")
c2 = bytes.fromhex("eea1a8f62fbfda992a2b3293a25e88611feabc4d1e00308be81925003edf5c17cb3d95d84c8e4adecbea3bd32f6d3a7aa663f0f7b242161dedcc5d8054608642")
t0 = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
opspan = time.monotonic_ns() - t0
print(f"OPSPAN_NS:{opspan}", flush=True)
print("CLAIM:" + __import__('json').dumps({"plaintext_hex": p1.hex()}), flush=True)