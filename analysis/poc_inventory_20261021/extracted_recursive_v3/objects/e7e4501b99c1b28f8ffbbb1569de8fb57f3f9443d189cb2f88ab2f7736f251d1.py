import json, sys

def http(method, path, body=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body is not None:
        req["http"]["body"] = body
    if headers:
        req["http"]["headers"] = headers
    print(json.dumps(req))
    sys.stdout.flush()
    line = sys.stdin.readline()
    return json.loads(line)

r = http("GET", "/")
print(json.dumps(r))