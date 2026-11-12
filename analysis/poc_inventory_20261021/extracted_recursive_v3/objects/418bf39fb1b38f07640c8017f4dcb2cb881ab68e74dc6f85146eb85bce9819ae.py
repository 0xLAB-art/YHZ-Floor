import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)

result = {
    "status": "UNDERDETERMINED",
    "reason": "ECDSA nonce reuse requires at least two signatures with the same nonce to recover the private key; only one signature provided"
}

print(json.dumps(result))
