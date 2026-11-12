import sys, json, binascii, time

def xor_hex(a, b):
    ba = binascii.unhexlify(a)
    bb = binascii.unhexlify(b)
    return binascii.hexlify(bytes(x ^ y for x, y in zip(ba, bb))).decode()

c1_hex = "6e6de7efcdfb49c755a28764ab55682f8bbd7f55699334176d0f2ed9e49f74f91fdba986f28d15507d51e7d144ca1186f144bb2d777a9c1d9278e7fd437e2923"
c2_hex = "06b22030205f2a387837c2eb29647c23034c3c7538b1e3fc552c453324787a3a01fccea9495f4f8b0b36581f7e2e66fc0aa9a1d75fe837cbca0158da33b50156"

plaintext_hex = xor_hex(c1_hex, c2_hex)

# Prepare claim
claim = {"plaintext2_hex": plaintext_hex}

# Output claim according to protocol
print(f"CLAIM:{json.dumps(claim)}")
# Optional timing (not required)
# opspan = time.monotonic_ns()
# print(f"OPSPAN_NS:{opspan}")
sys.stdout.flush()