import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "ChaCha20 nonce reuse detection requires known or guessable plaintext, a decryption oracle, or the secret key; given only two ciphertexts, the XOR reveals the plaintext XOR but not whether the nonce was reused"
}))