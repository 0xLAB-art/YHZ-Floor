import sys, json, base64, time
try:
 sys.stdout.reconfigure(line_buffering=True)
except: pass
ct_hex='392750a7b194e926466e13d6362442c4ed5b392786311b3e57b53ef4ed03b32f342b76fab1f0ad78da07bcf7cfb6bf405cf249920d0bb07758aa64cc7c0bc8ad16eda8d9cfe01e444c03c7cf07e0a639'
iv_hex='a136e502325c6154fa1676e6c24ec51c'
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[iv]+[ct[i:i+16] for i in range(0,len(ct),16)]
last_ns=[0]
def ask(fprev,targ):
 t0=time.monotonic_ns()
 b=base64.b64encode(bytes(fprev)+bytes(targ)).decode()
 print('{"q":"'+b+'"}',flush=True)
 line=sys.stdin.readline()
 last_ns[0]=time.monotonic_ns()-t0
 if not line:
  raise RuntimeError('eof')
 return ('true' in line.lower())
def dec(targ):
 inter=bytearray(16)
 f=bytearray(16)
 for plen in range(1,17):
  pos=16-plen
  for k in range(pos+1,16):
   f[k]=inter[k]^plen
  for k in range(pos):
   f[k]=0
  found=False
  for g in range(256):
   f[pos]=g
   if ask(f,targ):
    if plen==1:
     sv=f[14]
     f[14]^=1
     ok2=ask(f,targ)
     f[14]=sv
     if not ok2:
      continue
    inter[pos]=g^plen
    found=True
    break
  if not found:
   raise RuntimeError('nobyte')
 return bytes(inter)
pts=[]
for idx in [1,2,3,4]:
 it=dec(blocks[idx])
 pv=blocks[idx-1]
 pts.append(bytes(it[i]^pv[i] for i in range(16)))
full=b''.join(pts)
print('OPSPAN_NS:'+str(last_ns[0]),flush=True)
print('CLAIM:'+json.dumps({'plaintext_hex':full.hex()}),flush=True)