import time
c1 = bytes.fromhex("90309fbcee458ffa15d717c80d11badf55e37f8f8064458d114818d2525a0c73577542ef8e305a209855b821c0cf222aa60b8a9ac42e5c231dbb756cb5cb8f56")
c2 = bytes.fromhex("d96986545fc4645eadfe773cb406ec416b6e541986d220a47168417f4eb45c7351e78da986eb3296da898844cae00102f8591b303642f5fed26a23db34a7a9b1")
t0 = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
opspan = time.monotonic_ns() - t0
import json
print("OPSPAN_NS:" + str(opspan))
print("CLAIM:" + json.dumps({"plaintext2_hex": p1.hex()}))
flush = True