import json, sys

c1_hex = "65c54027baf5d276cf53b2450f74741e17cd6caf10c641818c9c89ec6328a55131c97d6d074f543fb07e5aa5cb0400445f7c82c6ab56af21c0b681323db51187"
c2_hex = "8bc9e3fb4ec009752f30fcbd1ca0a18007d0e32be770b037a739c758e255be8354210cb5cec57ca27195f56419af628004e0d70921329d083aa30cb74480a182"

# convert hex to bytes
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# XOR
p1 = bytes(a ^ b for a, b in zip(c1, c2))

plaintext2_hex = p1.hex()

# output OPSPAN_NS optionally
# we can measure time, but not necessary; we can just output claim.

# last line: CLAIM:...
claim_line = f"CLAIM:{{'plaintext2_hex': '{plaintext2_hex}'}}"  # but JSON requires double quotes. We'll format properly.

# Actually we need to output CLAIM: followed by JSON with double quotes. So:
claim_json = json.dumps({"plaintext2_hex": plaintext2_hex})
print(f"CLAIM:{claim_json}")
sys.stdout.flush()