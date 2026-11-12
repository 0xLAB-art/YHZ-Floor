import sys, base64, json, time
ct_hex="4b2ff72d7721031091971902885b53193a58542190a6f93029b2e35679f01db219e161692af616757a1767d6a8cb7fcc2e0c988e2165507e7828dab156638d521709815c75c271d3f1def04d2b477a83"
iv_hex="dc75eae15207780e53cde356c98596d7"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
prevs=[iv]+blocks[:-1]
def oracle(fp,tgt):
 sys.stdout.write('{"q":"'+base64.b64encode(fp+tgt).decode()+'"}\n')
 sys.stdout.flush()
 line=sys.stdin.readline()
 while line and line.strip()=="":
  line=sys.stdin.readline()
 j=json.loads(line)
 return bool(j.get("pad_ok",j.get("padOk",False)))
def dec_block(tgt):
 inter=bytearray(16)
 forged=bytearray(16)
 for k in range(1,17):
  pos=16-k
  for j in range(pos+1,16):
   forged[j]=inter[j]^k
  for g in range(256):
   forged[pos]=g
   if oracle(bytes(forged),tgt):
    if k==1:
     forged[14]^=1
     ok2=oracle(bytes(forged),tgt)
     forged[14]^=1
     if not ok2:
      continue
    inter[pos]=g^k
    break
 return bytes(inter)
t0=time.monotonic_ns()
n=len(blocks)
pts=[None]*n
pts[n-1]=bytes([16])*16
for idx in range(n-1):
 inter=dec_block(blocks[idx])
 pts[idx]=bytes(a^b for a,b in zip(inter,prevs[idx]))
t1=time.monotonic_ns()
full=b"".join(pts)
pad=full[-1]
if 1<=pad<=16 and full[-pad:]==bytes([pad])*pad:
 full=full[:-pad]
sys.stdout.write("OPSPAN_NS:%d\n" % (t1-t0))
sys.stdout.flush()
sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex":full.hex()})+"\n")
sys.stdout.flush()