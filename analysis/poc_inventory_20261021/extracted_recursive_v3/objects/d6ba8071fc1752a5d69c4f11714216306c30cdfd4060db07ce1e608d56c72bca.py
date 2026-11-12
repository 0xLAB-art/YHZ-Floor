import sys, json, base64
def req(method, path, headers=None, body=None, body_hex=None):
    o={"http":{"method":method,"path":path}}
    if headers: o["http"]["headers"]=headers
    if body is not None: o["http"]["body"]=body
    if body_hex is not None: o["http"]["body_hex"]=body_hex
    print(json.dumps(o), flush=True)
    line=sys.stdin.readline()
    r=json.loads(line)
    bd=base64.b64decode(r.get("body_b64",""))
    return r.get("status"), bd, r.get("content_type","")
paths=["/","/login","/admin","/admin/","/secret","/api/secret","/help","/robots.txt"]
outs=[]
for p in paths:
    try:
        s,b,c=req("GET",p)
        try: t=b[:2000].decode(errors='replace')
        except: t=repr(b[:500])
        outs.append(f"{p} -> {s} {c} :: {t[:1500]}")
    except Exception as e:
        outs.append(f"{p} ERR {e}")
        break
print(json.dumps({"debug":outs})[:3000])
print("CLAIM:{\"secret_hex\": \"00\"}", flush=True)