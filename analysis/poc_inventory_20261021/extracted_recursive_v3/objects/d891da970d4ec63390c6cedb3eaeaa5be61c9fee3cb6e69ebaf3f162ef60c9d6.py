import sys, json, base64, time

# Explore more endpoints and try POST to /session
print(json.dumps({"http": {"method": "POST", "path": "/session", "body": "", "headers": {"Content-Type": "application/json"}}}), flush=True)
reply = json.loads(sys.stdin.readline())
print(f"POST /session: Status {reply['status']}", file=sys.stderr)
if reply['status'] == 200:
    print(f"  Body: {base64.b64decode(reply['body_b64'])}", file=sys.stderr)

# Try other common endpoints
for path in ["/verify", "/decrypt", "/check", "/validate", "/api/secret", "/api/flag", "/me", "/user", "/account"]:
    print(json.dumps({"http": {"method": "GET", "path": path}}), flush=True)
    reply = json.loads(sys.stdin.readline())
    print(f"{path}: Status {reply['status']}", file=sys.stderr)
    if reply['status'] == 200:
        print(f"  Body: {base64.b64decode(reply['body_b64'])}", file=sys.stderr)

print("CLAIM:{\"secret_hex\": \"\"}", flush=True)