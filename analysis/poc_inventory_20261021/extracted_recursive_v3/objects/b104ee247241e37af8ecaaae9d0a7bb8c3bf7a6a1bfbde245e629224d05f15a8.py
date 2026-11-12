import sys, json, base64, time
ct_hex="5238ac704eb3bfed250f2fcb0a2113d3ecf2217836fbfda0052b67b2ae73edaa3380757c171322848ee34e80828a926a68ecb540cbade61318d430e025bed5436f22c981291d8740f64a9a813492a455"
iv_hex="9e78f54b81ecaf7530d4e9d9b9f1392d"
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
orig_prevs=[iv]+blocks[:-1]

def oracle_call(forged_prev, target):
    data=bytes(forged_prev)+bytes(target)
    b64=base64.b64encode(data).decode('ascii')
    sys.stdout.write(json.dumps({"q": b64})+"\n")
    sys.stdout.flush()
    line=sys.stdin.readline()
    if not line:
        raise RuntimeError("oracle EOF")
    return json.loads(line).get("pad_ok") is True

n=len(blocks)
plain_blocks=[]
intermediates=[]
for bi in range(n):
    target=blocks[bi]
    inter=bytearray(16)
    for pad_len in range(1,17):
        pos=16-pad_len
        found=False
        for trial in range(256):
            forged=bytearray(16)
            for k in range(pos+1,16):
                forged[k]=inter[k]^pad_len
            forged[pos]=trial
            ok=oracle_call(bytes(forged), target)
            if ok:
                if pad_len==1:
                    chk=bytearray(forged)
                    chk[14]^=0x01
                    ok2=oracle_call(bytes(chk), target)
                    if not ok2:
                        continue
                inter[pos]=trial^pad_len
                found=True
                break
        if not found:
            raise RuntimeError(f"byte not found block {bi} pad {pad_len}")
    intermediates.append(bytes(inter))
    pt=bytes([intermediates[-1][j]^orig_prevs[bi][j] for j in range(16)])
    plain_blocks.append(pt)
# final op timed
t0=time.monotonic_ns()
full=b"".join(plain_blocks)
# strip PKCS7 if valid
pad=full[-1]
if 1<=pad<=16 and full[-pad:]==bytes([pad])*pad:
    unpadded=full[:-pad]
else:
    unpadded=full
t1=time.monotonic_ns()
sys.stdout.write(f"OPSPAN_NS:{t1-t0}\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex": unpadded.hex()})+"\n")
sys.stdout.flush()