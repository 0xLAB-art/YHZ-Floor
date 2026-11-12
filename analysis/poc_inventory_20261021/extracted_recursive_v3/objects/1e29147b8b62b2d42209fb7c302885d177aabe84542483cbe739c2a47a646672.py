import json, sys, base64, urllib.parse

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
        return None

def dec(r):
    if not r:
        return b""
    try:
        return base64.b64decode(r.get("body_b64", ""))
    except Exception:
        return b""

out = open("/tmp/opencode/log.txt", "a")
def log(*a):
    print("LOG", *a, file=out, flush=True)

paths = ["/", "/index", "/help", "/README", "/flag", "/secret", "/robots.txt", "/health", "/api", "/admin", "/debug"]
found = {}
for p in paths:
    r = req("GET", p)
    log(p, r.get("status") if r else None, dec(r)[:2000])
    if r:
        found[p] = (r.get("status"), dec(r))

# try template injection / deserialization style probes
payloads = [
    ("GET", "/?name={{7*7}}", None),
    ("GET", "/?q={{7*7}}", None),
    ("GET", "/?template={{7*7}}", None),
    ("POST", "/", '{"__proto__":{"a":"b"}}'),
]
for m, p, b in payloads:
    r = req(m, p, b)
    log(m, p, b, r.get("status") if r else None, dec(r)[:2000])

print("CLAIM:" + json.dumps({"secret_hex": "00"}), flush=True)