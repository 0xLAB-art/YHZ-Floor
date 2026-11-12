import sys, json

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
    return line.strip()

paths = ["/", "/index", "/health", "/help", "/parse", "/record", "/api", "/robots.txt", "/status", "/info"]
for p in paths:
    r = req("GET", p)
    print("PROBE %s => %s" % (p, r), flush=True)