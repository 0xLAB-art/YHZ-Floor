import sys, json, base64, re
def log(*a):
    print(' '.join(str(x) for x in a), file=sys.stderr, flush=True)
    
def do_req(method, path, body=None, body_hex=None, headers=None):
    obj={"http":{"method":method,"path":path}}
    if body is not None:
        obj["http"]["body"]=body
    if body_hex is not None:
        obj["http"]["body_hex"]=body_hex
    if headers is not None:
        obj["http"]["headers"]=headers
    sys.stdout.write(json.dumps(obj)+"\n")
    sys.stdout.flush()
    line=sys.stdin.readline()
    if not line:
        return None
    try:
        resp=json.loads(line)
    except Exception as e:
        log("bad reply:", line[:500])
        return None
    b64=resp.get("body_b64","")
    try:
        raw=base64.b64decode(b64) if b64 else b""
    except:
        raw=b""
    return {"status":resp.get("status"),"raw":raw,"text":raw.decode(errors="ignore"),"ct":resp.get("content_type",""),"resp":resp}

prov=sys.argv[1] if len(sys.argv)>1 else "{}"
log("prov:", prov[:2000])
gets=["/","/openapi.json","/docs","/api/openapi.json","/swagger.json","/api/docs","/robots.txt","/secret","/admin","/flag","/profile","/me","/session","/token"]
for p in gets:
    try:
        r=do_req("GET", p)
        if r is None:
            log("GET",p,"=> NONE")
        else:
            log("GET",p,"=>",r["status"],"ct=",r["ct"],"len=",len(r["raw"]))
            log(r["text"][:3000])
    except Exception as e:
        log("err GET",p,e)
# try openapi parse
try:
    r=do_req("GET","/openapi.json")
    if r and r["text"].strip().startswith("{"):
        try:
            j=json.loads(r["text"])
            log("openapi paths:", list(j.get("paths",{}).keys())[:50])
        except Exception as e:
            log("openapi parse fail",e)
except Exception as e:
    log(e)
posts=["/register","/login","/encrypt","/decrypt","/profile","/session","/token","/create","/user","/encode","/oracle","/encrypt_token","/get-token","/api/register","/api/login","/api/encrypt"]
bodies=['{"username":"test123"}','{"user":"test123"}','{"username":"AAAAAAAAAAAAAAAA"}','{"username":"admin"}']
for p in posts:
    for b in bodies[:2]:
        try:
            r=do_req("POST",p,body=b,headers={"Content-Type":"application/json"})
            if r is None:
                log("POST",p,b[:20],"=> NONE")
            else:
                log("POST",p,b[:30],"=>",r["status"],"len=",len(r["raw"]))
                log(r["text"][:3000])
        except Exception as e:
            log("err POST",p,e)
    # break early to limit requests? continue
log("recon done")
print('CLAIM:{"secret_hex":"00"}', flush=True)