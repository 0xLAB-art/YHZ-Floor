import sys,json,hashlib,base64,re,select
def rl(t):
    r,_,_=select.select([sys.stdin],[],[],t)
    return sys.stdin.readline() if r else ""
def http(m,p,b=None,h=None,bh=None,t=3.0):
    d={"http":{"method":m,"path":p}}
    if h:d["http"]["headers"]=h
    if b is not None:d["http"]["body"]=b
    if bh is not None:d["http"]["body_hex"]=bh
    try:
        sys.stdout.write(json.dumps(d)+"\n");sys.stdout.flush()
    except Exception:
        return None
    l=rl(t)
    if not l:return None
    try:r=json.loads(l)
    except Exception:return None
    s=""
    v=r.get("body_b64")
    if isinstance(v,str):
        try:s=base64.b64decode(v).decode("utf-8","replace")
        except Exception:s=""
    r["_text"]=s
    return r
prov={}
for a in sys.argv[1:]:
    try:
        j=json.loads(a)
        if isinstance(j,dict):prov.update(j)
    except Exception:pass
if not prov:
    try:prov=json.loads(sys.stdin.readline() or "{}")
    except Exception:prov={}
p=int(prov.get("dh_p_hex") or "0",16)
g=int(prov.get("dh_g_hex") or "0",16) or 2
Y=int(prov.get("server_pub_hex") or "0",16)
R=re.compile(r"(?:diffie-hellman|ecdh|curve25519|ssh-rsa)[A-Za-z0-9._-]*",re.I)
found=[]
def scan(r):
    if not r:return
    low=[x.lower() for x in found]
    for x in R.findall(r.get("_text","")):
        if x.lower() not in low:low.append(x.lower());found.append(x)
off=["diffie-hellman-group1-sha1","diffie-hellman-group14-sha1","diffie-hellman-group-exchange-sha1","diffie-hellman-group-exchange-sha256"]
qh=",".join(off)
alive=http("GET","/",t=4.0)
if alive is not None:
    scan(alive)
    for pth in ["/kex","/negotiate","/ssh/kex","/api/kex","/handshake","/offer","/ssh","/api/negotiate","/session","/transcript","/info","/version","/help","/algo","/algos","/status","/demo","/weak"]:
        for u in [pth,pth+"?algos="+qh.replace(",","%2C"),pth+"?kex="+off[0]]:
            scan(http("GET",u,h={"X-Client-Kex-Algos":qh,"X-Offered-Kex":off[0]},t=3.0))
    for pth in ["/negotiate","/kex","/handshake"]:
        scan(http("POST",pth,b=json.dumps({"kex_algos":off,"client_kex_algos":off}),h={"Content-Type":"application/json"},t=3.0))
def pick(names):
    if not names:return "diffie-hellman-group1-sha1"
    low=[n.lower() for n in names]
    for pref in ["diffie-hellman-group1-sha1","diffie-hellman-group-exchange-sha1","diffie-hellman-group-exchange-sha256","diffie-hellman-group14-sha1"]:
        if pref in low:return names[low.index(pref)]
    for n in low:
        if "group1" in n:return names[low.index(n)]
    for n in low:
        if "sha1" in n:return names[low.index(n)]
    return names[0]
algo=pick(found)
w=len(prov.get("dh_p_hex",""))
y=int(hashlib.sha256(b"acts-weak-dh-client").hexdigest(),16)%(p-1)
cp=sh=0
for _ in range(128):
    if y<2:y+=2
    cp=pow(g,y,p);sh=pow(Y,y,p)
    if (not w) or (len(format(cp,"x"))==w and len(format(sh,"x"))==w):break
    y=(y+0x9E3779B97F4A7C15)%(p-1)
proof=hashlib.sha256((algo+format(sh,"x")).encode()).hexdigest()
print("CLAIM:"+json.dumps({"proof_hex":proof,"kex_algo":algo,"client_pub_hex":format(cp,"x")}))