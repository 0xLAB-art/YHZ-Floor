import json,sys
prov = json.loads(sys.argv[1])
c1 = bytes.fromhex(prov["c1_hex"]); c2 = bytes.fromhex(prov["c2_hex"])
pt = bytes(a ^ b for a, b in zip(c1, c2))
print("CLAIM:"+json.dumps({"plaintext2_hex": pt.hex()}))