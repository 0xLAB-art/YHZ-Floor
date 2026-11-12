import sys
import json
import base64

def http_request(method, path, body=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body is not None:
        req["http"]["body"] = body
    if headers is not None:
        req["http"]["headers"] = headers
    print(json.dumps(req), flush=True)
    response = json.loads(sys.stdin.readline())
    return response

# First, let's test the service with a simple encryption - send raw 16 bytes as latin-1 string
plaintext = '\x00' * 16
resp = http_request("POST", "/encrypt", body=plaintext)
print(f"Encrypt response: {resp}", file=sys.stderr)

# Get footprint
resp = http_request("GET", "/footprint")
print(f"Footprint response: {resp}", file=sys.stderr)

# Print claim placeholder
print('CLAIM:{"key_hex": "' + '00' * 16 + '"}')