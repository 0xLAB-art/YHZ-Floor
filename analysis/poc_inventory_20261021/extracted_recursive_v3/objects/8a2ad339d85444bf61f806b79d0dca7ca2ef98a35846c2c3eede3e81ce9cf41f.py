import os, sys, json, base64, select, socket, time
ct_hex="0f3aef70198362f9a3603480f7e11b85771e419a9e5831ad4431557f75b7882ec6a77ac14a11688540b6378aebb4f429abf379283d7250f9cf52524c903e8471093ddb097f6bbe023b41740c90dbb4f2"
iv_hex="9fe33b554fa7ce8d7abe63247508bc91"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
# low-level unbuffered query helpers
def raw_write_line(s):
    data=(s+"\n").encode()
    os.write(1,data)
    try:
        sys.stderr.write("W:"+s[:60]+"\n"); sys.stderr.flush()
    except: pass
def raw_readline_timeout(timeout=30):
    buf=b""
    end=time.monotonic()+timeout
    while True:
        rem=end-time.monotonic()
        if rem<=0:
            return None
        r,_,_=select.select([0],[],[],rem)
        if not r:
            return None
        try:
            chunk=os.read(0,4096)
        except Exception:
            return None
        if not chunk:
            # EOF
            if buf:
                return buf.decode(errors="ignore")
            return "EOF"
        buf+=chunk
        if b"\n" in buf:
            line,rest=buf.split(b"\n",1)
            # push back rest? store in global
            leftover.append(rest)
            return line.decode(errors="ignore")
leftover=[]
def stdin_query(fprev,tgt,timeout=30):
    b64=base64.b64encode(fprev+tgt).decode()
    raw_write_line(json.dumps({"q":b64}))
    # check leftover first
    if leftover:
        data=leftover.pop(0)
        if data:
            # if leftover contains newline, split
            if b"\n" in data:
                l,r=data.split(b"\n",1)
                leftover.append(r)
                data=l
            try:
                obj=json.loads(data.decode(errors="ignore").strip())
                if "pad_ok" in obj:
                    return bool(obj["pad_ok"])
            except: pass
    line=raw_readline_timeout(timeout)
    if line is None or line=="EOF":
        raise EOFError("stdin timeout/eof: %r"%line)
    line=line.strip()
    if not line:
        line=raw_readline_timeout(timeout)
        if line is None: raise EOFError("second timeout")
        line=line.strip()
    obj=json.loads(line)
    return bool(obj.get("pad_ok"))
# try socket fallback
def try_socket_oracle():
    import socket as sk
    for port in [14840]:
        try:
            s=sk.create_connection(("127.0.0.1",port),timeout=5)
            s.settimeout(10)
            f=s.makefile("rwb",buffering=0)
            # probe
            probe=b"\x00"*16+blocks[0]
            b64=base64.b64encode(probe).decode()
            f.write((json.dumps({"q":b64})+"\n").encode())
            resp=f.readline()
            sys.stderr.write("sock resp: %r\n"%resp)
            sys.stderr.flush()
            if resp:
                obj=json.loads(resp.decode(errors="ignore").strip())
                if "pad_ok" in obj:
                    return s,f
            s.close()
        except Exception as e:
            try: sys.stderr.write("sock fail %r\n"%e)
            except: pass
            try: sys.stderr.flush()
            except: pass
            continue
    return None,None
# decide transport: test stdin with short timeout first
use_sock=False
sock=None
sfile=None
# quick stdin probe with 15s timeout
try:
    probe_ok=stdin_query(b"\x00"*16,blocks[0],timeout=15)
    sys.stderr.write("stdin probe ok=%r\n"%probe_ok); sys.stderr.flush()
    # stdin works, define oracle as stdin_query
    def oracle(fprev,tgt):
        return stdin_query(fprev,tgt,timeout=60)
except Exception as e:
    try: sys.stderr.write("stdin probe fail %r, trying socket\n"%e); sys.stderr.flush()
    except: pass
    sock,sfile=try_socket_oracle()
    if sfile is not None:
        use_sock=True
        sys.stderr.write("using socket\n"); sys.stderr.flush()
        def oracle(fprev,tgt):
            b64=base64.b64encode(fprev+tgt).decode()
            sfile.write((json.dumps({"q":b64})+"\n").encode())
            resp=sfile.readline()
            if not resp: raise EOFError("sock eof")
            obj=json.loads(resp.decode(errors="ignore").strip())
            return bool(obj.get("pad_ok"))
    else:
        # retry stdin with longer timeout as last resort (maybe slow verifier)
        sys.stderr.write("socket failed, retry stdin long\n"); sys.stderr.flush()
        def oracle(fprev,tgt):
            return stdin_query(fprev,tgt,timeout=120)
# now Vaudenay decrypt first 4 blocks (5th is 0x10 padding)
t0=time.monotonic_ns()
targets=blocks[:4]
prevs=[iv]+blocks[:3]
intermediates=[]
for ti,tgt in enumerate(targets):
    I=bytearray(16)
    F=bytearray(16)
    for pos in range(15,-1,-1):
        pad=16-pos
        for k in range(pos+1,16): F[k]=I[k]^pad
        hit=None
        for g in range(256):
            F[pos]=g
            ok=oracle(bytes(F),tgt)
            if ok:
                if pad==1:
                    F2=bytearray(F); F2[14]^=0x01
                    # need direct transport call to avoid closure issues
                    try:
                        if use_sock:
                            b64=base64.b64encode(bytes(F2)+tgt).decode()
                            sfile.write((json.dumps({"q":b64})+"\n").encode())
                            resp=sfile.readline()
                            ok2=json.loads(resp.decode(errors="ignore").strip()).get("pad_ok")
                            ok2=bool(ok2)
                        else:
                            ok2=stdin_query(bytes(F2),tgt,timeout=60)
                    except Exception:
                        continue
                    if not ok2: continue
                hit=g
                break
        if hit is None:
            raise Exception("fail block %d pos %d"%(ti,pos))
        I[pos]=hit^pad
    intermediates.append(bytes(I))
    try: sys.stderr.write("block %d done %s\n"%(ti,bytes(I).hex())); sys.stderr.flush()
    except: pass
pt=b""
for ib,cb in zip(intermediates,prevs):
    pt+=bytes(a^b for a,b in zip(ib,cb))
t1=time.monotonic_ns()
try: os.write(1,("OPSPAN_NS:%d\n"%(t1-t0)).encode())
except: pass
try: os.write(1,("CLAIM:"+json.dumps({"plaintext_hex":pt.hex()})+"\n").encode())
except: print("CLAIM:"+json.dumps({"plaintext_hex":pt.hex()}),flush=True)