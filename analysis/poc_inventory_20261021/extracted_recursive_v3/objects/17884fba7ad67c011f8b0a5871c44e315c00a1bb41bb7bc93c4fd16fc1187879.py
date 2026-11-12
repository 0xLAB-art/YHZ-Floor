import json, sys

def req(method, path, body=None, headers=None):
    r = {"http": {"method": method, "path": path}}
    if body is not None:
        r["http"]["body"] = body
    if headers:
        r["http"]["headers"] = headers
    print(json.dumps(r))
    sys.stdout.flush()
    line = sys.stdin.readline()
    return json.loads(line)

for p in ["/", "/help", "/parse", "/records", "/api", "/status", "/health"]:
    try:
        resp = req("GET", p)
        print(p, json.dumps(resp)[:400])
    except Exception as e:
        print(p, "ERR", e)