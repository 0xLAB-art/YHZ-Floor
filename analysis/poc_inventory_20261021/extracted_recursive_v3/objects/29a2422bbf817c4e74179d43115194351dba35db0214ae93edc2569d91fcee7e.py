import sys, json, base64, zlib, struct

def req(path, method="GET", body=None, body_hex=None, headers=None):
    m = {"http": {"method": method, "path": path}}
    if headers: m["http"]["headers"] = headers
    if body_hex is not None: m["http"]["body_hex"] = body_hex
    elif body is not None: m["http"]["body"] = body
    print(json.dumps(m), flush=True)
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        r = json.loads(line)
    except Exception:
        return None
    b = r.get("body_b64")
    if b:
        try: r["text"] = base64.b64decode(b).decode("utf-8", "replace")
        except Exception: pass
    return r

def show(tag, r):
    if r is None:
        print(tag, "NOREPLY", flush=True); return
    t = r.get("text","")
    print(tag, r.get("status"), r.get("content_type"), t[:400].replace("\n"," "), flush=True)

out = []
#1. Baseline discovery
for p in ["/", "/index.html", "/help", "/readme", "/record", "/parse", "/records", "/health"]:
    r = req(p)
    show("GET "+p, r)
    if r and r.get("text"): out.append((p, r["text"][:2000]))

# 2. POST probes on likely parse endpoints
for p in ["/record", "/parse", "/records", "/read", "/"]:
    r = req(p, "POST", body="A")
    show("POST "+p, r)
    if r and r.get("text"): out.append(("POST "+p, r["text"][:2000]))

print("===OUT===", flush=True)
for k,v in out:
    print("---", k, v.replace("\n"," ")[:600], flush=True)

print("CLAIM:{\"secret_hex\": \"\"}", flush=True)