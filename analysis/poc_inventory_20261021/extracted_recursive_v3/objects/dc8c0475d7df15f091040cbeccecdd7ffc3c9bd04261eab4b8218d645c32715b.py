import sys
import json
import base64

def http_request(method, path, body_hex=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    if headers is not None:
        req["http"]["headers"] = headers
    print(json.dumps(req), flush=True)
    response = json.loads(sys.stdin.readline())
    return response

# First, let's test the service with a simple encryption
plaintext = bytes([0] * 16)
resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
print(f"Encrypt response: {resp}", file=sys.stderr)

# Get footprint
resp = http_request("GET", "/footprint")
print(f"Footprint response: {resp}", file=sys.stderr)

# Parse the footprint
if resp["status"] == 200:
    body = base64.b64decode(resp["body_b64"])
    footprint = json.loads(body)
    print(f"Footprint: {footprint}", file=sys.stderr)

# Now let's understand the structure better - try a few different plaintexts
for i in range(3):
    pt = bytes([i] * 16)
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    resp = http_request("GET", "/footprint")
    if resp["status"] == 200:
        body = base64.b64decode(resp["body_b64"])
        footprint = json.loads(body)
        print(f"Plaintext {i}: pages={footprint['pages']}, count={footprint['count']}", file=sys.stderr)