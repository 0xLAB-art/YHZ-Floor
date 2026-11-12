import json, time

c1_hex = "d65cec526f6c7e78e18002bb86bbc29cac8a66381eef78add2d97bd12ec28fdfed7e6e385066398ba24fe09c1de109afdf48164a03cd8f31ad084a34777550a5"
c2_hex = "731705ca016aab16d15ae391fe481eb38e8cc9a4e6b9cf1a743e81d24b68db1dbe2de7e1dc380ae2934019682992c955efd5eb0e00ee637196bab131b4df3dfb"

# convert to bytes
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# XOR
p1 = bytes(a ^ b for a, b in zip(c1, c2))

plaintext2_hex = p1.hex()

# measure time
start = time.monotonic_ns()
# just do the xor again maybe
p1_check = bytes(a ^ b for a, b in zip(c1, c2))
end = time.monotonic_ns()
ops = end - start

print(f"OPSPAN_NS:{ops}")
# flush
import sys
sys.stdout.flush()

claim = json.dumps({"plaintext2_hex": plaintext2_hex})
print(f"CLAIM:{claim}")
sys.stdout.flush()