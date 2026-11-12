import hashlib, json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
CURVE = 'NIST P-256'

sig1_hex = "9a2ca6103de387ce988156898ca08747afe6a4611340f49f3414301906040b84e641d250cafa67652a4b0200599503e10942161616799dffbeb4740191a17238"
sig2_hex = "9a2ca6103de387ce988156898ca08747afe6a4611340f49f3414301906040b84d587069f2fd6f1746cb1bf75a4e0d35239ab4c810342b04574f8368077425e91"
z1_hex = "2150a9e2851c5e29c98af468398a6cf6bea302f84086f9a803e65ad40c81fe58"
z2_hex = "25842f894834775199f0b3caae9c4058bd9b4d0b68c8a318906a456a14d6ebcf"
challenge_msg_hex = "3447288f3c7ba0e2fde53e986ad97ad343923263e3537e24f2a9fbde65cb23ec"

sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)
r1 = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
r2 = int.from_bytes(sig2[:32], 'big')
s2 = int.from_bytes(sig2[32:], 'big')
z1 = int.from_bytes(bytes.fromhex(z1_hex), 'big')
z2 = int.from_bytes(bytes.fromhex(z2_hex), 'big')

msg1 = bytes.fromhex(z1_hex)

def verifies(key, msg, sig):
    try:
        DSS.new(key, 'fips-186-3').verify(SHA256.new(msg), sig)
        return True
    except Exception:
        return False

def rec(rA, sA, zA, rB, sB, zB):
    if (sA - sB) % N == 0:
        return None
    k = ((zA - zB) * pow(sA - sB, -1, N)) % N
    if rA % N == 0:
        return None
    d = ((sA * k - zA) * pow(rA, -1, N)) % N
    if d == 0:
        return None
    return d

cands = []
for (rA, sA, zA, rB, sB, zB) in [(r1, s1, z1, r2, s2, z2), (r1, -s1 % N, z1, r2, -s2 % N, z2)]:
    d = rec(rA, sA, zA, rB, sB, zB)
    if d:
        cands.append(d)

d = None
for cand in cands:
    key = ECC.construct(curve=CURVE, d=cand)
    if verifies(key, msg1, sig1) and verifies(key, bytes.fromhex(z2_hex), sig2):
        d = cand
        break

if d is None and cands:
    d = cands[0]

key = ECC.construct(curve=CURVE, d=d)
challenge_sig = DSS.new(key, 'fips-186-3').sign(SHA256.new(bytes.fromhex(challenge_msg_hex)))

print('CLAIM:' + json.dumps({'d_hex': '%064x' % d, 'sig_hex': challenge_sig.hex()}))