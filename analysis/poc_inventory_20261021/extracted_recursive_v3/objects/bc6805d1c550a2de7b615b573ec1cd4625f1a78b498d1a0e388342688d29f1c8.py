import sys, json, base64, time
ct_hex="4b2ff72d7721031091971902885b53193a58542190a6f93029b2e35679f01db219e161692af616757a1767d6a8cb7fcc2e0c988e2165507e7828dab156638d521709815c75c271d3f1def04d2b477a83"
iv_hex="dc75eae15207780e53cde356c98596d7"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
prevs=[iv]+blocks[:-1]
targets=blocks
def query(forged_prev,target):
    data=forged_prev+target
    print(json.dumps({"q": base64.b64encode(data).decode()}), flush=True)
    line=sys.stdin.readline()
    while line is not None and line.strip()=="":
        line=sys.stdin.readline()
    if not line:
        raise RuntimeError("EOF from oracle")
    r=json.loads(line)
    return bool(r.get("pad_ok", r.get("padOk", False)))
def decrypt_block(target):
    inter=bytearray(16)
    forged=bytearray(16)
    for k in range(1,17):
        pos=16-k
        for j in range(pos+1,16):
            forged[j]=inter[j]^k
        found=False
        for guess in range(256):
            forged[pos]=guess
            ok=query(bytes(forged), target)
            if ok:
                if k==1:
                    # verify it is really 0x01 by flipping byte 14
                    saved=forged[14]
                    forged[14]^=0x01
                    still=query(bytes(forged), target)
                    forged[14]=saved
                    if not still:
                        continue
                inter[pos]=guess^k
                found=True
                break
        if not found:
            raise RuntimeError(f"no guess found for k={k}")
    return bytes(inter)
start=time.monotonic_ns()
plain_blocks=[]
for idx in range(len(targets)):
    t=targets[idx]
    p_prev=prevs[idx]
    inter=decrypt_block(t)
    pt=bytes(a^b for a,b in zip(inter,p_prev))
    plain_blocks.append(pt)
end=time.monotonic_ns()
full=b"".join(plain_blocks)
# strip pkcs7 if present for claim (verifier also strips, either ok)
# keep full padded or stripped? claim stripped 64 bytes
pad=full[-1]
if 1<=pad<=16 and full[-pad:]==bytes([pad])*pad:
    unpadded=full[:-pad]
else:
    unpadded=full
print(f"OPSPAN_NS:{end-start}", flush=True)
print("CLAIM:"+json.dumps({"plaintext_hex": unpadded.hex()}), flush=True)