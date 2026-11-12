import sys, json, base64

def req(method, path, body=None, headers=None, hexbody=None):
    msg = {"http": {"method": method, "path": path}}
    if headers:
        msg["http"]["headers"] = headers
    if hexbody is not None:
        msg["http"]["body_hex"] = hexbody
    elif body is not None:
        msg["http"]["body"] = body
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        r = json.loads(line)
    except Exception:
        return {"raw": line}
    if "body_b64" in r:
        try:
            r["body"] = base64.b64decode(r["body_b64"]).decode("utf-8", "replace")
        except Exception:
            pass
    return r

paths = ["/", "/admin", "/admin/", "/admin/secret", "/admin/panel", "/api/admin", "/health",
         "/robots.txt", "/secret", "/flag", "/login", "/index.html", "/admin/index.html",
         "/session", "/admin/session", "/dashboard"]
for p in paths:
    r = req("GET", p)
    print("=== GET", p, "===")
    print(json.dumps(r)[:1200])