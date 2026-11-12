import sys, json, base64, time, os, select
ct_hex="c00208c31a649ac32260916a7da8e5d3a29c25a70f6bd4dc2c69ff23e71a6581becb8776f1d27cab264e56e9c7e40f20dbd01feb05060f61bf77204eb3f2d7f84e3e080bb5d770849327c8075fbe5ecc"
iv_hex="6d2d5a2e2c6fd5dac9493555d560120d"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
fd_in=0
_buf=b""
last_dur_ns=[0]
qcount=[0]
def _read_line(timeout):
    global _buf
    end=time.monotonic()+timeout
    while True:
        nl=_buf.find(b"\n")
        if nl>=0:
            line=_buf[:nl]
            _buf=_buf[nl+1:]
            if line.strip()==b"":
                continue
            return line.decode()
        rem=end-time.monotonic()
        if rem<=0:
            raise TimeoutError("oracle read timeout")
        r,_,_=select.select([fd_in],[],[],min(1.0,rem))
        if r:
            try:
                chunk=os.read(fd_in,8192)
            except BlockingIOError:
                continue
            if not chunk:
                time.sleep(0.02)
                continue
            _buf+=chunk
        continue
def oracle(forged_prev,target,timeout=30):
    payload=base64.b64encode(forged_prev+target).decode()
    msg=json.dumps({"q": payload})+"\n"
    os.write(1,msg.encode())
    t0=time.monotonic_ns()
    line=_read_line(timeout)
    t1=time.monotonic_ns()
    last_dur_ns[0]=t1-t0
    qcount[0]+=1
    if qcount[0]%200==0:
        os.write(2,f"queries={qcount[0]}\n".encode())
    obj=json.loads(line.strip())
    return bool(obj.get("pad_ok"))
def recover_intermediate(target,first_timeout=60):
    I=bytearray(16)
    forged=bytearray(16)
    for pad_len in range(1,17):
        pos=16-pad_len
        for j in range(pos+1,16):
            forged[j]=I[j]^pad_len
        for j in range(0,pos):
            forged[j]=0x00
        to=first_timeout if (pad_len==1 and qcount[0]<5) else 30
        found=False
        for guess in range(256):
            forged[pos]=guess
            ok=oracle(bytes(forged),target,timeout=to)
            if ok:
                if pad_len==1:
                    fb=bytearray(forged)
                    fb[14]^=0x01
                    ok2=oracle(bytes(fb),target,timeout=30)
                    if not ok2:
                        continue
                I[pos]=guess^pad_len
                found=True
                break
        if not found:
            raise RuntimeError(f"no guess pad {pad_len}")
    return bytes(I)
inters=[]
for idx in range(4):
    inters.append(recover_intermediate(blocks[idx]))
I_last=bytes(a^0x10 for a in blocks[3])
inters.append(I_last)
pt=bytearray()
prev=iv
for idx,I in enumerate(inters):
    pt.extend(bytes(a^b for a,b in zip(I,prev)))
    prev=blocks[idx]
pt=bytes(pt)
os.write(1,f"OPSPAN_NS:{last_dur_ns[0]}\n".encode())
os.write(1,("CLAIM:"+json.dumps({"plaintext_hex": pt.hex()})+"\n").encode())