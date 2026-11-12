import sys
import json

def inv(a, m):
    return pow(a % m, -1, m)

data = json.load(open(sys.argv[1], "r"))
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
r = int(data["signature_1"]["r"], 16)
s1 = int(data["signature_1"]["s"], 16)
z1 = int(data["signature_1"]["z"], 16)
s2 = int(data["signature_2"]["s"], 16)
z2 = int(data["signature_2"]["z"], 16)
k = ((z1 - z2) * inv(s1 - s2, n)) % n
d = ((s1 * k - z1) * inv(r, n)) % n
print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))
