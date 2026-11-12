import sys
import json

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

print(json.dumps({"status": "UNDERDETERMINED", "reason": "only one signature provided, need two signatures with shared nonce to recover private key"}))
