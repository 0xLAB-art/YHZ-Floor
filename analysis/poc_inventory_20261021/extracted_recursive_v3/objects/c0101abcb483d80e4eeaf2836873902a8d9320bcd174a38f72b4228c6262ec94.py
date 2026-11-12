import sys, json, base64, time
ct_hex="4b243d54cf34c7536f17198d96afad3d1422509f96297766e141cb86ddab166476838b2ac8ff3c556284e1b1546eceada6da5afd9b95eecc4bda57c93067f324ca8ecdfdd5d84a3afa0d1cce3ab7d4b6"
iv_hex="7297416ab13274f28a4f3298675178c3"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[iv]+[ct[i:i+16] for i in range(0,len(ct),16)]
# blocks[0]=iv, blocks[1..5]=Ct
def query(forged_prev: bytes, target: bytes) -> bool:
    payload=base64.b64encode(forged_prev+target).decode()
    print(json.dumps({"q": payload}), flush=True)
    line=sys.stdin.readline()
    if not line:
        raise RuntimeError("EOF from oracle")
    obj=json.loads(line)
    return bool(obj.get("pad_ok"))

def recover_intermediate(target: bytes) -> bytes:
    D=[0]*16
    for k in range(15,-1,-1):
        pad=16-k
        # suffix for j>k
        suffix={j: (D[j]^pad) for j in range(k+1,16)}
        found=False
        for b in range(256):
            forged=bytearray(16)
            for j, v in suffix.items():
                forged[j]=v
            forged[k]=b
            ok=query(bytes(forged), target)
            if ok:
                if k==15:
                    forged2=bytearray(forged)
                    forged2[14]^=1
                    ok2=query(bytes(forged2), target)
                    if ok2:
                        D[k]=b^pad
                        found=True
                        break
                    else:
                        continue
                else:
                    D[k]=b^pad
                    found=True
                    break
        if not found:
            raise RuntimeError(f"failed k={k}")
    return bytes(D)

t_start=time.monotonic_ns()
plain_blocks=[]
# recover first 4 blocks (64-byte message); 5th is padding block
for idx in range(1,5):
    target=blocks[idx]
    prev=blocks[idx-1]
    D=recover_intermediate(target)
    P=bytes(d^p for d,p in zip(D,prev))
    plain_blocks.append(P)
plaintext= b"".join(plain_blocks)
t_end=time.monotonic_ns()
print(f"OPSPAN_NS:{t_end-t_start}", flush=True)
print("CLAIM:"+json.dumps({"plaintext_hex": plaintext.hex()}), flush=True)