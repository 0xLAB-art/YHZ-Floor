import sys, json, base64, time
sys.stdout.reconfigure(line_buffering=True)
ct_hex="0f3aef70198362f9a3603480f7e11b85771e419a9e5831ad4431557f75b7882ec6a77ac14a11688540b6378aebb4f429abf379283d7250f9cf52524c903e8471093ddb097f6bbe023b41740c90dbb4f2"
iv_hex="9fe33b554fa7ce8d7abe63247508bc91"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
# decrypt first 4 blocks only (last block is pure padding 0x10*16 since P is 64 bytes)
targets=blocks[:4]
prevs=[iv]+blocks[:3]
qcount=0
def query(fprev,tgt):
    global qcount
    b64=base64.b64encode(fprev+tgt).decode()
    print(json.dumps({"q": b64}), flush=True)
    qcount+=1
    line=sys.stdin.readline()
    if not line:
        raise EOFError("oracle EOF after %d queries" % qcount)
    obj=json.loads(line.strip())
    return bool(obj.get("pad_ok"))
# sanity: one test query with valid padding (should usually be False for random)
intermediates=[]
for tgt in targets:
    I=bytearray(16)
    F=bytearray(16)
    for pos in range(15,-1,-1):
        pad=16-pos
        for k in range(pos+1,16):
            F[k]=I[k]^pad
        for g in range(256):
            F[pos]=g
            ok=query(bytes(F),tgt)
            if ok:
                if pad==1:
                    F2=bytearray(F); F2[14]^=0x01
                    ok2=query(bytes(F2),tgt)
                    if not ok2:
                        continue
                break
        else:
            raise Exception("no valid byte")
        I[pos]=F[pos]^pad
    intermediates.append(bytes(I))
pt=b""
for ib,cb in zip(intermediates,prevs):
    pt+=bytes(a^b for a,b in zip(ib,cb))
print("CLAIM:"+json.dumps({"plaintext_hex": pt.hex()}), flush=True)