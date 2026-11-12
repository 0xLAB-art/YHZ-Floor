import json, sys, base64

def req(method, path, headers=None, body=None, body_hex=None):
    r = {"http": {"method": method, "path": path}}
    if headers: r["http"]["headers"] = headers
    if body is not None: r["http"]["body"] = body
    if body_hex is not None: r["http"]["body_hex"] = body_hex
    print(json.dumps(r), flush=True)
    line = sys.stdin.readline()
    return json.loads(line)

for p in ["/", "/login", "/admin", "/session", "/flag", "/secret"]:
    resp = req("GET", p)
    print(p, resp.get("status"), base64.b64decode(resp.get("body_b64","")).decode(errors="replace")[:500])