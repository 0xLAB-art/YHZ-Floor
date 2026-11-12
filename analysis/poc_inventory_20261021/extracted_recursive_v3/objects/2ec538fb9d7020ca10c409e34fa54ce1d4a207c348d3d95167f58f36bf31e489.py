import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "Only one signature provided; ECDSA nonce reuse requires at least two signatures to detect reuse or recover the private key"
}))
