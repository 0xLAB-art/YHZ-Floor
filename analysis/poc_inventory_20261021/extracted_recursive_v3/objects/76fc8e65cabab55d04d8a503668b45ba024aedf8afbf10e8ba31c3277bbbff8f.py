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
print("Exploring service...")

# Try to encrypt a test plaintext
test_pt = b'\x00' * 16
resp = http_request("POST", "/encrypt", body_hex=test_pt.hex())
print(f"Encrypt response: {resp}")

# Get footprint
resp = http_request("GET", "/footprint")
print(f"Footprint response: {resp}")

# Let's also check if there's a root endpoint
resp = http_request("GET", "/")
print(f"Root response: {resp}")

# Now let's understand the footprint format better by doing a few encryptions
for i in range(3):
    pt = bytes([i] * 16)
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    print(f"Encrypt {i}: {resp}")
    resp = http_request("GET", "/footprint")
    print(f"Footprint {i}: {resp}")

print("Done exploring")