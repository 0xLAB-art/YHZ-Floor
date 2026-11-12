import sys
import json
import base64

def http_request(method, path, body=None, headers=None):
    req = {
        "http": {
            "method": method,
            "path": path,
        }
    }
    if body is not None:
        req["http"]["body"] = body
    if headers is not None:
        req["http"]["headers"] = headers
    print(json.dumps(req), flush=True)
    response = json.loads(sys.stdin.readline())
    return response

# First, let's explore the service to find endpoints
print("Exploring service...")

# Try common endpoints
for path in ["/", "/parse", "/record", "/api/parse", "/api/record", "/v1/parse", "/v1/record"]:
    resp = http_request("GET", path)
    print(f"GET {path}: status={resp['status']}, body={resp.get('body_b64', '')[:100]}")
    if resp['status'] == 200:
        body = base64.b64decode(resp['body_b64']).decode('utf-8', errors='replace')
        print(f"  Body: {body[:500]}")