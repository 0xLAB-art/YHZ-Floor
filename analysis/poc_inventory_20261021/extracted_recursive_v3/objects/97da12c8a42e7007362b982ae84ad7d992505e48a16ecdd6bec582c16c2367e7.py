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
    line = sys.stdin.readline()
    print(f"Raw response: {line}", file=sys.stderr)
    if not line.strip():
        return {"status": 0, "body_b64": "", "content_type": ""}
    response = json.loads(line)
    return response

# Simple test
print("Testing service...", file=sys.stderr)
resp = http_request("POST", "/encrypt", body_hex="00" * 16)
print(f"Encrypt response: {resp}", file=sys.stderr)

if resp.get("status") == 200:
    resp = http_request("GET", "/footprint")
    print(f"Footprint response: {resp}", file=sys.stderr)
else:
    print("Encrypt failed", file=sys.stderr)