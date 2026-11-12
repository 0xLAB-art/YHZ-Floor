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
        return {"status":-1,"raw":line}
    try:
        r=json.loads(line)
    except Exception as e:
        return {"status":-1,"raw":line,"err":str(e)}
    return r
def show(name, r):
    try:
        b64=r.get("body_b64","")
        body=base64.b64decode(b64).decode("utf-8",errors="replace") if b64 else ""
    except Exception as e:
        body="<b64decode err %s>"%e
    sys.stderr.write(f"=== {name} ===\nstatus={r.get('status')} ct={r.get('content_type')} bodylen={len(body)}\n{body[:4000]}\n---rawkeys:{list(r.keys())}---\nraw:{json.dumps(r)[:2000]}\n")
    sys.stderr.flush()
    return body
import sys as _s
prov=_s.argv[1] if len(_s.argv)>1 else ""
sys.stderr.write("PROV:"+prov[:2000]+"\n")
paths=["/","/login","/admin","/secret","/robots.txt","/api","/api/login","/api/admin","/admin/","/static","/help","/openapi.json","/swagger.json"]
for p in paths:
    r=http("GET",p)
    show("GET "+p,r)
# try POST login variants
for b in ['{"username":"admin","password":"admin"}','{"user":"admin"}','username=admin&password=admin', '{"username":"guest","password":"guest"}']:
    r=http("POST","/login",body=b,headers={"Content-Type":"application/json"})
    show("POST /login "+b[:40],r)
    r2=http("POST","/api/login",body=b,headers={"Content-Type":"application/json"})
    show("POST /api/login "+b[:40],r2)
# try admin with no auth
r=http("GET","/admin")
show("GET /admin again",r)
sys.stdout.write('CLAIM:{"secret_hex": "00"}\n')
sys.stdout.flush()