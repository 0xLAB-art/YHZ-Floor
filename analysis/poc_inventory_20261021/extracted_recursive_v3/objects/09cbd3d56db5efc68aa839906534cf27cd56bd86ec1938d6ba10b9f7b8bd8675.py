import sys, json, base64, time
ct_hex="0bc75d95fe2fe3b9e1feb1f0055ac54707d97e2ee7047ab2231c99989c87863fcb38a303735eabe45f290daca391e12a9835b119fc67aeff84f2132119c894d87ce3ab47ea5ea6f8661ee21e525f97db"
iv_hex="b7b3bb5d750f25a72ea603313b243455"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i*16:(i+1)*16] for i in range(len(ct)//16)]
prevs=[iv]+blocks[:-1]
qcount=[0]
def oracle_q(forged_prev,target):
  data=forged_prev+target
  b64=base64.b64encode(data).decode('ascii')
  line=json.dumps({"q":b64},separators=(',',':'))
  sys.stdout.write(line+"\n")
  sys.stdout.flush()
  resp=sys.stdin.readline()
  if not resp:
    print(f"EOF after query #{qcount[0]} len={len(data)}",file=sys.stderr,flush=True)
    raise RuntimeError("EOF from oracle")
  qcount[0]+=1
  try:
    obj=json.loads(resp)
  except Exception as e:
    print(f"bad reply: {resp!r} err={e}",file=sys.stderr,flush=True)
    raise
  return bool(obj.get("pad_ok",False))
inters=[]
t0=time.monotonic_ns()
for bi in range(len(blocks)):
  target=blocks[bi]
  inter=bytearray(16)
  forged=bytearray(16)
  for pad_len in range(1,17):
    for k in range(1,pad_len):
      forged[16-k]=inter[16-k]^pad_len
    pos=16-pad_len
    found=None
    for guess in range(256):
      forged[pos]=guess
      ok=oracle_q(bytes(forged),target)
      if ok:
        if pad_len==1:
          fb2=bytearray(forged)
          fb2[14]^=1
          ok2=oracle_q(bytes(fb2),target)
          if ok2:
            found=guess
            break
          else:
            continue
        else:
          found=guess
          break
    if found is None:
      print(f"block {bi} pad {pad_len} not found",file=sys.stderr,flush=True)
      raise RuntimeError("byte not found")
    inter[pos]=found^pad_len
  inters.append(bytes(inter))
  print(f"block {bi} done inter={inters[-1].hex()}",file=sys.stderr,flush=True)
t1=time.monotonic_ns()
pt=b''.join(bytes(inters[i][j]^prevs[i][j] for j in range(16)) for i in range(len(blocks)))
pl=pt[-1]
if 1<=pl<=16 and pt[-pl:]==bytes([pl])*pl:
  pt_unpadded=pt[:-pl]
else:
  pt_unpadded=pt
claim=json.dumps({"plaintext_hex":pt_unpadded.hex()},separators=(',',':'))
sys.stdout.write("OPSPAN_NS:"+str(t1-t0)+"\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:"+claim+"\n")
sys.stdout.flush()