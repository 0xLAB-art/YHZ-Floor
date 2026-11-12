import sys, json, base64, time
ct_hex="7feffb7fe9f6adced12896d47a5fc8eaa2a51219aa331713634f22ecc40c6a35112d4733fe30d96588df29a587c89e64d72be382807e144d1ecc2761a99c4f65b626077b5bb7caaa93183335d5f5d7fc"
iv_hex="b3b8aa9275f2f1dac764b728d15a1f1f"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i*16:(i+1)*16] for i in range(len(ct)//16)]
def oracle(forged_prev,target):
  raw=bytes(forged_prev)+bytes(target)
  q=base64.b64encode(raw).decode()
  sys.stdout.write(json.dumps({"q":q})+"\n")
  sys.stdout.flush()
  line=sys.stdin.readline()
  if not line:
    raise RuntimeError("eof-no-reply")
  return json.loads(line).get("pad_ok") is True
def dec_block(target):
  inter=bytearray(16)
  for k in range(15,-1,-1):
    pad=16-k
    found=None
    for g in range(256):
      forged=bytearray(16)
      for j in range(k+1,16):
        forged[j]=inter[j]^pad
      forged[k]=g
      if oracle(forged,target):
        if pad==1:
          chk=bytearray(forged)
          chk[14]^=1
          if not oracle(chk,target):
            continue
        found=g
        break
    if found is None:
      raise RuntimeError("no-byte")
    inter[k]=found^pad
  return bytes(inter)
inters=[]
t0=time.monotonic_ns()
for t in blocks:
  inters.append(dec_block(t))
t1=time.monotonic_ns()
plain=bytearray()
for i,t in enumerate(blocks):
  prev=iv if i==0 else blocks[i-1]
  plain.extend(bytes(a^b for a,b in zip(inters[i],prev)))
sys.stdout.write("OPSPAN_NS:"+str(t1-t0)+"\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex":bytes(plain).hex()})+"\n")
sys.stdout.flush()