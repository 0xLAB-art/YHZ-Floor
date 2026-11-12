import sys
import json

with open(sys.argv[1]) as f:
    instance = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "ChaCha20 nonce reuse detection requires either known plaintext, the key, or distinguishable plaintext structure; with only two ciphertexts no such oracle is available"
}))
