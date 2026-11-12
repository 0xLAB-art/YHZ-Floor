import sys, json, base64, time
ct_hex="392750a7b194e926466e13d6362442c4ed5b392786311b3e57b53ef4ed03b32f342b76fab1f0ad78da07bcf7cfb6bf405cf249920d0bb07758aa64cc7c0bc8ad16eda8d9cfe01e444c03c7cf07e0a639"
iv_hex="a136e502325c6154fa1676e6c24ec51c"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[iv]+[ct[i:i+16] for i in range(0,len(ct),16)]
last_ns=[0]

def oracle_q(forged_prev,target):
    t0=time.monotonic_ns()
    payload=bytes(forged_prev)+bytes(target)
    s=base64.b64encode(payload).decode()
    print(json.dumps({"q": s}),flush=True)
    line=sys.stdin.readline()
    last_ns[0]=time.monotonic_ns()-t0
    while line is not None and line.strip()=="":
        line=sys.stdin.readline()
    if not line:
        raise RuntimeError("oracle EOF")
    o=json.loads(line)
    return bool(o.get("pad_ok"))

def decrypt_block(target):
    inter=bytearray(16)
    forged=bytearray(16)
    for pad_len in range(1,17):
        pos=16-pad_len
        for k in range(pos+1,16):
            forged[k]=inter[k]^pad_len
        for k in range(pos):
            forged[k]=0
        found=False
        for g in range(256):
            forged[pos]=g
            try:
                ok=oracle_q(forged,target)
            except RuntimeError:
                raise
            if ok:
                if pad_len==1:
                    saved=forged[14]
                    forged[14]^=1
                    ok2=oracle_q(forged,target)
                    forged[14]=saved
                    if not ok2:
                        continue
                inter[pos]=g^pad_len
                found=True
                break
        if not found:
            raise RuntimeError("no valid byte")
    return bytes(inter)

pts=[]
for idx in range(1,len(blocks)):
    inter=decrypt_block(blocks[idx])
    prev=blocks[idx-1]
    pts.append(bytes(inter[i]^prev[i] for i in range(16)))
full=b"".join(pts)
pad=full[-1]
if 1<=pad<=16 and full[-pad:]==bytes([pad])*pad:
    out=full[:-pad]
else:
    out=full
print("OPSPAN_NS:"+str(last_ns[0]),flush=True)
print("CLAIM:"+json.dumps({"plaintext_hex": out.hex()}),flush=True)