import json, sys, base64

def req(method, path, body=None, headers=None):
    h = {"method": method, "path": path}
    if body is not None:
        h["body"] = body
    if headers:
        h["headers"] = headers
    print(json.dumps({"http": h}), flush=True)
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {"raw": line.strip()}

paths = ["/", "/health", "/index.html", "/kex", "/negotiate", "/ssh", "/api", "/info",
         "/session", "/handshake", "/algorithms", "/algos", "/docs", "/openapi.json",
         "/api/kex", "/api/negotiate", "/ssh/negotiate", "/v1/kex", "/help", "/status",
         "/robots.txt", "/favicon.ico"]

for p in paths:
    r = req("GET", p)
    if r is None:
        print("NO REPLY for", p, flush=True)
        break
    b = r.get("body_b64", "")
    try:
        txt = base64.b64decode(b).decode("utf-8", "replace")
    except Exception:
        txt = b
    print("===", p, r.get("status"), r.get("content_type"), "len", len(b), flush=True)
    print(txt[:1200], flush=True)