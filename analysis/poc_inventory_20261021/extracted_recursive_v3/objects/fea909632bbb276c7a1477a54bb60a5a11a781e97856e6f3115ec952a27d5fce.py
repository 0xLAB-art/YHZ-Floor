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
        return {"_raw":line, "_err":str(e)}
    return r
def dec(r):
    if r is None:
        return "NORESP"
    if "_raw" in r:
        return str(r)
    b64=r.get("body_b64","")
    try:
        b=base64.b64decode(b64)
    except Exception as e:
        return f"status={r.get('status')} b64err={e} raw={r}"
    try:
        t=b.decode()
    except:
        t=repr(b[:2000])
    headers=str(r.get("content_type",""))
    return f"status={r.get('status')} ctype={headers} len={len(b)} body={t[:3000]}"
outs=[]
paths=["/","/help","/api","/api/help","/encrypt","/decrypt","/login","/profile","/secret","/flag","/admin","/show","/token","/cookie","/session","/oracle","/ecb","/docs","/openapi.json","/robots.txt"]
for p in paths:
    r=http("GET",p)
    outs.append(f"GET {p} => {dec(r)}")
# try POST variants
for p in ["/encrypt","/login","/token","/session","/oracle"]:
    r=http("POST",p,body=json.dumps({"user":"test"}),headers={"Content-Type":"application/json"})
    outs.append(f"POST {p} test => {dec(r)}")
# dump all
sys.stderr.write("\n".join(outs)+"\n")
print("PROBE_DUMP_START")
for o in outs:
    print(o)
print("PROBE_DUMP_END")
print("CLAIM:{\"secret_hex\": \"00\"}", flush=True)