import json, time

c1_hex = "79953f8e4d6735025a66928566d4996ff461e7c61d52165b8001e97002e602828b35b6e99f9f01098c6cbec3e38e46c9620b294e12f025232ade1efa0e9d5b33"
c2_hex = "3affcf5a60327d24774b208d89d551a272e7757395f6f9041ec8f26e486cd490e0999f302fe0ce03597cdd63f0c394a9b23cc52e31033716dc20bee093a06d1e"

t0 = time.monotonic_ns()
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
assert len(c1) == len(c2) == 64
# RC4 keystream K: c1 = P1 xor K, c2 = 0x00*64 xor K = K
# => P1 = c1 xor c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))
t1 = time.monotonic_ns()

print("OPSPAN_NS:%d" % (t1 - t0))
print("CLAIM:" + json.dumps({"plaintext_hex": p1.hex()}))
sys.stdout.flush()