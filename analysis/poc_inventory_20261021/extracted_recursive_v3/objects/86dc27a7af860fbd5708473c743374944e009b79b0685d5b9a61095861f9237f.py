import json
c1 = bytes.fromhex("82b6472a14c544c7cb604d2a2e634a739d8929e6d2d61df56da0bcaa9e358168defd49a182bf9942a7a9607aae8feffa8f70cb8ec403840fba68fc3a87a99900")
c2 = bytes.fromhex("7216f2c0b40712edfee725ff1e0051f46dbf307c5baecd881368b38af7c31d54bef139f5e305382328e4ec4a30b9a2d0fa546dfa811612a994c4917e919634b0")
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print("CLAIM:" + json.dumps({"plaintext2_hex": p1.hex()}))