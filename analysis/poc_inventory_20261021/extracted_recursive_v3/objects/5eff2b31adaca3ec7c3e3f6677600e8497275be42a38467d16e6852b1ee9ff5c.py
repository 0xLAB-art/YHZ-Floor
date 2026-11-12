import sys, json, base64

def req(path, method="GET", body=None, headers=None):
    m = {"method": method, "path": path}
    if body is not None:
        m["body"] = body
    if headers:
        m["headers"] = headers
    print(json.dumps({"http": m}), flush=True)
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)

# Probe common endpoints
for p in ["/", "/help", "/index.html", "/api", "/parse", "/record", "/health", "/status"]:
    r = req(p)
    print("PROBE", p, json.dumps(r)[:2000], flush=True)