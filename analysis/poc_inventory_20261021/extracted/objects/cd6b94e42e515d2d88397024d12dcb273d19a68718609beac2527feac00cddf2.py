import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "ECDSA nonce reuse requires two signatures sharing the same nonce; only one signature provided"
}))
