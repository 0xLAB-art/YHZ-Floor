import sys
import json
import base64
import time
import select
ct_hex='6ec59a3da460be879c121d4645164ab9baf55839546451f26a5029fe28ea8bc99c0559be9d4bfdb6c9d1cd6cf731359aee1f9347530e39d2ec064a3c0e951d54cc622dc350f25f02e594e1a320412870'
iv_hex='2df9046dfe1791d1a4199c280ffc3601'
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[iv]
for i in range(0,len(ct),16):
  blocks.append(ct[i:i+16])
def ask(fp,tgt):
  payload=base64.b64encode(fp+tgt).decode()
  msg=json.dumps({'q':payload})+chr(10)
  sys.stdout.write(msg)
  sys.stdout.flush()
  rlist,_,_=select.select([sys.stdin],[],[],5.0)
  if rlist:
    line=sys.stdin.readline()
    if not line:
      return None
    try:
      obj=json.loads(line)
      v=obj.get('pad_ok')
      if v is True:
        return True
      if v is False:
        return False
      return bool(v)
    except:
      return None
  return None
def oracle(fp,tgt):
  for _ in range(5):
    r=ask(fp,tgt)
    if r is not None:
      return r
    time.sleep(0.2)
  raise RuntimeError('oracle timeout')
def recover(tgt):
  inter=bytearray(16)
  forged=bytearray(16)
  for pad in range(1,17):
    pos=16-pad
    for k in range(pos+1,16):
      forged[k]=inter[k]^pad
    found=False
    for g in range(256):
      forged[pos]=g
      r=oracle(bytes(forged),tgt)
      if r:
        if pad==1 and pos>0:
          fb2=bytearray(forged)
          fb2[pos-1]^=1
          r2=oracle(bytes(fb2),tgt)
          if not r2:
            continue
        inter[pos]=g^pad
        found=True
        break
    if not found:
      raise RuntimeError('nofind')
  return bytes(inter)
t0=time.monotonic_ns()
pts=[]
for idx in [1,2,3,4]:
  im=recover(blocks[idx])
  prev=blocks[idx-1]
  pt=bytes([a^b for a,b in zip(im,prev)])
  pts.append(pt)
t1=time.monotonic_ns()
padded=b''.join(pts)
out_hex=padded.hex()
sys.stdout.write('OPSPAN_NS:'+str(t1-t0)+chr(10))
sys.stdout.flush()
sys.stdout.write('CLAIM:'+json.dumps({'plaintext_hex':out_hex})+chr(10))
sys.stdout.flush()