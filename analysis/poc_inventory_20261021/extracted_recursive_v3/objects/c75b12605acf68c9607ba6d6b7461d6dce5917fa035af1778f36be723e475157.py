import time
t0 = time.monotonic_ns()
c1 = bytes.fromhex("02758363e36bd4d0511f44aa9e9a9eaea598b27774a5afaa17c0c8a0812c2e7d649b297a1140de12dd257fc3ad6ac2f871684c3dac0c8b339b4d8677875eb48e")
c2 = bytes.fromhex("6e2995d2b947558928912b8be1facbf12faa00814c1bc150dc303487f6542112488537897b475f0deca052444ec228e43983ce4a2d17f9392629b1f8170acf65")
assert len(c1) == len(c2) == 64
p1 = bytes(a ^ b for a, b in zip(c1, c2))
t1 = time.monotonic_ns()
print(f"OPSPAN_NS:{t1 - t0}")
print("CLAIM:" + __import__('json').dumps({"plaintext_hex": p1.hex()}))