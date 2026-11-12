import json, sys

def req(method, path, body=None, body_hex=None, headers=None):
    m = {"http": {"method": method, "path": path}}
    if body is not None:
        m["http"]["body"] = body
    if body_hex is not None:
        m["http"]["body_hex"] = body_hex
    if headers:
        m["http"]["headers"] = headers
    sys.stdout.write(json.dumps(m) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return {"status": -1, "body_b64": ""}
    return json.loads(line)

import base64

for p in ["/", "/index", "/help", "/health", "/api", "/status", "/records", "/parse"]:
    r = req("GET", p)
    print("==", p, r.get("status"))
    try:
        print(repr(base64.b64decode(r.get("body_b64", ""))[:600]))
    except Exception as e:
        print("ERR", e)

# try POST to root and common endpoints
for p in ["/", "/parse", "/records", "/record"]:
    r = req("POST", p, body="hello")
    print("POST", p, r.get("status"))
    try:
        print(repr(base64.b64decode(r.get("body_b64", ""))[:600]))
    except Exception as e:
        print("ERR", e)