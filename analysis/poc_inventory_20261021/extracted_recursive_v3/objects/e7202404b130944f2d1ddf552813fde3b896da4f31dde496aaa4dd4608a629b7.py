import json
c1 = bytes.fromhex("be61e9410044ff78291ebb6eace021ae0e6354496bc5277d9ba801283eae21b323b7877e2eb45740b70c98086e12e1b1c5ae30d6d5db2c985c22d84c4eb10729")
c2 = bytes.fromhex("5321f634ed9df577cd018ebfe6f42db83a8756b42db4a5a6a14b70461d3576411d2f434882dd5fb6e0daa4991a0369276875ef7ffc4540006f2174b12e2c5d18")
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print("CLAIM:" + json.dumps({"plaintext2_hex": p1.hex()}))