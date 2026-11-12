import sys,json,base64,time
ct_hex="4b243d54cf34c7536f17198d96afad3d1422509f96297766e141cb86ddab166476838b2ac8ff3c556284e1b1546eceada6da5afd9b95eecc4bda57c93067f324ca8ecdfdd5d84a3afa0d1cce3ab7d4b6"
iv_hex="7297416ab13274f28a4f3298675178c3"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blks=[iv]+[ct[i:i+16] for i in range(0,len(ct),16)]
def qfunc(a,b):
 p=base64.b64encode(a+b).decode()
 s=json.dumps({"q":p},separators=(',',':'))
 print(s,flush=True)
 l=sys.stdin.readline()
 if not l:
  raise RuntimeError('eof')
 return bool(json.loads(l).get('pad_ok'))
def rec(tgt):
 D=[0]*16
 for k in range(15,-1,-1):
  pad=16-k
  for b in range(256):
   f=bytearray(16)
   for j in range(k+1,16):
    f[j]=D[j]^pad
   f[k]=b
   if qfunc(bytes(f),tgt):
    if k==15:
     f2=bytearray(f)
     f2[14]^=1
     p2=base64.b64encode(bytes(f2)+tgt).decode()
     print(json.dumps({"q":p2},separators=(',',':')),flush=True)
     l=sys.stdin.readline()
     if not l:
      raise RuntimeError('eof2')
     if not bool(json.loads(l).get('pad_ok')):
      continue
    D[k]=b^pad
    break
  else:
   raise RuntimeError('fail')
 return bytes(D)
t0=time.monotonic_ns()
out=b''
for idx in range(1,5):
 tgt=blks[idx]
 prv=blks[idx-1]
 D=rec(tgt)
 out+=bytes(x^y for x,y in zip(D,prv))
t1=time.monotonic_ns()
print('OPSPAN_NS:'+str(t1-t0),flush=True)
print('CLAIM:'+json.dumps({"plaintext_hex":out.hex()},separators=(',',':')),flush=True)