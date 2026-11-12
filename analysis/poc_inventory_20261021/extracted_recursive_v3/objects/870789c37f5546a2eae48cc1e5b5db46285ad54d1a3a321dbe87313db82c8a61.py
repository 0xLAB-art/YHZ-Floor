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

# First, let's try to encrypt a test plaintext and get footprint
print("Testing service...")

# Encrypt 16 zero bytes
resp = http_request("POST", "/encrypt", body_hex="00" * 32)
print(f"Encrypt response: {resp}")

# Get footprint
resp = http_request("GET", "/footprint")
print(f"Footprint response: {resp}")

# Let's try a few more to understand the pattern
for i in range(3):
    pt = bytes([i] * 16).hex()
    resp = http_request("POST", "/encrypt", body_hex=pt)
    print(f"Encrypt {i} response: {resp}")
    resp = http_request("GET", "/footprint")
    print(f"Footprint {i} response: {resp}")