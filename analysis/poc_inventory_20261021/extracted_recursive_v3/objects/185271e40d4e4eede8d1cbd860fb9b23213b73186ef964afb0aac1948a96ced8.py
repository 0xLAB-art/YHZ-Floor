import json
c1 = bytes.fromhex("e7c0a0f5820321f1c412cb92c3fb3ddc1e79190211d6448fb1fd735c82864419436c475b9238ce59e649b7b604f886b207fc0fc014738feaca0635128ca813d5")
c2 = bytes.fromhex("afcc45afdbb08c354fa33020e00b9d2c6f474c7455b0c22cb4e92a1f733f63f96f3191d7fd8a903308592efe83d8eece92df952796ba9bd706b55521f3246ffa")
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print("CLAIM:" + json.dumps({"plaintext2_hex": p1.hex()}))