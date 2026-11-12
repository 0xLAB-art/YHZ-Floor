import json, sys, base64

def req(method, path, headers=None, body=None):
    m = {"http": {"method": method, "path": path}}
    if headers: m["http"]["headers"] = headers
    if body is not None: m["http"]["body"] = body
    sys.stdout.write(json.dumps(m) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    r = json.loads(line)
    b = r.get("body_b64")
    if b:
        try:
            r["text"] = base64.b64decode(b).decode("utf-8", "replace")
        except Exception:
            r["text"] = ""
    return r

out = []
for p in ["/", "/index", "/login", "/admin", "/admin/secret", "/secret", "/robots.txt", "/help", "/api", "/health", "/static/app.js", "/app.js", "/main.js"]:
    r = req("GET", p)
    out.append({"path": p, "status": r.get("status") if r else None, "ct": r.get("content_type") if r else None, "body": (r.get("text", "")[:1500] if r else None)})

sys.stderr.write(json.dumps(out, indent=1))
print('CLAIM:{"secret_hex": ""}')