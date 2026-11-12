import sys, json, base64
def req(method, path, body=None, headers=None, body_hex=None):
    o={"http":{"method":method,"path":path}}
    if body is not None:
        o["http"]["body"]=body
    if body_hex is not None:
        o["http"]["body_hex"]=body_hex
    if headers is not None:
        o["http"]["headers"]=headers
    print(json.dumps(o), flush=True)
    line=sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception as e:
        return {"_raw":line[:2000],"_err":str(e)}
def bt(r):
    try:
        b=base64.b64decode(r.get("body_b64",""))
        return b
    except Exception as e:
        return b"ERR:"+str(e).encode()
paths=["/","/robots.txt","/source","/app","/index","/home","/login","/admin","/console","/debug"]
outs=[]
for p in paths:
    try:
        r=req("GET",p)
        if r is None:
            outs.append(f"{p} => NO REPLY")
            continue
        st=r.get("status")
        ct=r.get("content_type")
        b=bt(r)
        try:
            t=b.decode(errors='replace')
        except:
            t=repr(b[:2000])
        outs.append(f"{p} => status={st} ct={ct} len={len(b)} body_snip={t[:3000]!r}")
    except Exception as e:
        outs.append(f"{p} EXC {e}")
for line in outs:
    sys.stderr.write(line+"\n")
    sys.stderr.flush()
    print("DEBUG:"+line[:2000], flush=True)
# no claim, just recon
sys.stderr.write("RECON_DONE\n")