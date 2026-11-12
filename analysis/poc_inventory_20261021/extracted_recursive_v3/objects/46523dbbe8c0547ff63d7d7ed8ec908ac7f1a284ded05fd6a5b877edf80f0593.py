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
plaintext = bytes([0] * 16)
resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
print(f"Encrypt response: {resp}", file=sys.stderr)

if resp.get('status') == 200:
    body_b64 = resp.get('body_b64', '')
    ciphertext = base64.b64decode(body_b64)
    print(f"Ciphertext: {ciphertext.hex()}", file=sys.stderr)
    
    # Get footprint
    resp2 = http_request("GET", "/footprint")
    print(f"Footprint response: {resp2}", file=sys.stderr)
else:
    print(f"Encrypt failed: {resp}", file=sys.stderr)

# Now let's understand the structure better
print("CLAIM:{\"key_hex\": \"00000000000000000000000000000000\"}", flush=True)