import json, time

c1_hex = "ffd91a8166846a1dd46bb8fc38204516f8ae2e80182b5cdbf7f2df4d0e7392ff26c39a43d3a1f94b6938faa0a6e58474bd22b8f88d51ea3fd13ef275585a313e"
c2_hex = "443f4509e2aadb2fbf5006f5b8acc57ddbcb16bd32ad8e509880b51755efa17816f6050af1b5cd9b81e1c8f7c2b9ff87876f9e83bc44ccc3ee302265b3802d79"

start = time.monotonic_ns()
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
end = time.monotonic_ns()
print("OPSPAN_NS:" + str(end-start), flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": p1.hex()}), flush=True)