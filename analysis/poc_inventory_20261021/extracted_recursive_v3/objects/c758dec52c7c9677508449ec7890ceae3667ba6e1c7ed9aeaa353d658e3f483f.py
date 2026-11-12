import json, sys, time

c1_hex = 'a62ba21fbe21904188f64139f680633386e56ce8914a9cd1c0af62cc0c00b2a1c14a49b375b9f12ac6ece3e2c33197fc80fbc7dfec713e7bd9ff92befa0f1df7'
c2_hex = '7eb1c4df6faf9b5366bb0c665347c80c0f0fbc30501d497e03bb729bd6ec4b185056f598753ab15f8f1381dcffc165f19344a81d6e4133cf6cb9bff24264ab02'

b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)
p1 = bytes(x ^ y for x, y in zip(b1, b2))
plaintext_hex = p1.hex()

# optional timing measurement
start = time.monotonic_ns
# (no heavy operation needed; just measure immediate)
end = time.monotonic_ns
ops_span = end - start

claim_obj = {"plaintext_hex": plaintext_hex}
print(f"CLAIM:{json.dumps(claim_obj)}")
sys.stdout.flush()