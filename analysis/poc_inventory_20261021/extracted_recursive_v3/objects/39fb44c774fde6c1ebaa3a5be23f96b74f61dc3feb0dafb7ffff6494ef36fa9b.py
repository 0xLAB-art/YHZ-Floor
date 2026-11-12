import sys, json, base64

token_hex = "b5a293cf06b3a76d49ad26acf4a7c50229d39ffce9534e629dee02ae0de63992"

for path in ["/secret", "/flag", "/admin", "/profile", "/me"]:
    print(json.dumps({"http": {"method": "GET", "path": path, "headers": {"Cookie": "session=" + token_hex}}}), flush=True)
    reply = json.loads(sys.stdin.readline())
    print(f"{path} cookie: {reply['status']}", file=sys.stderr)
    if reply['status'] == 200:
        print(base64.b64decode(reply['body_b64']), file=sys.stderr)

for path in ["/secret", "/flag", "/admin", "/profile", "/me"]:
    print(json.dumps({"http": {"method": "GET", "path": path, "headers": {"Authorization": "Bearer " + token_hex}}}), flush=True)
    reply = json.loads(sys.stdin.readline())
    print(f"{path} bearer: {reply['status']}", file=sys.stderr)
    if reply['status'] == 200:
        print(base64.b64decode(reply['body_b64']), file=sys.stderr)

print("CLAIM:{\"secret_hex\": \"\"}", flush=True)