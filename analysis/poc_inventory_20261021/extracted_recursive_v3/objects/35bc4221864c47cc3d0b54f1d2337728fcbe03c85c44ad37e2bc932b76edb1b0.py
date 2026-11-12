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

# First, let's explore the service
print("Exploring service...", file=sys.stderr)

# Try GET /footprint first to see initial state
resp = http_request("GET", "/footprint")
print(f"Footprint response: {resp}", file=sys.stderr)

# Try encrypting a test plaintext
plaintext = bytes([0] * 16)
resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
print(f"Encrypt response: {resp}", file=sys.stderr)

# Check footprint after encryption
resp = http_request("GET", "/footprint")
print(f"Footprint after encrypt: {resp}", file=sys.stderr)

# Let's try a few more plaintexts to understand the pattern
for i in range(4):
    pt = bytes([i] * 16)
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    resp2 = http_request("GET", "/footprint")
    print(f"PT={i}: encrypt={resp}, footprint={resp2}", file=sys.stderr)