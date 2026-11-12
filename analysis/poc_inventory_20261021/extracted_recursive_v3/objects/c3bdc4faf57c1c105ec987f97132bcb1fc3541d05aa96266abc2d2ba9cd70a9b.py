import sys, json, base64, os

LOG = "/tmp/probe3.txt"
try:
    f = open(LOG, "a", buffering=1)
except Exception:
    f = None

def rec(*a):
    if f:
        try:
            f.write(" ".join(str(x) for x in a) + "\n")
        except Exception:
            pass

def req(method, path, body=None, headers=None):
    m = {"http": {"method": method, "path": path}}
    if body is not None:
        m["http"]["body"] = body
    if headers:
        m["http"]["headers"] = headers
    line = json.dumps(m)
    rec(">>>", line)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
    l = sys.stdin.readline()
    if not l:
        rec("<<< EOF")
        return None
    try:
        r = json.loads(l)
    except Exception:
        rec("<<< parsefail", repr(l)[:400])
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

rec("=== /tmp listing ===")
try:
    for n in sorted(os.listdir("/tmp")):
        rec(" ", n)
except Exception as e:
    rec("ls fail", e)

for cand in ("/tmp/probe.txt", "/tmp/probe2.txt"):
    try:
        with open(cand) as fh:
            rec("=== PREVIOUS LOG", cand)
            rec(fh.read()[:60000])
    except Exception as e:
        rec("no read", cand, repr(e))

PATHS = ["/", "/index.html", "/health", "/robots.txt", "/admin", "/admin/", "/admin/secret",
         "/api", "/docs", "/openapi.json", "/login", "/session", "/static/app.js","/app.js",
         "/source", "/debug", "/.env", "/flag"]
for p in PATHS:
    r = req("GET", p)
    rec("===== BODY", p, (r or {}).get("status"), (r or {}).get("content_type"))
    rec(dec(r)[:5000])

if f:
    f.close()
print("CLAIM:{\"secret_hex\": \"\"}", flush=True)