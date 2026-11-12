import json, sys

def http(method, path, body=None, headers=None, body_hex=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    elif body is not None:
        req["http"]["body"] = body
    if headers:
        req["http"]["headers"] = headers
    print(json.dumps(req))
    sys.stdout.flush()
    line = sys.stdin.readline()
    return json.loads(line)

# Probe common endpoints
for p in ["/", "/parse", "/records", "/api/parse", "/health", "/status", "/flag", "/secret"]:
    try:
        r = http("GET", p)
        print(p, json.dumps(r)[:300])
    except Exception as e:
        print(p, "ERR", repr(e))

# Attempt overflow: long record to /parse
for n in [256, 512, 1024, 2048, 4096, 8192]:
    try:
        r = http("POST", "/parse", body_hex=("A" * n).encode().hex())
        print("POST /parse len", n, json.dumps(r)[:500])
    except Exception as e:
        print("POST /parse len", n, "ERR", repr(e))