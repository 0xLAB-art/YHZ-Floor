import os, sys, json, base64, time
ct_hex="4d990f713daecefb2c4903086fe0fff719a639e6e3d8f8bf43e3b8ec0e5cf4466bc2ab9753c2d2e6760791a5df802e316c7f677cbc2adf6135f91b0ba68298ab37d076f68629e1ba1fca8ee3e64b148a"
iv_hex="ea5130a66a4e3d81a66fdc5a83d956f5"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
prevs=[iv]+blocks[:-1]
try:
 sys.stdout.flush()
except: pass
_rbuf=b""
def _readline():
 global _rbuf
 while b"\n" not in _rbuf:
  chunk=os.read(0,4096)
  if not chunk:
   raise RuntimeError("EOF stdin")
  _rbuf+=chunk
 idx=_rbuf.index(b"\n")
 line=_rbuf[:idx+1]
 _rbuf=_rbuf[idx+1:]
 return line.decode()
def query(fp,tgt):
 pay=bytes(fp)+bytes(tgt)
 s=base64.b64encode(pay).decode()
 msg=json.dumps({"q": s})+"\n"
 os.write(1,msg.encode())
 while True:
  line=_readline()
  if not line.strip():
   continue
  try:
   j=json.loads(line)
  except:
   continue
  if "pad_ok" in j:
   return bool(j["pad_ok"])
   
def recover(tgt):
 I=bytearray(16)
 F=bytearray(16)
 for pos in range(15,-1,-1):
  n=16-pos
  for j in range(pos+1,16):
   F[j]=I[j]^n
  found=False
  for g in range(256):
   F[pos]=g
   ok=query(F,tgt)
   if ok:
    if n==1:
     sv=F[14]
     F[14]=sv^1
     ok2=query(F,tgt)
     F[14]=sv
     if not ok2:
      continue
    I[pos]=g^n
    found=True
    break
  if not found:
   raise RuntimeError("no guess")
 return bytes(I)
t0=time.monotonic_ns()
pt=b""
for idx,tgt in enumerate(blocks):
 Im=recover(tgt)
 pt+=bytes(a^b for a,b in zip(Im,prevs[idx]))
t1=time.monotonic_ns()
pl=pt[-1]
if 1<=pl<=16 and pt[-pl:]==bytes([pl])*pl:
 pt_out=pt[:-pl]
else:
 pt_out=pt
os.write(1,f"OPSPAN_NS:{t1-t0}\n".encode())
os.write(1,("CLAIM:"+json.dumps({"plaintext_hex":pt_out.hex()})+"\n").encode())