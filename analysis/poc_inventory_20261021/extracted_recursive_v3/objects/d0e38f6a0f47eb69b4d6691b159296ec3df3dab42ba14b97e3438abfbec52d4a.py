import sys, json, base64, hashlib, secrets

# First, let's explore the HTTP endpoint to understand the SSH service interface
print(json.dumps({"http": {"method": "GET", "path": "/"}}), flush=True)

# Read the response
response = json.loads(sys.stdin.readline())
print(f"Response: {response}", file=sys.stderr)

# Decode the error body
error_body = base64.b64decode(response['body_b64'])
print(f"Error body: {error_body}", file=sys.stderr)

# Try common SSH-related endpoints
for path in ['/ssh', '/kex', '/negotiate', '/connect', '/session', '/api', '/health', '/info']:
    print(json.dumps({"http": {"method": "GET", "path": path}}), flush=True)
    resp = json.loads(sys.stdin.readline())
    print(f"{path}: {resp}", file=sys.stderr)
    if resp['status'] != 404:
        body = base64.b64decode(resp['body_b64'])
        print(f"  Body: {body}", file=sys.stderr)