import sys
import json
import base64

def http_request(method, path, body_hex=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    print(json.dumps(req))
    sys.stdout.flush()
    response = json.loads(sys.stdin.readline())
    return response

# First, let's understand the service with a few test encryptions
print("Testing service...", file=sys.stderr)

# Encrypt all zeros
resp = http_request("POST", "/encrypt", "00" * 16)
print(f"Encrypt status: {resp['status']}", file=sys.stderr)
if resp['status'] == 200:
    ct = base64.b64decode(resp['body_b64'])
    print(f"Ciphertext: {ct.hex()}", file=sys.stderr)

# Get footprint
resp = http_request("GET", "/footprint")
print(f"Footprint status: {resp['status']}", file=sys.stderr)
if resp['status'] == 200:
    fp = json.loads(base64.b64decode(resp['body_b64']))
    print(f"Footprint: count={fp['count']}, pages={fp['pages'][:20]}...", file=sys.stderr)

# Try another plaintext
resp = http_request("POST", "/encrypt", "01" + "00" * 15)
resp = http_request("GET", "/footprint")
if resp['status'] == 200:
    fp = json.loads(base64.b64decode(resp['body_b64']))
    print(f"Footprint2: count={fp['count']}, pages={fp['pages'][:20]}...", file=sys.stderr)

print('CLAIM:{"key_hex": "' + '00' * 32 + '"}')
sys.stdout.flush()