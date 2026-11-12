import time
t0 = time.monotonic_ns()
c1 = bytes.fromhex("a6d1f0241c21f68061aa3a30707dba589c046a1f6e6c4d2bb7c329e7f08924bd6c6ed632e6cd4aeb65888a5296873e54abe890144591cf3e0e5e686b297dc3c4")
c2 = bytes.fromhex("7200e4f82b2bf72b7b8ea00f78cfc9fa4c76b3c22b8ce6833adf8a0ddf768070afbe23d37160ecca4093c729af4b69e175de67deda576643e3584744b075b3a4")
# same key+nonce => same keystream; P2 = 0 so keystream = c2; P1 = c1 XOR keystream
p1 = bytes(a ^ b for a, b in zip(c1, c2))
t1 = time.monotonic_ns()
print("OPSPAN_NS:" + str(t1 - t0))
print("CLAIM:" + '{"plaintext2_hex": "' + p1.hex() + '"}')