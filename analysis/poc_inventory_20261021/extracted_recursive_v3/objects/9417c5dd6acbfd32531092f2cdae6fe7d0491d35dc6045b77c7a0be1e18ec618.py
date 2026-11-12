import sys, json, base64
def req(method, path, body=None, headers=None, body_hex=None):
    o={"http":{"method":method,"path":path}}
    if body is not None:
        o["http"]["body"]=body
    if body_hex is not None:
        o["http"]["body_hex"]=body_hex
    if headers is not None:
        o["http"]["headers"]=headers
    sys.stdout.write(json.dumps(o)+"\n")
    sys.stdout.flush()
    line=sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)
def bd(r):
    try:
        return base64.b64decode(r.get("body_b64",""))
    except:
        return b""
def tstr(b):
    try:
        return b.decode(errors="replace")
    except:
        return repr(b)
def log(s):
    sys.stderr.write(s+"\n")
    sys.stderr.flush()
paths=["/","/api","/api/","/api/v1","/v1","/openapi.json","/swagger.json","/swagger","/docs","/redoc","/openapi","/.well-known","/health","/healthz","/status","/ping","/version","/hello","/hi","/greet","/greeting","/echo","/test","/demo","/render","/template","/templates","/view","/page","/show","/display","/preview","/markdown","/md","/hello-world","/jinja","/ssti","/pickle","/unpickle","/deserialize","/deserialize/","/api/deserialize","/api/pickle","/api/render","/api/template","/api/hello","/api/echo","/api/eval","/api/exec","/api/run","/api/search","/api/query","/api/user","/api/profile","/api/view","/api/preview","/search","/query","/user","/profile","/calc","/eval","/exec","/run","/cmd","/execute","/load","/loads","/decode","/encode","/session","/cookie","/login","/register","/submit","/form","/input","/output","/data","/fetch","/url","/proxy","/upload","/download","/file","/files","/read","/include","/main","/app","/home","/welcome","/index.html","/greet/"]
found=[]
for p in paths:
    try:
        r=req("GET",p)
        if r is None:
            log(f"{p} NOREPLY")
            continue
        st=r.get("status")
        b=bd(r)
        t=tstr(b)
        snip=t[:500].replace("\n","\\n")
        log(f"GET {p} => {st} len={len(b)} {snip[:400]}")
        if st!=404:
            found.append((p,st,snip,t))
    except Exception as e:
        log(f"GET {p} EXC {e}")
log(f"FOUND_NON404: {found}")
# probe POST on same paths with empty json
for p in paths[:40]:
    try:
        r=req("POST",p,'{}',{"Content-Type":"application/json"})
        if r is None:
            continue
        st=r.get("status")
        b=bd(r)
        t=tstr(b)
        snip=t[:500].replace("\n","\\n")
        if st!=404:
            log(f"POST {p} => {st} len={len(b)} {snip[:400]}")
    except Exception as e:
        log(f"POST {p} EXC {e}")
# SSTI query-param probe on any found + common /
probe_payloads=["{{7*7}}","${7*7}","#{7*7}","*{7*7}"]
test_paths = [p for p,_s,_sn,_t in found] + ["/hello","/greet","/hi","/echo","/render","/template","/view","/page","/show","/preview","/search","/index","/"]
uniq=[]
for x in test_paths:
    if x not in uniq:
        uniq.append(x)
for base in uniq:
    for pl in ["{{7*7}}","{{7*'7'}}"]:
        for q in [f"?name={pl}",f"?input={pl}",f"?template={pl}",f"?q={pl}",f"?username={pl}",f"?msg={pl}",f"?text={pl}",f"?content={pl}",f"?title={pl}",f"?data={pl}"]:
            import urllib.parse as up
            enc=up.quote(pl,safe="")
            qq=q.replace(pl,enc)
            try:
                r=req("GET",base+qq)
                if r is None:
                    continue
                b=bd(r); t=tstr(b)
                if "49" in t or "7777777" in t or "49" in b.decode(errors="ignore"):
                    log(f"SSTI? GET {base+qq} => {r.get('status')} body={t[:800]}")
            except Exception as e:
                log(f"SSTI probe exc {e}")
    # break early to save time? continue
log("RECON2_DONE")