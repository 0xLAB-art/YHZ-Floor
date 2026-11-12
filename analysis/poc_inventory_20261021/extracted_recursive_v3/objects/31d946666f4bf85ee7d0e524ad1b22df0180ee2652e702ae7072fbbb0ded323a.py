import sys, json, base64

def req(method, path, headers=None, body=None, body_hex=None):
    m = {"http": {"method": method, "path": path}}
    if headers: m["http"]["headers"] = headers
    if body_hex is not None: m["http"]["body_hex"] = body_hex
    elif body is not None: m["http"]["body"] = body
    print(json.dumps(m), flush=True)
    line = sys.stdin.readline()
    if not line: return None
    try:
        r = json.loads(line)
    except Exception:
        return None
    b = r.get("body_b64")
    if b:
        try: r["text"] = base64.b64decode(b).decode("utf-8", "replace")
        except Exception: pass
    return r

out = []
for p in ["/", "/index.html", "/help", "/api", "/robots.txt"]:
    r = req("GET", p)
    out.append((p, None if r is None else (r.get("status"), r.get("content_type"), str(r.get("text"))[:400])))
sys.stderr.write(repr(out) + "\n")
print('CLAIM:{"secret_hex": ""}', flush=True)