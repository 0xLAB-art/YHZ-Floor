import sys, json, base64, time
ct_hex='c5a9f76cdf6d777cf8270c08b230696fe4a7c46ad244182061b8e29639c835339f90e9c0cd01ccff1e5f384a2f2a606a8b73736bee8cf80fb6c239602f0e751bd6a841c5d4779f5f4f747a65bb711e0a'
iv_hex='efd6f1db6c0c2623f75f8d4b586b4c16'
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
prevs=[iv]+blocks[:-1]
qcount=[0]
def oracle_q(fprev,targ):
    payload=base64.b64encode(fprev+targ).decode()
    sys.stdout.write(json.dumps({"q":payload})+"\n")
    sys.stdout.flush()
    while True:
        line=sys.stdin.readline()
        if line is None or line=='':
            print('WARN empty stdin read, waiting',file=sys.stderr,flush=True)
            time.sleep(0.05)
            continue
        line=line.strip()
        if line=='':
            continue
        try:
            obj=json.loads(line)
        except Exception as e:
            print(f'WARN bad json {line!r} {e}',file=sys.stderr,flush=True)
            continue
        if 'pad_ok' not in obj:
            print(f'WARN no pad_ok {line!r}',file=sys.stderr,flush=True)
            continue
        qcount[0]+=1
        return bool(obj.get('pad_ok'))
t0=time.monotonic_ns()
rec=bytearray()
for bi in range(len(blocks)):
    targ=blocks[bi]
    inter=bytearray(16)
    forged=bytearray(16)
    for i in range(15,-1,-1):
        pad=16-i
        for j in range(i+1,16):
            forged[j]=inter[j]^pad
        found=None
        for g in range(256):
            forged[i]=g
            ok=oracle_q(bytes(forged),targ)
            if ok:
                if pad==1:
                    chk=bytearray(forged)
                    chk[14]^=1
                    sys.stdout.write(json.dumps({"q":base64.b64encode(bytes(chk)+targ).decode()})+"\n")
                    sys.stdout.flush()
                    line2=sys.stdin.readline()
                    while line2 is not None and line2.strip()=='' :
                        line2=sys.stdin.readline()
                    try:
                        ok2=json.loads(line2.strip()).get('pad_ok')
                    except Exception:
                        ok2=False
                    qcount[0]+=1
                    if not ok2:
                        continue
                found=g
                break
        if found is None:
            print(f'FAIL block {bi} pos {i}',file=sys.stderr,flush=True)
            raise SystemExit(1)
        inter[i]=found^pad
    prev=prevs[bi]
    pb=bytes(inter[k]^prev[k] for k in range(16))
    rec.extend(pb)
    print(f'BLOCK {bi} done {pb.hex()} queries={qcount[0]}',file=sys.stderr,flush=True)
t1=time.monotonic_ns()
print('OPSPAN_NS:'+str(t1-t0),flush=True)
print('CLAIM:'+json.dumps({"plaintext_hex":rec.hex()}),flush=True)