import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)

print(json.dumps({
    "status": "UNDERDETERMINED",
    "reason": "Nonce reuse detection requires plaintext, key, nonce, or keystream distinguisher"
}))
