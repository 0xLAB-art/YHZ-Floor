import sys, json, base64, time
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
ct_hex="890ed6b8106221edcf98d9fb95faa866c51840045b4431a5a922da2289333d72b3e38463c56f4dc45e4c5b7d4c813bf698b8db959247a582f6beebf24bd75cbe28a239755a1cc5e600eed4aa9f27c10a"
iv_hex="dc03e26b8c8ea0f11e2420d44fa1ed47"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
prevs=[iv]+blocks[:-1]
# last block is full PKCS7 padding 0x10*16, intermediate known, no oracle needed
# verify: pt_last = 16*chr(16), inter_last = pt_last xor prev_last
nblocks=len(blocks)
inter_list=[None]*nblocks
pt_list=[None]*nblocks
# compute last block intermediate directly
prev_last=prevs[-1]
pt_last=bytes([16])*16
inter_last=bytes(a^b for a,b in zip(pt_last,prev_last))
inter_list[-1]=inter_last
pt_list[-1]=pt_last
def ask(fprev,targ):
    q=base64.b64encode(fprev+targ).decode()
    print(json.dumps({"q": q}), flush=True)
    line=sys.stdin.readline()
    if not line:
        raise RuntimeError("EOF from oracle")
    return bool(json.loads(line).get("pad_ok"))
def recover(targ):
    inter=bytearray(16)
    forged=bytearray(16)
    for p in range(15,-1,-1):
        pad=16-p
        for j in range(p+1,16):
            forged[j]=inter[j]^pad
        hit=None
        for g in range(256):
            forged[p]=g
            ok=ask(bytes(forged),targ)
            if ok:
                if pad==1:
                    s=forged[14]
                    forged[14]=s^1
                    ok2=ask(bytes(forged),targ)
                    forged[14]=s
                    if not ok2:
                        continue
                hit=g
                break
        if hit is None:
            raise RuntimeError("no hit")
        inter[p]=hit^pad
    return bytes(inter)
t0=time.monotonic_ns()
for idx in range(nblocks-1):
    inter_list[idx]=recover(blocks[idx])
    pt_list[idx]=bytes(a^b for a,b in zip(inter_list[idx],prevs[idx]))
pt_full=b"".join(pt_list)
# strip padding
c=pt_full[-1]
if 1<=c<=16 and pt_full[-c:]==bytes([c])*c:
    pt_out=pt_full[:-c]
else:
    pt_out=pt_full
t1=time.monotonic_ns()
print(f"OPSPAN_NS:{t1-t0}", flush=True)
print("CLAIM:"+json.dumps({"plaintext_hex": pt_out.hex()}), flush=True)