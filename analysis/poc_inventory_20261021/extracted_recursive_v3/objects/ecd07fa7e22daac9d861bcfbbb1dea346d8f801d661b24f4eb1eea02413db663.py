import sys, json, base64

def req(method, path, body=None, headers=None, hexbody=None):
    m = {"method": method, "path": path}
    if body is not None:
        m["body"] = body
    if hexbody is not None:
        m["body_hex"] = hexbody
    if headers:
        m["headers"] = headers
    print(json.dumps({"http": m}), flush=True)
    line = sys.stdin.readline()
    if not line:
        print("NO_REPLY", flush=True)
        return {}
    try:
        r = json.loads(line)
    except Exception:
        print("BADREPLY", line[:200], flush=True)
        return {}
    b = r.get("body_b64") or ""
    try:
        txt = base64.b64decode(b).decode("utf-8", "replace")
    except Exception:
        txt = "<decode fail>"
    print("### %s %s -> %s | %s" % (method, path, r.get("status"), txt[:400]), flush=True)
    return r

for p in ["/", "/help", "/index", "/health", "/api", "/api/help", "/parse", "/record", "/records", "/docs", "/openapi.json", "/robots.txt", "/source", "/debug"]:
    req("GET", p)

print("CLAIM:" + json.dumps({"secret_hex": ""}), flush=True)