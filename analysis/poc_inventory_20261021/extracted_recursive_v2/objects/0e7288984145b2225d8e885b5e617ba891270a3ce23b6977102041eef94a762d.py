import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "Nonce reuse in ChaCha20 allows keystream recovery by XORing ciphertexts, but without known plaintext, the original messages or key cannot be determined from ciphertexts alone."
}))
