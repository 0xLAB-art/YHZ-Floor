import sys, json, base64

def req(method, path, body=None, headers=None):
    m = {"method": method, "path": path}
    if body is not None:
        m["body"] = body
    if headers:
        m["headers"] = headers
    sys.stdout.write(json.dumps({"http": m}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception as e:
        return {"parse_error": line}

def show(tag, r):
    if r is None:
        sys.stderr.write(tag + " -> None\n")
        return
    try:
        b = base64.b64decode(r.get("body_b64", ""))
    except Exception:
        b = b""
    sys.stderr.write("=== %s | status=%s ct=%s len=%d\n%s\n" % (
        tag, r.get("status"), r.get("content_type"), len(b),
        b[:2000].decode("utf-8", "replace")))

for p in ["/", "/health", "/index.html", "/help", "/api", "/parse", "/records", "/record", "/upload", "/debug"]:
    show("GET " + p, req("GET", p))