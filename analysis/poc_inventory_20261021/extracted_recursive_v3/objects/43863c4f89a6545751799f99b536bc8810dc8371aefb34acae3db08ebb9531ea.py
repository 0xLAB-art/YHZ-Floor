import sys
import json

with open(sys.argv[1]) as f:
    instance = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "Nonce reuse detection requires known plaintext, key material, or distinguishing oracle; ciphertexts alone are insufficient"
}))
