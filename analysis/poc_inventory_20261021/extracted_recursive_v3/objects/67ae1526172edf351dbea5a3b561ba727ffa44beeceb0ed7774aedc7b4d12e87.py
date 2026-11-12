import sys, json, base64, time
ct_hex="830ee7d8ada9c7826ebdd3fa0e095b0f716fdd797940fc7b581c518774fbe2b3d324b530d00f10781483dd65a96c607ab67405ea2b663f31137a22bc5f0a1080dd47eff9ed9380307dca9ed708415bfd"
iv_hex="379cffbb64432feba08c262ebae3dcfa"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
n=len(ct)//16
prev_blocks=[iv]+[ct[i*16:(i+1)*16] for i in range(n)]
targets=[ct[i*16:(i+1)*16] for i in range(n)]
def query(fp,tgt):
    s=base64.b64encode(fp+tgt).decode()
    print(json.dumps({"q":s}),flush=True)
    while True:
        line=sys.stdin.readline()
        if not line:
            raise EOFError("oracle EOF")
        line=line.strip()
        if not line:
            continue
        try:
            o=json.loads(line)
        except Exception:
            continue
        if "pad_ok" in o:
            return bool(o["pad_ok"])
        continue
def recover(tgt):
    inter=[0]*16
    forged=[0]*16
    for k in range(15,-1,-1):
        pad=16-k
        for j in range(k+1,16):
            forged[j]=inter[j]^pad
        found=False
        for g in range(256):
            forged[k]=g
            if query(bytes(forged),tgt):
                if k==15:
                    ver=bytes(forged[:14]+[forged[14]^0x01,forged[15]])
                    if query(ver,tgt):
                        inter[k]=g^pad
                        found=True
                        break
                    else:
                        continue
                else:
                    inter[k]=g^pad
                    found=True
                    break
        if not found:
            raise RuntimeError(f"no guess at pos {k}")
    return bytes(inter)
t0=time.monotonic_ns()
plain_blocks=[]
for idx,tgt in enumerate(targets):
    inter=recover(tgt)
    prev=prev_blocks[idx]
    pt=bytes(inter[j]^prev[j] for j in range(16))
    plain_blocks.append(pt)
t1=time.monotonic_ns()
padded=b"".join(plain_blocks)
# strip PKCS7 if valid
try:
    l=padded[-1]
    if 1<=l<=16 and padded[-l:]==bytes([l])*l:
        unpadded=padded[:-l]
    else:
        unpadded=padded
 except Exception:
    unpadded=padded
print(f"OPSPAN_NS:{t1-t0}",flush=True)
print(f"CLAIM:{json.dumps({'plaintext_hex':unpadded.hex()})}",flush=True)