import sys, json, base64, time, os, select
try:
  sys.stdout.reconfigure(line_buffering=True)
except Exception as e:
  print(f"reconf fail {e}", file=sys.stderr, flush=True)
ct_hex="0bc75d95fe2fe3b9e1feb1f0055ac54707d97e2ee7047ab2231c99989c87863fcb38a303735eabe45f290daca391e12a9835b119fc67aeff84f2132119c894d87ce3ab47ea5ea6f8661ee21e525f97db"
iv_hex="b7b3bb5d750f25a72ea603313b243455"
print(f"ENV_KEYS={sorted(os.environ.keys())}", file=sys.stderr, flush=True)
print(f"ARGV={sys.argv}", file=sys.stderr, flush=True)
try:
  print(f"CWD={os.getcwd()} TMP={os.listdir('/tmp')[:50]}", file=sys.stderr, flush=True)
except Exception as e:
  print(f"listdir fail {e}", file=sys.stderr, flush=True)
try:
  print(f"stdin isatty={sys.stdin.isatty()} stdout isatty={sys.stdout.isatty()}", file=sys.stderr, flush=True)
except Exception as e:
  print(f"isatty fail {e}", file=sys.stderr, flush=True)
# check stdin readable before query (non-blocking, 1s timeout)
try:
  r,_,_=select.select([sys.stdin],[],[],1.0)
  print(f"select-before-query readable={bool(r)}", file=sys.stderr, flush=True)
  if r:
    import fcntl
    print("stdin has pending data, peeking", file=sys.stderr, flush=True)
except Exception as e:
  print(f"select fail {e}", file=sys.stderr, flush=True)
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i*16:(i+1)*16] for i in range(len(ct)//16)]
prevs=[iv]+blocks[:-1]
print(f"nblocks={len(blocks)} ct_len={len(ct)}", file=sys.stderr, flush=True)
qcount=[0]
def oracle_q(fprev,targ):
  data=fprev+targ
  b64=base64.b64encode(data).decode('ascii')
  msg=json.dumps({"q": b64})
  # low-level write + flush to maximise relay compatibility
  sys.stdout.write(msg+"\n")
  sys.stdout.flush()
  try:
    os.fsync(sys.stdout.fileno())
  except Exception:
    pass
  print(f"Q#{qcount[0]} sent len={len(data)} b64={b64[:16]}... waiting", file=sys.stderr, flush=True)
  # wait with select timeout 10s so we can log instead of hanging
  try:
    r,_,_=select.select([sys.stdin],[],[],10.0)
  except Exception as e:
    print(f"select-wait fail {e}", file=sys.stderr, flush=True)
    r=[]
  if not r:
    print(f"Q#{qcount[0]} TIMEOUT no data on stdin", file=sys.stderr, flush=True)
    # blocking read attempt once
  resp=sys.stdin.readline()
  print(f"Q#{qcount[0]} raw reply={resp!r}", file=sys.stderr, flush=True)
  if not resp:
    raise RuntimeError("EOF from oracle")
  obj=json.loads(resp)
  qcount[0]+=1
  return bool(obj.get("pad_ok", False))
# quick single test query before full attack
try:
  test_forged=bytes(16)
  test_ok=oracle_q(test_forged, blocks[0])
  print(f"TEST query pad_ok={test_ok}", file=sys.stderr, flush=True)
except Exception as e:
  print(f"TEST query failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
  import traceback; traceback.print_exc(file=sys.stderr)
  sys.stderr.flush()
  # still try to continue to full attack? stdin EOF so will fail; emit dummy claim to get verdict
  # Do not exit yet; fall through to full attack attempt which will also log
inters=[]
t0=time.monotonic_ns()
try:
  # skip block 0 byte cracking if test already consumed? No, restart cleanly.
  # Full Vaudenay
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
    print(f"BLOCK {bi} inter={inters[-1].hex()}", file=sys.stderr, flush=True)
  t1=time.monotonic_ns()
  pt=b''.join(bytes(inters[i][j]^prevs[i][j] for j in range(16)) for i in range(len(blocks)))
  print(f"PT padded hex={pt.hex()}", file=sys.stderr, flush=True)
  pl=pt[-1]
  if 1<=pl<=16 and pt[-pl:]==bytes([pl])*pl:
    pt_up=pt[:-pl]
  else:
    pt_up=pt
  claim=json.dumps({"plaintext_hex": pt_up.hex()})
  sys.stdout.write("OPSPAN_NS:"+str(t1-t0)+"\n"); sys.stdout.flush()
  sys.stdout.write("CLAIM:"+claim+"\n"); sys.stdout.flush()
except Exception as e:
  print(f"ATTACK EXC {type(e).__name__}: {e}", file=sys.stderr, flush=True)
  import traceback; traceback.print_exc(file=sys.stderr); sys.stderr.flush()
  # emit best-effort claim if we got partial blocks, else dummy to close run
  try:
    if inters and len(inters)==len(blocks):
      raise e
    # dummy claim (will fail but ensures CLAIM line present)
    sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex": "00"*64})+"\n"); sys.stdout.flush()
  except Exception:
    pass