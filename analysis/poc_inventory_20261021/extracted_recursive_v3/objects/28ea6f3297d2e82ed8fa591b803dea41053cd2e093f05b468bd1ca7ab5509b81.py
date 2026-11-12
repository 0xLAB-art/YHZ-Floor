import sys, json, base64, time

# First, let's explore the service endpoints
print(json.dumps({"http": {"method": "GET", "path": "/"}}), flush=True)
reply = json.loads(sys.stdin.readline())
print(f"Status: {reply['status']}", file=sys.stderr)
print(f"Body: {base64.b64decode(reply['body_b64'])}", file=sys.stderr)

# Try common endpoints
for path in ["/login", "/session", "/profile", "/secret", "/flag", "/admin"]:
    print(json.dumps({"http": {"method": "GET", "path": path}}), flush=True)
    reply = json.loads(sys.stdin.readline())
    print(f"{path}: Status {reply['status']}", file=sys.stderr)
    if reply['status'] == 200:
        print(f"  Body: {base64.b64decode(reply['body_b64'])}", file=sys.stderr)

print("CLAIM:{\"secret_hex\": \"\"}", flush=True)