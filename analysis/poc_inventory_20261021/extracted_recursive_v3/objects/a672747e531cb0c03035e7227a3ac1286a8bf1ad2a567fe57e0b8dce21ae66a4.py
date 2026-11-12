import sys, json, base64

def q(method, path, body=None, body_hex=None, headers=None):
    m = {"q": "http", "method": method, "path": path}
    if headers: m["headers"] = headers
    if body is not None: m["body"] = body
    if body_hex is not None: m["body_hex"] = body_hex
    print(json.dumps(m), flush=True)
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        r = json.loads(line)
    except Exception:
        return None
    b = r.get("body_b64")
    txt = base64.b64decode(b).decode("utf-8", "replace") if b else ""
    return (r.get("status"), r.get("content_type"), txt)

out = []
for p in ["/", "/index", "/index.html", "/health", "/api", "/parse", "/record", "/robots.txt"]:
    try:
        r = q("GET", p)
    except Exception as e:
        r = ("ERR", "", str(e))
    out.append("GET %s -> %r" % (p, r))

for p in ["/", "/parse", "/record", "/api", "/api/parse"]:
    try:
        r = q("POST", p, body="AAAA")
    except Exception as e:
        r = ("ERR", "", str(e))
    out.append("POST %s -> %r" % (p, r))

sys.stderr.write("\n".join(out) + "\n")
print("CLAIM:" + json.dumps({"secret_hex": ""}))