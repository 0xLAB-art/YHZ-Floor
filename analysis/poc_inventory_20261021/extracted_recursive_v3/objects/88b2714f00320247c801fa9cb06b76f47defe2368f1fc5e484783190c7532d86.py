import sys, json, time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex="802f837077f3d284cfb128efcbfb8bada1c47bd70c1b07dd89eadbf1442f9503e4dd96a4ac952c613ed294444224911860f6b8a624e5f75a92c56469a5580712"
sig2_hex="802f837077f3d284cfb128efcbfb8bada1c47bd70c1b07dd89eadbf1442f95038090dc38803d72d63381b83eed307afe17d0290405318ab4fbbb0017f757a9a1"
z1_hex="982b18ef18708e1f97671a35e0492c4bea0a5e4ba32e02d1f21342bf43c187a0"
z2_hex="c4cae8fe0c0d716155cd43cd439f9ca70f8ec2d538389709ad4d499b46fc21f6"
msg_hex="62d1f87a708bc05c11f9e1490b02e90a76d60cdce1b2861ae22821c961945c6c"
N=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

def parse_der(der):
    # SEQUENCE { INTEGER r, INTEGER s }
    assert der[0]==0x30
    i=1
    if der[1]&0x80:
        n=der[1]&0x7f
        i=2+n
    else:
        i=2
    out=[]
    for _ in range(2):
        assert der[i]==0x02, der[i]
        ln=der[i+1]
        v=int.from_bytes(der[i+2:i+2+ln],'big')
        out.append(v)
        i=i+2+ln
    return out

b1=bytes.fromhex(sig1_hex); b2=bytes.fromhex(sig2_hex)
r1=int.from_bytes(b1[:32],'big'); s1=int.from_bytes(b1[32:],'big')
r2=int.from_bytes(b2[:32],'big'); s2=int.from_bytes(b2[32:],'big')
z1=int(z1_hex,16); z2=int(z2_hex,16)

t0=time.monotonic_ns()
k=(pow(s1-s2,-1,N)*(z1-z2))%N
d=(pow(r1,-1,N)*(s1*k-z1))%N
t1=time.monotonic_ns()
print("OPSPAN_NS:%d"%(t1-t0)); sys.stdout.flush()

key=ECC.construct(curve='NIST P-256',d=d)
for (rr,ss,zh) in ((r1,s1,z1_hex),(r2,s2,z2_hex)):
    try:
        DSS.new(key,'fips-186-3').verify(b'\x30'+bytes([6+66])+b'\x02\x21\x00'+b'%064x'%rr+b'\x02\x21\x00'+b'%064x'%ss,SHA256.new(bytes.fromhex(zh)))
    except Exception as e:
        print("VERIFY_FAIL %s"%e); sys.stdout.flush()

der=DSS.new(key,'fips-186-3').sign(SHA256.new(bytes.fromhex(msg_hex)))
sr,ss=parse_der(der)
print("CLAIM:"+json.dumps({"d_hex":"%064x"%d,"sig_hex":"%064x%064x"%(sr,ss)}))
sys.stdout.flush()