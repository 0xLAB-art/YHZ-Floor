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

resp = req("GET", "/")
print(json.dumps(resp))