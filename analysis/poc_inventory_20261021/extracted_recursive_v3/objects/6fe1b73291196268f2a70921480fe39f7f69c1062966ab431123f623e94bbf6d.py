import sys, json, base64
def req(method, path, body=None, body_hex=None, headers=None):
    o={"http":{"method":method,"path":path}}
    if body is not None: o["http"]["body"]=body
    if body_hex is not None: o["http"]["body_hex"]=body_hex
    if headers is not None: o["http"]["headers"]=headers
    sys.stdout.write(json.dumps(o)+"\n"); sys.stdout.flush()
    line=sys.stdin.readline()
    if not line: return {"error":"eof"}
    try: return json.loads(line)
    except: return {"raw":line}
def b64d(s):
    try: return base64.b64decode(s)
    except: return b""
print("ARGV:"+sys.argv[1] if len(sys.argv)>1 else "NOARGV", flush=True)
paths=["/","/index","/index.html","/login","/register","/profile","/user","/admin","/secret","/flag","/encrypt","/decrypt","/oracle","/api","/session","/token","/cookie","/show","/dashboard","/home","/main","/info","/help","/api/secret","/api/profile","/.well-known","/robots.txt"]
for p in paths:
    try:
        r=req("GET",p)
        st=r.get("status")
        ct=r.get("content_type")
        bb=r.get("body_b64","")
        data=b64d(bb)
        txt=data[:2000]
        try: t=txt.decode(errors="replace")
        except: t=repr(txt)
        # escape newlines for single line logging
        t=t.replace("\n","\\n")[:2000]
        print(f"RESP GET {p} status={st} ct={ct} len={len(data)} body={t}", flush=True)
    except Exception as e:
        print(f"ERR {p} {e}", flush=True)
print('CLAIM:{"secret_hex": "00"}', flush=True)