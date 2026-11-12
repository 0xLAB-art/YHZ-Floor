import time
c1 = bytes.fromhex("417a4f888538d5108d3c04f2f35850cde01ba62f043be528d2902987462e1e654a8a92575984efcc539ec919fd4168d5ea8c35632e8a1269f61826feca454019")
c2 = bytes.fromhex("889ee60b79c3f043d4ee135dc997dad9ada2dad37b6fa31e1bfb4885f74404f4e4c6a32b0f3efddcfcd13984badf5f69266eab6f037a0d9cd801c6cdfb6ce570")
t0 = time.monotonic_ns()
ks = c2
p1 = bytes(a ^ b for a, b in zip(c1, ks))
t1 = time.monotonic_ns()
print("OPSPAN_NS:%d" % (t1 - t0))
print("CLAIM:" + '{"plaintext_hex": "%s"}' % p1.hex())