import sys, json, base64
def http(method, path, body=None, body_hex=None, headers=None):
    req={"http":{"method":method,"path":path}}
    if body is not None:
        req["http"]["body"]=body
    if body_hex is not None:
        req["http"]["body_hex"]=body_hex
    if headers is not None:
        req["http"]["headers"]=headers
    sys.stdout.write(json.dumps(req)+"\n")
    sys.stdout.flush()
    line=sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)
def txt(r):
    try:
        return base64.b64decode(r.get("body_b64","")).decode(errors="replace")
    except Exception as e:
        return "<derr>"
def log(*a):
    print(*a, file=sys.stderr, flush=True)
paths=["/","/health","/healthz","/api","/api/health","/render","/template","/ssti","/greet","/hello","/hi","/echo","/eval","/exec","/cmd","/run","/shell","/ping","/deserialize","/pickle","/unpickle","/yaml","/load","/loads","/parse","/preview","/view","/profile","/user","/search","/query","/test","/debug","/console","/admin","/login","/session","/cookie","/api/render","/api/eval","/api/exec","/api/deserialize","/api/pickle","/api/yaml","/api/parse","/api/search","/api/greet","/api/hello","/api/template","/actuator","/env","/secret","/flag","/robots.txt","/openapi.json"]
found=[]
for p in paths:
    try:
        r=http("GET",p)
        if r is None:
            log("NONE "+p)
            continue
        s=r.get("status")
        b=txt(r)
        if s!=404:
            log("HIT GET "+p+" status="+str(s)+" ct="+str(r.get("content_type"))+" body="+b[:3000])
            found.append(p)
        else:
            if len(b)>60 or b.strip()!='{"error": "not found"}' and b.strip()!='{"error":"not found"}':
                log("404-diff "+p+" body="+b[:500])
    except Exception as e:
        log("ERR "+p+" "+str(e))
log("FOUND GET: "+json.dumps(found))
# probe POST on all found + common POST targets
targets=list(set(found+["/render","/template","/greet","/hello","/eval","/exec","/deserialize","/pickle","/api/deserialize","/api/render","/api/eval","/search","/view","/preview","/api/search"]))
for t in targets:
    for m in ["POST","PUT"]:
        try:
            r=http(m,t,body=json.dumps({"input":"probe"}),headers={"Content-Type":"application/json"})
            if r is None: continue
            b=txt(r)
            log(m+" "+t+" json status="+str(r.get("status"))+" body="+b[:2000])
        except Exception as e:
            log("ERR "+m+t+str(e))
# also try POST form to same targets
for t in targets[:12]:
    try:
        r=http("POST",t,body="name=test",headers={"Content-Type":"application/x-www-form-urlencoded"})
        log("POSTFORM "+t+" status="+str(r.get("status"))+" body="+txt(r)[:2000])
    except Exception as e:
        log("ERRF "+t+str(e))
print("CLAIM:"+json.dumps({"secret_hex":"00"}))