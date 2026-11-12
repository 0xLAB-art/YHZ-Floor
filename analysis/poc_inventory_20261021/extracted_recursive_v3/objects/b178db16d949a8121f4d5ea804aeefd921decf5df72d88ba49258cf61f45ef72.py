import sys, json, base64, time
ct_hex="890ed6b8106221edcf98d9fb95faa866c51840045b4431a5a922da2289333d72b3e38463c56f4dc45e4c5b7d4c813bf698b8db959247a582f6beebf24bd75cbe28a239755a1cc5e600eed4aa9f27c10a"
iv_hex="dc03e26b8c8ea0f11e2420d44fa1ed47"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
prevs=[iv]+blocks[:-1]
NB=len(blocks)
# last block is full 0x10 padding -> intermediate known, skip oracle
pt_last=bytes([16])*16
inter_last=bytes(a^b for a,b in zip(pt_last,prevs[-1]))
inters=[None]*NB
pts=[None]*NB
inters[-1]=inter_last
pts[-1]=pt_last
def ask(fprev,targ):
    b=base64.b64encode(fprev+targ).decode()
    sys.stdout.write('{"q":"'+b+'"}\n')
    sys.stdout.flush()
    line=sys.stdin.readline()
    if not line:
        raise RuntimeError("oracle EOF")
    o=json.loads(line)
    return bool(o.get("pad_ok"))
def recover(targ):
    inter=bytearray(16)
    forged=bytearray(16)
    for pos in range(15,-1,-1):
        pad=16-pos
        for j in range(pos+1,16):
            forged[j]=inter[j]^pad
        hit=None
        for g in range(256):
            forged[pos]=g
            if ask(bytes(forged),targ):
                if pad==1:
                    s=forged[14]
                    forged[14]=s^1
                    try:
                        ok2=ask(bytes(forged),targ)
                    except Exception:
                        ok2=False
                    forged[14]=s
                    if not ok2:
                        continue
                hit=g
                break
        if hit is None:
            raise RuntimeError("no hit")
        inter[pos]=hit^pad
    return bytes(inter)
t0=time.monotonic_ns()
for idx in range(NB-1):
    inters[idx]=recover(blocks[idx])
    pts[idx]=bytes(a^b for a,b in zip(inters[idx],prevs[idx]))
    print("blk "+str(idx)+" "+pts[idx].hex(), file=sys.stderr, flush=True)
pt_full=b"".join(pts)
c=pt_full[-1]
if 1<=c<=16 and pt_full[-c:]==bytes([c])*c:
    out=pt_full[:-c]
else:
    out=pt_full
t1=time.monotonic_ns()
sys.stdout.write("OPSPAN_NS:"+str(t1-t0)+"\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex":out.hex()},separators=(",",":"))+"\n")
sys.stdout.flush()