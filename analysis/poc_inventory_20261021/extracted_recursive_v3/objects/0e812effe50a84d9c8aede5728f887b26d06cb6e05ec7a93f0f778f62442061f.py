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

for p in ["/", "/help", "/parse", "/records", "/api", "/status", "/health", "/flag", "/secret"]:
    try:
        resp = req("GET", p)
        print("RESP", p, json.dumps(resp)[:600], flush=True)
    except Exception as e:
        print("ERR", p, repr(e), flush=True)