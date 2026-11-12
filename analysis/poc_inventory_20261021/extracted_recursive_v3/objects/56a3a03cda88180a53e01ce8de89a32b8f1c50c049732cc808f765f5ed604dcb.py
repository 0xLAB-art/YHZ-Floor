import sys, json, base64, os

LOG = "/tmp/probe.txt"
f = open(LOG, "w", buffering=1)

def rec(*a):
    try:
        f.write(" ".join(str(x) for x in a) + "\n")
    except Exception:
        pass

def req(method, path, body=None, headers=None, timeout_note=""):
    m = {"http": {"method": method, "path": path}}
    if body is not None:
        m["http"]["body"] = body
    if headers:
        m["http"]["headers"] = headers
    line = json.dumps(m)
    rec(">>>", line[:2000])
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
    l = sys.stdin.readline()
    if not l:
        rec("<<< EOF")
        return None
    try:
        r = json.loads(l)
    except Exception as e:
        rec("<<< parse error", repr(l)[:500], repr(e))
        return None
    rec("<<<", json.dumps(r)[:4000])
    return r

def dec(r):
    if not r:
        return ""
    try:
        return base64.b64decode(r.get("body_b64", "")).decode("utf-8", "replace")
    except Exception:
        return ""

PATHS = ["/", "/index.html", "/health", "/healthz", "/robots.txt", "/favicon.ico",
         "/admin", "/admin/", "/admin/index.html", "/admin/secret", "/admin/session",
         "/api", "/api/", "/api/session", "/api/admin", "/api/secret", "/session", "/login",
         "/app.js", "/main.js", "/script.js", "/bundle.js", "/static/app.js", "/static/main.js",
         "/static/bundle.js", "/assets/app.js", "/js/app.js", "/client.js", "/index.js",
         "/source", "/src", "/debug", "/flag", "/secret", "/openapi.json", "/swagger.json",
         "/.env", "/README", "/README.md", "/Dockerfile", "/robots", "/sitemap.xml"]

for p in PATHS:
    r = req("GET", p)
    if r:
        b = dec(r)
        rec("===== BODY", p, r.get("status"), r.get("content_type"))
        rec(b[:6000])

HDR_TRIES = [
    {"X-Session-Token": "admin"},
    {"X-Session": "admin"},
    {"X-Admin-Token": "admin"},
    {"Authorization": "Bearer admin"},
    {"Cookie": "session=admin"},
    {"Cookie": "token=admin"},
    {"Cookie": "admin=1"},
    {"X-Session-Token": "1"},
    {"X-Session-Token": ""},
    {"X-User": "admin"},
    {"X-Admin": "true"},
]
for h in HDR_TRIES:
    r = req("GET", "/admin", headers=h)
    if r:
        rec("===== HDRBODY", json.dumps(h), r.get("status"))
        rec(dec(r)[:3000])

f.close()
print("CLAIM:{\"secret_hex\": \"\"}", flush=True)