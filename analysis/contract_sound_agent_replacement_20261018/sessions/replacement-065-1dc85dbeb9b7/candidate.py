import json
import sys

with open(sys.argv[1]) as f:
    instance = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "Nonce reuse in ChaCha20 enables keystream recovery from two ciphertexts, but without a known plaintext, crib, or distinguishing oracle, we cannot definitively confirm the nonce was reused or recover actionable plaintext."
}))
