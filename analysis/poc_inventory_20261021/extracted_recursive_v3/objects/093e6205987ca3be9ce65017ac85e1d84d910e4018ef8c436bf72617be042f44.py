import json
c1 = bytes.fromhex('debf59ab72847e7a4e9918ed2fa562852bf0a0a5dbacd5c2d12792c73437aef2b62f97a215dc809eea6dea2f5939bc8548a5ad01fcac44f57964ae3e6bbdc883')
c2 = bytes.fromhex('0e049a77b357310977edaa3fd6d043970a56199c34bb53e453f0c825cdef18d1702c3341e0a2e7362b19fcbc90c5e42ec6354a173b58c4a1364f83cdf78a2e44')
p = bytes(a ^ b for a, b in zip(c1, c2))
print('CLAIM:' + json.dumps({'plaintext2_hex': p.hex()}))