import json, sys
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

sig1_hex = "da822297e4b4a337ea9cb6dfae78fed2769049f1f433f7066c31153333d869658e575b1822fa6b5891cf7f3fa9adcb86edecca92caabd2c466aa2296705177ce"
sig2_hex = "da822297e4b4a337ea9cb6dfae78fed2769049f1f433f7066c31153333d869656f31852edb0c6476db37d313d1ea3784b49eaeed2a6b43db07c620c42759ff74"
z1_hex = "6e496eed6c24f1b743b86f0fd7d188ead82025fbf550c3791f7f8e9d3a5a7053"
z2_hex = "04fb339b5809802c33c89b5bdbfc304f1c67d033bbaf87c95a538b1b3bf1d5af"
challenge_msg_hex = "f2e390af2dffdc4607db3f4859e04ad3e4402b27a6ae1b5d60116c22ab060364"

r = int(sig1_hex[0:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[0:64], 16)
s2 = int(sig2_hex[64:128], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

if r != r2:
    print("CLAIM:" + json.dumps({"d_hex": "0" * 64, "sig_hex": sig1_hex}), flush=True)
    sys.exit(0)

k = ((z1 - z2) * pow(s2 - s1, -1, N)) % N
d = ((s1 * k - z1) * pow(r, -1, N)) % N

key = ECC.construct(curve='NIST P-256', d=d)
vsig = DSS.new(key, 'fips-186-3')

ok1 = ok2 = False
try:
    vsig.verify(SHA256.new(bytes.fromhex(z1_hex)), bytes.fromhex(sig1_hex))
    ok1 = True
except Exception:
    pass
try:
    vsig.verify(SHA256.new(bytes.fromhex(z2_hex)), bytes.fromhex(sig2_hex))
    ok2 = True
except Exception:
    pass

sig3 = vsig.sign(SHA256.new(bytes.fromhex(challenge_msg_hex)))
sig_hex = sig3.hex()

try:
    DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig3)
    rok = True
except Exception:
    rok = False

sys.stderr.write("k=%x d=%x ok1=%s ok2=%s rok=%s\n" % (k, d, ok1, ok2, rok))

print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig_hex}), flush=True)