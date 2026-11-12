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
    except Exception:
        return {"parse_error": line}

def show(tag, r):
    if r is None:
        sys.stderr.write(tag + " -> None\n")
        return
    try:
        b = base64.b64decode(r.get("body_b64", ""))
    except Exception:
        b = b""
    sys.stderr.write("=== %s | status=%s ct=%s len=%d :: %s\n" % (
        tag, r.get("status"), r.get("content_type"), len(b),
        b[:600].decode("utf-8", "replace")))

paths = ["/health","/status","/info","/version","/docs","/openapi.json","/robots.txt",
 "/favicon.ico","/secret","/flag","/metrics","/events","/event","/log","/logs",
 "/data","/ingest","/submit","/import","/read","/load","/parse","/records","/record",
 "/v1","/v1/records","/v1/parse","/api/v1/records","/api/records","/api/parse",
 "/records/parse","/record/parse","/parse/record","/records.bin","/upload","/blob",
 "/packet","/packets","/frames","/frame","/pkt","/msg","/message","/messages",
 "/stream","/binary","/raw","/echo","/test","/ping","/vuln","/challenge","/ctf"]

for p in paths:
    show("GET " + p, req("GET", p))

for p in ["/","/records","/parse","/upload","/health"]:
    show("OPTIONS " + p, req("OPTIONS", p))
    show("POST " + p, req("POST", p, body=""))

show("HEAD /", req("HEAD", "/"))