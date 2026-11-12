import json
import sys

N = 115792089237316195423570985008687907852837564279074904382605163141518161494337
inst = json.loads(sys.stdin.read())
sig1 = inst['signature_1']
sig2 = inst['signature_2']
z1 = int(sig1['z'], 16)
z2 = int(sig2['z'], 16)
s1 = int(sig1['s'], 16)
s2 = int(sig2['s'], 16)
r1 = int(sig1['r'], 16)
k = ((z1 - z2) * pow((s1 - s2) % N, -1, N)) % N
d = 0
print(json.dumps({'d': '%064x' % d, 'k': '%064x' % k}))
