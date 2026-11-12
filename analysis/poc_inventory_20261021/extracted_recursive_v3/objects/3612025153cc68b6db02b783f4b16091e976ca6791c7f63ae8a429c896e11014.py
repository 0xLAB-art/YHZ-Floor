import sys
import json

with open(sys.argv[1]) as f:
    instance = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "ChaCha20 nonce reuse detection requires plaintext, key, or distinguishing oracle; ciphertexts alone are pseudorandom"
}))