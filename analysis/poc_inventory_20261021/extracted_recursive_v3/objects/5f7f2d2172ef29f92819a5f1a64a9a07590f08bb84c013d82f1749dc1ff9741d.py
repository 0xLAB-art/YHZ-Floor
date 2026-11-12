import sys, json, base64

def req(method, path, body=None, body_hex=None, headers=None):
    m = {"http": {"method": method, "path": path}}
    if body is not None:
        m["http"]["body"] = body
    if body_hex is not None:
        m["http"]["body_hex"] = body_hex
    if headers:
        m["http"]["headers"] = headers
    print(json.dumps(m), flush=True)
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        r = json.loads(line)
    except Exception:
        return {"raw": line}
    return r

def show(tag, r):
    if r is None:
        print(tag, "-> None"); return
    st = r.get("status")
    b = r.get("body_b64")
    ct = r.get("content_type")
    if b is None:
        print(tag, "->", r); return
    try:
        txt = base64.b64decode(b)
    except Exception:
        txt = b
    try:
        txt = txt.decode("utf-8", "replace")
    except Exception:
        txt = repr(txt)
    if len(txt) > 1200:
        txt = txt[:1200] + "...<trunc>"
    print(tag, "->", st, ct, repr(txt), flush=True)

paths = ["/", "/health", "/index.html", "/robots.txt", "/help", "/version",
         "/records", "/record", "/parse", "/parsing", "/records/parse",
         "/record/parse", "/api", "/api/records", "/api/parse", "/api/v1/records",
         "/v1/records", "/submit", "/read", "/upload", "/data", "/debug",
         "/status", "/info", "/favicon.ico"]
for p in paths:
    show("GET " + p, req("GET", p))

for p in ["/", "/records", "/parse", "/api/records"]:
    show("POST " + p, req("POST", p, body=""))

print("DONE-RECON", flush=True)