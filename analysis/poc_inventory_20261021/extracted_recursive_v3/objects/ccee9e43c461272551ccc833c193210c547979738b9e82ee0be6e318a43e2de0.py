import sys,json,base64,time
ct_hex='6cdb521065a2d535a390481697fcc9db8a8e2106935cbf4affc40283c504271503f5d43bccf2d334e9ac46d23ea2ca7c4f1c55a67ca797e8b5c7d154da9205d41cc6f3d1eebfc255af1b5b0c00d438af'
iv_hex='ad6fb3f9bf75126ea6dee124484370b8'
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
cts=[ct[i:i+16] for i in range(0,len(ct),16)]
prev_list=[iv]+cts[:-1]
targets=cts
def oracle(fp,tg):
 q=base64.b64encode(fp+tg).decode()
 sys.stdout.write(json.dumps({'q':q})+'\n')
 sys.stdout.flush()
 line=sys.stdin.readline()
 if not line:
  raise Exception('no reply')
 return json.loads(line).get('pad_ok') is True
def dec_block(tg):
 inter=bytearray(16)
 craft=bytearray(16)
 for pad in range(1,17):
  pos=16-pad
  for k in range(pos+1,16):
   craft[k]=inter[k]^pad
  found=False
  for g in range(256):
   craft[pos]=g
   if oracle(bytes(craft),tg):
    if pad==1:
     craft[14]^=1
     ok2=oracle(bytes(craft),tg)
     craft[14]^=1
     if not ok2:
      continue
    inter[pos]=g^pad
    found=True
    break
  if not found:
   raise Exception('fail pad')
 return bytes(inter)
t0=time.monotonic_ns()
plain=b''
for idx,tg in enumerate(targets):
 D=dec_block(tg)
 P=bytes(a^b for a,b in zip(D,prev_list[idx]))
 plain+=P
t1=time.monotonic_ns()
sys.stdout.write('OPSPAN_NS:'+str(t1-t0)+'\n')
sys.stdout.flush()
sys.stdout.write('CLAIM:'+json.dumps({'plaintext_hex':plain.hex()})+'\n')
sys.stdout.flush()