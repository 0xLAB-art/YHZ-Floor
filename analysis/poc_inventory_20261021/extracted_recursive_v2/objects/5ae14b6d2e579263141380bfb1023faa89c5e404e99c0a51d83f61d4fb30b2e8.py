import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "Only one signature provided; nonce reuse requires at least two signatures to compare nonces and potentially recover the private key"
}))
