import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "ECDSA nonce reuse requires at least two signatures; only one signature provided"
}))
