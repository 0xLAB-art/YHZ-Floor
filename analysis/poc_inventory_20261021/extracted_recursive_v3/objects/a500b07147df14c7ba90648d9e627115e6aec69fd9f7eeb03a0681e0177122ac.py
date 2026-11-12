import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "Nonce reuse detection requires known or chosen plaintext, a decryption oracle, or distinguishing access; ciphertexts alone are indistinguishable from random without the key or additional side-channel information."
}))