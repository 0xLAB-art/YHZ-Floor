import sys, json, time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex="802f837077f3d284cfb128efcbfb8bada1c47bd70c1b07dd89eadbf1442f9503e4dd96a4ac952c613ed294444224911860f6b8a624e5f75a92c56469a5580712"
sig2_hex="802f837077f3d284cfb128efcbfb8bada1c47bd70c1b07dd89eadbf1442f95038090dc38803d72d63381b83eed307afe17d0290405318ab4fbbb0017f757a9a1"
z1_hex="982b18ef18708e1f97671a35e0492c4bea0a5e4ba32e02d1f21342bf43c187a0"
z2_hex="c4cae8fe0c0d716155cd43cd439f9ca70f8ec2d538389709ad4d499b46fc21d6"
z2_hex="c4cae8fe0c0d716155cd43cd439f9ca70f8ec2d538389709ad4d499b46fc21f6"
msg_hex="62d1f87a708bc05c11f9e1490b02e90a76d60cdce1b2861ae22821c961945c6c"
N=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

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
        DSS.new(key,'fips-186-3').verify(bytes.fromhex('%064x%064x'%(rr,ss)),SHA256.new(bytes.fromhex(zh)))
        print("OK raw"); sys.stdout.flush()
    except Exception as e1:
        try:
            DSS.new(key,'fips-186-3').verify(b'\x30\x46\x02\x21\x00'+('%064x'%rr).encode()+b'\x02\x21\x00'+('%064x'%ss).encode(),SHA256.new(bytes.fromhex(zh)))
            print("OK der"); sys.stdout.flush()
        except Exception as e2:
            print("VERIFY_FAIL %r %r"%(e1,e2)); sys.stdout.flush()

der=DSS.new(key,'fips-186-3').sign(SHA256.new(bytes.fromhex(msg_hex)))
print("TYPE %r"%type(der)); sys.stdout.flush()

def extract(der):
    if isinstance(der,(tuple,list)):
        return int(der[0]),int(der[1])
    if isinstance(der,str):
        der=der.encode('latin-1')
    der=bytes(der)
    i=1
    if der[1]&0x80:
        i=2+(der[1]&0x7f)
    else:
        i=2
    out=[]
    for _ in range(2):
        ln=der[i+1]
        out.append(int.from_bytes(der[i+2:i+2+ln],'big'))
        i=i+2+ln
    return out[0],out[1]

sr,ss=extract(der)
print("CLAIM:"+json.dumps({"d_hex":"%064x"%d,"sig_hex":"%064x%064x"%(sr,ss)}))
sys.stdout.flush()