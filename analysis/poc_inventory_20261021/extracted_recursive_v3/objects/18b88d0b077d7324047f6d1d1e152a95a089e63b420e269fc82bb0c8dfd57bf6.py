import json, sys, base64

def http(method, path, body=None, headers=None, body_hex=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    elif body is not None:
        req["http"]["body"] = body
    if headers is not None:
        req["http"]["headers"] = headers
    print(json.dumps(req))
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return {"status": None, "body_b64": ""}
    return json.loads(line)

r = http("GET", "/")
try:
    b = base64.b64decode(r.get("body_b64") or "").decode()
except Exception:
    b = r.get("body_b64", "")
print("ROOT", r.get("status"), repr(b[:500]))