import sys, json, base64, time, os
ct_hex="e3099e94621290bdf325a922fede651c954ee1216dc94364b73ec124a88b47256be3f007a315bbe5b6913bb9c149c298bf61266d7302d31ae20eedf38cb6c749bf4ff0d0cba713eca0d571d51bb2f3e7"
iv_hex="16a5d06ec579fb053ed4fceeadaba7bc"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
prevs=[iv]+blocks[:-1]
def oracle(fp,tgt):
  b=base64.b64encode(fp+tgt).decode()
  msg=json.dumps({"q":b},separators=(",", ":"))
  sys.stdout.write(msg+"\n")
  sys.stdout.flush()
  line=sys.stdin.readline()
  if not line:
    time.sleep(0.2)
    line=sys.stdin.readline()
  if not line:
    raise RuntimeError("no reply eof")
  return json.loads(line).get("pad_ok") is True
def dec_block(tgt):
  I=bytearray(16)
  F=bytearray(16)
  for k in range(1,17):
    pos=16-k
    for j in range(pos+1,16):
      F[j]=I[j]^k
    for g in range(256):
      F[pos]=g
      try:
        ok=oracle(bytes(F),tgt)
      except RuntimeError as e:
        print("oracle err "+str(e),file=sys.stderr,flush=True)
        raise
      if not ok:
        continue
      if k==1:
        F2=bytearray(F)
        F2[14]^=1
        ok2=oracle(bytes(F2),tgt)
        if not ok2:
          continue
      I[pos]=g^k
      break
    else:
      raise RuntimeError("byte fail")
  return bytes(I)
t0=time.monotonic_ns()
pt=b""
for idx,tgt in enumerate(blocks):
  print("blk %d"%idx,file=sys.stderr,flush=True)
  I=dec_block(tgt)
  print("I%d=%s"%(idx,I.hex()),file=sys.stderr,flush=True)
  pt+=bytes(a^b for a,b in zip(I,prevs[idx]))
t1=time.monotonic_ns()
print("pt="+pt.hex(),file=sys.stderr,flush=True)
pad=pt[-1]
if 1<=pad<=16 and pt[-pad:]==bytes([pad])*pad:
  out=pt[:-pad]
else:
  out=pt
sys.stdout.write("OPSPAN_NS:%d\n"%(t1-t0))
sys.stdout.flush()
sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex":out.hex()},separators=(",", ":"))+"\n")
sys.stdout.flush()