import sys, json, base64

LOG = "/tmp/probe2.txt"
try:
    f = open(LOG, "w", buffering=1)
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
    except Exception as e:
        rec("<<< parsefail", repr(l)[:400])
        return None
    rec("<<<", json.dumps(r)[:3000])
    return r

def dec(r):
    if not r:
        return ""
    try:
        return base64.b64decode(r.get("body_b64", "")).decode("utf-8", "replace")
    except Exception:
        return ""

#1. Does an old log survive?  Read whatever /tmp has before overwriting.
import os
rec("=== EXISTING /tmp FILES ===")
try:
    for n in sorted(os.listdir("/tmp")):
        try:
            sz = os.path.getsize(os.path.join("/tmp", n))
        except Exception:
            sz = -1
        rec(" ", n, sz)
except Exception as e:
    rec("ls fail", e)

for cand in ("/tmp/probe.txt", "/tmp/probe2.txt"):
    try:
        with open(cand) as fh:
            rec("=== CONTENT OF", cand)
            rec(fh.read()[:40000])
    except Exception as e:
        rec("no read", cand, e)

# 2. Probe wide to map the service surface.
PATHS = ["/", "/index.html", "/admin", "/admin/", "/api", "/docs", "/openapi.json",
         "/.env", "/robots.txt", "/login", "/static/", "/app.js", "/source", "/debug"]
for p in PATHS:
    r = req("GET", p)
    rec("===== BODY", p, (r or {}).get("status"), (r or {}).get("content_type"))
    rec(dec(r)[:5000])

if f:
    f.close()
print("CLAIM:{\"secret_hex\": \"\"}", flush=True)