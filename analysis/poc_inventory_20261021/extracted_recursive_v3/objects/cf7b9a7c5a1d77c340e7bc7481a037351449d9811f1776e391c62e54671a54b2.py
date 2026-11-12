import json, sys, base64

def req(method, path, headers=None, body=None):
    r = {"http": {"method": method, "path": path}}
    if headers: r["http"]["headers"] = headers
    if body is not None: r["http"]["body"] = body
    print(json.dumps(r), flush=True)
    line = sys.stdin.readline()
    return json.loads(line)

resp = req("GET", "/")
print(json.dumps(resp))