import sys, json, base64

def req(method, path, body=None, headers=None):
    msg = {"http": {"method": method, "path": path}}
    if body is not None:
        msg["http"]["body"] = body
    if headers:
        msg["http"]["headers"] = headers
    print(json.dumps(msg), flush=True)
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {"status": -1, "body_b64": ""}

paths = ["/", "/admin", "/admin/", "/login", "/session", "/admin/session", "/api",
         "/api/session", "/robots.txt", "/source", "/app.py", "/index.html",
         "/static/app.js", "/openapi.json", "/docs", "/health", "/flag",
         "/.git/HEAD", "/debug", "/admin/index.html", "/verify", "/secret",
         "/admin/secret", "/admin/flag", "/version", "/info", "/dump"]

for p in paths:
    r = req("GET", p)
    if r is None:
        break
    try:
        b = base64.b64decode(r.get("body_b64", "")).decode("utf-8", "replace")
    except Exception:
        b = "<binary>"
    print("=== %s -> %s %s" % (p, r.get("status"), r.get("content_type")), flush=True)
    print(b[:3000], flush=True)
    print("=== end %s" % p, flush=True)