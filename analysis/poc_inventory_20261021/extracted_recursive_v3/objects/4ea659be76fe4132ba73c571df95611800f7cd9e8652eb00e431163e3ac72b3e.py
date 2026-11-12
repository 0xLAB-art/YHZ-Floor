import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "Single signature provided; nonce reuse requires at least two signatures to detect duplicate k values"
}))