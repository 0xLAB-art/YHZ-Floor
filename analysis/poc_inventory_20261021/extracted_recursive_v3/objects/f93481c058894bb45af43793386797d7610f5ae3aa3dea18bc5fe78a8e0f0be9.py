import time
c1 = bytes.fromhex("34c433e7e930b79f1031c703650fbf06346973f0263acfa57a9c9078758d7571d7d6a0826e3fff9ef310eaf2faf0746d73313f94827bbc36651957c9471019da")
c2 = bytes.fromhex("bd36c203819c06bdec7dcb7dbf922e3fd2564d924db371f53686c28b6a8dfc079ee5268965e609cb284478312e774dafcd674e0d0a275bd369639e9ce45158c6")
t0 = time.monotonic_ns()
# nonce reuse: C2 = keystream XOR 0x00*64 -> keystream = C2; P1 = C1 XOR keystream
p1 = bytes(a ^ b for a, b in zip(c1, c2))
opspan = time.monotonic_ns() - t0
assert len(p1) == 64
print("OPSPAN_NS:%d" % opspan)
print('CLAIM:' + '{"plaintext2_hex": "%s"}' % p1.hex(), flush=True)