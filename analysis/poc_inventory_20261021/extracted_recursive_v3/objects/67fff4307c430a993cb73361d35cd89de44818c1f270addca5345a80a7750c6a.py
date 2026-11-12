import sys, json

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
    try:
        return json.loads(line)
    except Exception:
        return {"raw": line}

def show(tag, r):
    if r is None:
        print("#", tag, "NO REPLY", flush=True)
        return
    try:
        import base64
        b = base64.b64decode(r.get("body_b64", ""))
        print("#", tag, r.get("status"), repr(b[:800]), flush=True)
    except Exception as e:
        print("#", tag, r, flush=True)

for p in ["/", "/index.html", "/help", "/parse", "/record", "/robots.txt", "/favicon.ico"]:
    r = req("GET", p)
    show(p, r)

print("CLAIM:" + json.dumps({"secret_hex": ""}), flush=True)