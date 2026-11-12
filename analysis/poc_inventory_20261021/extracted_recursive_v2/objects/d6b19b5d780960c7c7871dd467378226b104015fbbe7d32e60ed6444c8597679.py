import json
import sys

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

if 'signature_2' not in data:
    print(json.dumps({"status": "UNDERDETERMINED", "reason": "second signature missing, cannot recover private key from single signature"}))
else:
    N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    sig1 = data['signature_1']
    sig2 = data['signature_2']
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    def modinv(a, m):
        return pow(a, -1, m)
    
    k = ((z1 - z2) * modinv(s1 - s2, N)) % N
    d = ((s1 * k - z1) * modinv(r, N)) % N
    
    print(json.dumps({"k": f"{k:064x}", "d": f"{d:064x}"}))
