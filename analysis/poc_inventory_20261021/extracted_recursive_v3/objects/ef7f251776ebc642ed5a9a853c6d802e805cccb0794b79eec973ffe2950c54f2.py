import json, sys

def http(method, path, body=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body is not None:
        req["http"]["body"] = body
    if headers is not None:
        req["http"]["headers"] = headers
    print(json.dumps(req))
    sys.stdout.flush()
    line = sys.stdin.readline()
    return json.loads(line)

for p in ["/", "/index.html", "/parse", "/records", "/api", "/health", "/robots.txt"]:
    r = http("GET", p)
    print(p, r.get("status"), (r.get("body_b64") or "")[:200])