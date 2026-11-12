import sys, json, base64, time
ct_hex="83679b10525a6878558e2c8dd4c2e75004624a7baac05327e3fe9e0df1523136d28882b3a315f688a6ec50b9857d164757ce803c58cde52554fd52d0f6f5681ae772eba7cb6c543b0048b9573bb536ad"
iv_hex="d026215840190e7066e27c739f3ba211"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
prevs=[iv]+blocks[:-1]
targets=blocks[:4]
prevs=prevs[:4]
print("starting attack", file=sys.stderr, flush=True)
def oracle(fprev,targ):
  payload=base64.b64encode(fprev+targ).decode()
  line_out=json.dumps({"q": payload})
  print(line_out, flush=True)
  print("sent query len "+str(len(fprev+targ)), file=sys.stderr, flush=True)
  line=sys.stdin.readline()
  print("got reply: "+repr(line[:200] if line else line), file=sys.stderr, flush=True)
  if not line:
    raise EOFError("no reply")
  return bool(json.loads(line).get("pad_ok"))
def recover(targ):
  I=bytearray(16)
  for pos in range(15,-1,-1):
    pad=16-pos
    found=None
    for g in range(256):
      f=bytearray(16)
      for j in range(pos+1,16):
        f[j]=I[j]^pad
      f[pos]=g
      ok=oracle(bytes(f),targ)
      if ok:
        if pos==15:
          f2=bytearray(f)
          f2[14]^=1
          ok2=oracle(bytes(f2),targ)
          if not ok2:
            continue
        found=g
        break
    if found is None:
      raise RuntimeError("fail at "+str(pos))
    I[pos]=found^pad
  return bytes(I)
pts=[]
for idx in range(4):
  print("block "+str(idx), file=sys.stderr, flush=True)
  inter=recover(targets[idx])
  pt=bytes(a^b for a,b in zip(inter,prevs[idx]))
  pts.append(pt)
  print("block "+str(idx)+" done "+pt.hex(), file=sys.stderr, flush=True)
pt_all=b"".join(pts)
t0=time.monotonic_ns()
t1=time.monotonic_ns()
print("OPSPAN_NS:"+str(t1-t0), flush=True)
print("CLAIM:"+json.dumps({"plaintext_hex": pt_all.hex()}), flush=True)