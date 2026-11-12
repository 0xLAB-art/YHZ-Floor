import sys, json, base64

def req(method, path, body=None, body_hex=None, headers=None):
    msg = {"http": {"method": method, "path": path}}
    if headers:
        msg["http"]["headers"] = headers
    if body is not None:
        msg["http"]["body"] = body
    if body_hex is not None:
        msg["http"]["body_hex"] = body_hex
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {"raw": line}

def show(tag, r):
    if not r:
        print("R:" + tag + ": NONE")
        return
    b = r.get("body_b64")
    try:
        body = base64.b64decode(b).decode("utf-8", "replace")[:1500]
    except Exception:
        body = str(b)
    print("R:" + tag + ": st=" + str(r.get("status")) + " ct=" + str(r.get("content_type")) + " :: " + body)

probes = [
    ("root", dict(method="GET", path="/")),
    ("robots", dict(method="GET", path="/robots.txt")),
    ("flag", dict(method="GET", path="/flag")),
    ("flagtxt", dict(method="GET", path="/flag.txt")),
    ("secret", dict(method="GET", path="/secret")),
    ("search_ssti", dict(method="GET", path="/search?q=%7B%7B7*7%7D%7D")),
    ("root_ssti", dict(method="GET", path="/?q=%7B%7B7*7%7D%7D&name=%7B%7B7*7%7D%7D")),
    ("api", dict(method="GET", path="/api")),
    ("debug", dict(method="GET", path="/debug")),
    ("health", dict(method="GET", path="/health")),
    ("index_php", dict(method="GET", path="/index.php")),
    ("post_root", dict(method="POST", path="/", body="test")),
]
for tag, kw in probes:
    try:
        r = req(**kw)
    except Exception as e:
        r = None
        print("R:" + tag + ": EXC " + str(e))
    show(tag, r)