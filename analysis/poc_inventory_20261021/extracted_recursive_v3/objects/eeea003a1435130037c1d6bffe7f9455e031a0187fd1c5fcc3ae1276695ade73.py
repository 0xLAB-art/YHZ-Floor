import sys, json, base64, re, itertools

def req(method, path, headers=None, body=None, body_hex=None):
    m = {"http": {"method": method, "path": path}}
    if headers: m["http"]["headers"] = headers
    if body_hex is not None: m["http"]["body_hex"] = body_hex
    elif body is not None: m["http"]["body"] = body
    sys.stdout.write(json.dumps(m) + "\n"); sys.stdout.flush()
    line = sys.stdin.readline()
    if not line: return None
    try: r = json.loads(line)
    except Exception: return None
    b = r.get("body_b64")
    if b:
        try:
            raw = base64.b64decode(b)
            r["text"] = raw.decode("utf-8", "replace")
            r["raw"] = raw.hex()
        except Exception: pass
    return r

paths = ["/","/parse","/records","/record","/upload","/ingest","/submit","/data","/v1/parse",
"/health","/healthz","/status","/index","/docs","/openapi.json","/swagger.json","/source",
"/flag","/secret","/debug","/info","/version","/api/parse","/api/v1/parse","/process",
"/msg","/message","/messages","/packet","/packets","/frame","/frames","/tlv","/proto",
"/protocol","/binary","/blob","/read","/write","/decode","/encode","/echo","/test",
"/hello","/ping","/login","/session","/env","/config","/admin","/dump","/log","/logs"]

log = []
found = ""
for p in paths:
    for mth in ("GET", "POST"):
        r = req(mth, p)
        if r is None:
            log.append((p, mth, "NO REPLY")); continue
        st = r.get("status"); ct = r.get("content_type"); tx = str(r.get("text"))[:300]
        log.append((p, mth, st, ct, tx))
        if st != 404:
            for m in re.findall(r"\b[0-9a-fA-F]{16,}\b", str(r.get("text","")) + str(r.get("raw",""))):
                if len(set(m.lower())) > 3:
                    found = m

sys.stderr.write(json.dumps(log, indent=0) + "\n")
sys.stderr.write("FOUND=" + found + "\n")
print('CLAIM:{"secret_hex": "' + found + '"}', flush=True)