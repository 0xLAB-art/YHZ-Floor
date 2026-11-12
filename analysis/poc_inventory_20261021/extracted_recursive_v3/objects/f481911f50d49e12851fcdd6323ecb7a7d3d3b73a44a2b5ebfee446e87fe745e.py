import sys, json, base64, time, os
try:
  sys.stdout.reconfigure(line_buffering=True)
except Exception:
  pass
ct_hex="0bc75d95fe2fe3b9e1feb1f0055ac54707d97e2ee7047ab2231c99989c87863fcb38a303735eabe45f290daca391e12a9835b119fc67aeff84f2132119c894d87ce3ab47ea5ea6f8661ee21e525f97db"
iv_hex="b7b3bb5d750f25a72ea603313b243455"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
print(f"ct_len={len(ct)} iv_len={len(iv)}",file=sys.stderr,flush=True)
blocks=[ct[i*16:(i+1)*16] for i in range(len(ct)//16)]
prevs=[iv]+blocks[:-1]
print(f"nblocks={len(blocks)}",file=sys.stderr,flush=True)
def oracle_q(fprev,targ):
  data=fprev+targ
  b64=base64.b64encode(data).decode('ascii')
  msg=json.dumps({"q":b64})
  print(f"SEND len={len(data)} b64len={len(b64)} msglen={len(msg)}",file=sys.stderr,flush=True)
  print(msg,flush=True)
  print("waiting reply...",file=sys.stderr,flush=True)
  resp=sys.stdin.readline()
  print(f"RECV raw={resp!r}",file=sys.stderr,flush=True)
  if not resp:
    raise RuntimeError("EOF waiting oracle")
  obj=json.loads(resp)
  return bool(obj.get("pad_ok",False))
inters=[]
t0=time.monotonic_ns()
try:
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
            fb2=bytearray(forged); fb2[14]^=1
            ok2=oracle_q(bytes(fb2),target)
            if ok2:
              found=guess; break
            else:
              continue
          else:
            found=guess; break
      if found is None:
        raise RuntimeError(f"byte not found bi={bi} pad={pad_len}")
      inter[pos]=found^pad_len
    inters.append(bytes(inter))
    print(f"block {bi} inter={inters[-1].hex()}",file=sys.stderr,flush=True)
  t1=time.monotonic_ns()
  pt=b''.join(bytes(inters[i][j]^prevs[i][j] for j in range(16)) for i in range(len(blocks)))
  print(f"pt_hex={pt.hex()}",file=sys.stderr,flush=True)
  pl=pt[-1]
  if 1<=pl<=16 and pt[-pl:]==bytes([pl])*pl:
    pt=pt[:-pl]
  claim=json.dumps({"plaintext_hex":pt.hex()})
  print("OPSPAN_NS:"+str(t1-t0),flush=True)
  print("CLAIM:"+claim,flush=True)
except Exception as e:
  print(f"EXC {type(e).__name__}: {e}",file=sys.stderr,flush=True)
  import traceback; traceback.print_exc(file=sys.stderr); sys.stderr.flush()
  raise