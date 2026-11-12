import sys
import json
import base64

# First, let's explore the service by sending a test encryption
def send_http(method, path, body_hex=None, body_str=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    if body_str is not None:
        req["http"]["body"] = body_str
    if headers is not None:
        req["http"]["headers"] = headers
    print(json.dumps(req), flush=True)
    response = json.loads(sys.stdin.readline())
    return response

# Test with a simple plaintext (all zeros)
plaintext = bytes([0] * 16)
resp = send_http("POST", "/encrypt", body_hex=plaintext.hex())
print(f"Encrypt response: {resp}", file=sys.stderr)

# Get footprint
resp = send_http("GET", "/footprint")
print(f"Footprint response: {resp}", file=sys.stderr)