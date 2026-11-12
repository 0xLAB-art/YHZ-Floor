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

# First, let's try to encrypt a test plaintext
plaintext = bytes([0] * 16)
resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
print(f"Encrypt response: {resp}", file=sys.stderr)

# Then get footprint
resp = http_request("GET", "/footprint")
print(f"Footprint response: {resp}", file=sys.stderr)

# Decode the body
body_b64 = resp['body_b64']
body = base64.b64decode(body_b64)
print(f"Decoded body: {body}", file=sys.stderr)
footprint = json.loads(body)
print(f"Pages: {footprint['pages']}", file=sys.stderr)
print(f"Count: {footprint['count']}", file=sys.stderr)

# Analyze pages: page = table * 256 + index
for page in footprint['pages']:
    table = page // 256
    index = page % 256
    print(f"  Page {page}: table={table}, index={index}", file=sys.stderr)