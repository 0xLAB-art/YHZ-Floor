import sys, json, base64

def req(method, path, body=None, headers=None):
    o = {"method": method, "path": path}
    if body is not None:
        o["body"] = body
    if headers:
        o["headers"] = headers
    print(json.dumps({"http": o}), flush=True)
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {"raw": line}

def show(tag, r):
    if r is None:
        print(tag, "-> None", flush=True)
        return
    b = r.get("body_b64", "")
    try:
        d = base64.b64decode(b)
    except Exception:
        d = b.encode()
    print("==", tag, r.get("status"), r.get("content_type"), flush=True)
    print(repr(d[:600]), flush=True)

paths = ["/", "/help", "/index.html", "/robots.txt", "/readme", "/api", "/health", 
 "/record", "/records", "/parse", "/parser", "/upload", "/decode", "/log"]
for p in paths:
    show("GET " + p, req("GET", p))