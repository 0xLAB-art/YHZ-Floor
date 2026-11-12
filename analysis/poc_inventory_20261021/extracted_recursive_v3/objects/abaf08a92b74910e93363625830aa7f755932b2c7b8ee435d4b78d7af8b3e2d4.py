import sys, json, base64

def req(method, path, body=None, headers=None):
    m = {"http": {"method": method, "path": path}}
    if body is not None:
        m["http"]["body"] = body
    if headers:
        m["http"]["headers"] = headers
    print(json.dumps(m), flush=True)
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)

r = req("GET", "/")
print("ROOT:", json.dumps(r)[:2000], flush=True)
for p in ["/health", "/index.html", "/robots.txt", "/admin", "/admin/", "/api", "/source", "/static/app.js"]:
    rr = req("GET", p)
    try:
        b = base64.b64decode(rr["body_b64"]).decode("utf-8", "replace") if rr else ""
    except Exception:
        b = ""
    print("PATH", p, rr.get("status") if rr else None, b[:1500], flush=True)