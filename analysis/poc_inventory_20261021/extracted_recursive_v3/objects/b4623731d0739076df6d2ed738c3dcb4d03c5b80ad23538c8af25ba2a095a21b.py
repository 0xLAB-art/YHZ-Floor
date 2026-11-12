import sys, json, base64, time
ct_hex="2d8b1cf4a1462301d00db3524eaf30099264d96a23b7c2bd66715a3f32a6fcc4605c8bb0295d378dc2a41302274f62053bfa614a884a4dd598ca28fc61ee743f52bb56f89ad884d9238b15549ee55a28"
iv_hex="2ceef434f762d4c6ba315182c44368df"
def oracle(prev, tgt):
    b=base64.b64encode(prev+tgt).decode()
    sys.stdout.write('{\"q\":\"'+b+'\"}\n')
    sys.stdout.flush()
    line=sys.stdin.readline()
    if not line:
        raise RuntimeError('eof oracle')
    return json.loads(line).get('pad_ok') is True
def dec_block(tgt):
    inter=bytearray(16)
    forged=bytearray(16)
    for pos in range(15,-1,-1):
        pad=16-pos
        for j in range(pos+1,16):
            forged[j]=inter[j]^pad
        hit=None
        for g in range(256):
            forged[pos]=g
            if oracle(bytes(forged),tgt):
                if pad==1:
                    forged[14]^=1
                    ok2=oracle(bytes(forged),tgt)
                    forged[14]^=1
                    if not ok2:
                        continue
                hit=g
                break
        if hit is None:
            raise RuntimeError('no hit')
        inter[pos]=hit^pad
    return bytes(inter)
def main():
    t0=time.monotonic_ns()
    ct=bytes.fromhex(ct_hex)
    iv=bytes.fromhex(iv_hex)
    blks=[ct[i:i+16] for i in range(0,len(ct),16)]
    prevs=[iv]+blks[:-1]
    pt=b''
    for idx,tgt in enumerate(blks):
        I=dec_block(tgt)
        P=bytes(a^b for a,b in zip(I,prevs[idx]))
        pt+=P
    t1=time.monotonic_ns()
    pad=pt[-1]
    if 1<=pad<=16 and pt[-pad:]==bytes([pad])*pad:
        pt_nopad=pt[:-pad]
    else:
        pt_nopad=pt
    sys.stdout.write('OPSPAN_NS:'+str(t1-t0)+'\n')
    sys.stdout.flush()
    sys.stdout.write('CLAIM:'+json.dumps({'plaintext_hex':pt_nopad.hex()},separators=(',',':'))+'\n')
    sys.stdout.flush()
if __name__=='__main__':
    main()