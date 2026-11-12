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

# Try GET /footprint first to see initial state
resp = http_request("GET", "/footprint")
print(f"Footprint response: {resp}")

# Try encrypting a test plaintext
plaintext = bytes([0] * 16)
resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
print(f"Encrypt response: {resp}")

# Check footprint after encryption
resp = http_request("GET", "/footprint")
print(f"Footprint after encrypt: {resp}")