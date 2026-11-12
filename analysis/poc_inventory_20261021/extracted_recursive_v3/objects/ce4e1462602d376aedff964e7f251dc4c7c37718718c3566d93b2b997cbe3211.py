import sys, json, base64
def http(method, path, body=None, body_hex=None, headers=None):
    req={"http":{"method":method,"path":path}}
    if body is not None:
        req["http"]["body"]=body
    if body_hex is not None:
        req["http"]["body_hex"]=body_hex
    if headers is not None:
        req["http"]["headers"]=headers
    print(json.dumps(req), flush=True)
    line=sys.stdin.readline()
    if not line:
        return None
    try:
        r=json.loads(line)
    except Exception as e:
        return {"_raw":line[:1000], "_err":str(e)}
    return r
def body_text(r):
    if r is None: return "NORESP"
    if "_raw" in r: return str(r)[:800]
    b64=r.get("body_b64","")
    try:
        b=base64.b64decode(b64)
    except Exception as e:
        return f"st={r.get('status')} b64err {e}"
    try:
        t=b.decode()
    except:
        t=repr(b[:1000])
    return f"st={r.get('status')} ct={r.get('content_type')} len={len(b)} body={t[:800]}"
import sys as _s
def log(m):
    _s.stderr.write(m+"\n"); _s.stderr.flush()
paths=["/","/token","/session","/login","/profile","/secret","/flag","/admin","/show","/cookie"]
for p in paths:
    r=http("GET",p)
    log(f"GET {p} => {body_text(r)}")
log("DONE_RECON")
print("CLAIM:{\"secret_hex\": \"00\"}", flush=True)