import json
import sys

inst = json.loads(sys.stdin.read())
print(json.dumps({'status': 'UNDERDETERMINED', 'reason': 'a single signature does not determine the nonce', 'public_key_present': 'public_key' in inst}))
