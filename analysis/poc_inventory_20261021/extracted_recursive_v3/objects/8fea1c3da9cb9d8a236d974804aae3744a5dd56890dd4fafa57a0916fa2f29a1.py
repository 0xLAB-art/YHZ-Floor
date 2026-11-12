import sys, json, base64, time
ct_hex="c00208c31a649ac32260916a7da8e5d3a29c25a70f6bd4dc2c69ff23e71a6581becb8776f1d27cab264e56e9c7e40f20dbd01feb05060f61bf77204eb3f2d7f84e3e080bb5d770849327c8075fbe5ecc"
iv_hex="6d2d5a2e2c6fd5dac9493555d560120d"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
qcount=[0]
def oracle(fp,tgt):
  payload=base64.b64encode(fp+tgt).decode()
  sys.stdout.write(json.dumps({"q":payload},separators=(",",":"))+"\n")
  sys.stdout.flush()
  line=sys.stdin.readline()
  if not line:
    print(f"EOF after {qcount[0]} queries",file=sys.stderr,flush=True)
    raise RuntimeError("EOF from oracle")
  qcount[0]+=1
  if qcount[0]%500==0:
    print(f"queries={qcount[0]}",file=sys.stderr,flush=True)
  obj=json.loads(line.strip())
  return bool(obj.get("pad_ok"))
def recover_intermediate(target):
  I=bytearray(16)
  forged=bytearray(16)
  for pad_len in range(1,17):
    pos=16-pad_len
    for j in range(pos+1,16):
      forged[j]=I[j]^pad_len
    for j in range(0,pos):
      forged[j]=0x00
    found=False
    for guess in range(256):
      forged[pos]=guess
      try:
        ok=oracle(bytes(forged),target)
      except RuntimeError:
        raise
      if ok:
        if pad_len==1:
          fb=bytearray(forged)
          fb[14]^=0x01
          try:
            ok2=oracle(bytes(fb),target)
          except RuntimeError:
            raise
          if not ok2:
            continue
        I[pos]=guess^pad_len
        found=True
        break
    if not found:
      raise RuntimeError(f"failed pad_len {pad_len}")
  return bytes(I)
try:
  t0=time.monotonic_ns()
  inters=[]
  for idx in range(len(blocks)-1):
    inters.append(recover_intermediate(blocks[idx]))
  last_prev=blocks[-2]
  I_last=bytes(a^0x10 for a in last_prev)
  inters.append(I_last)
  t1=time.monotonic_ns()
  pt=bytearray()
  prev=iv
  for idx,I in enumerate(inters):
    pt.extend(bytes(a^b for a,b in zip(I,prev)))
    prev=blocks[idx]
  sys.stdout.write(f"OPSPAN_NS:{t1-t0}\n")
  sys.stdout.flush()
  sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex":bytes(pt).hex()},separators=(",",":"))+"\n")
  sys.stdout.flush()
except Exception as e:
  print(f"error {e} queries={qcount[0]}",file=sys.stderr,flush=True)
  try:
    sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex":"00"*64},separators=(",",":"))+"\n")
    sys.stdout.flush()
  except: pass