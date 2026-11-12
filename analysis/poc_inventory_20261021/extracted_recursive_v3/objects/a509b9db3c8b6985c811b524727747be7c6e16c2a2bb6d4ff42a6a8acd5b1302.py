import time
t0 = time.monotonic_ns()
c1 = bytes.fromhex("39ea1fd49a51ef2b8334845ebee547b2e94a5573cc933bfce74a26e3a984845f760c665e3a3b764233f8ed8a67c34b535a93a13c7418f08eefcc962bdd6bc7a4")
c2 = bytes.fromhex("d529af319efe59bdcbdbde726a2b44c5f65fdaa96f98ddc50a10601e683ef4e4a56498b1f6fce38d736744d2f7fc0ece97bff03fa39ebfd06f146cc35301d24e")
pt = bytes(a ^ b for a, b in zip(c1, c2))
t1 = time.monotonic_ns()
print("OPSPAN_NS:%d" % (t1 - t0))
print("CLAIM:" + __import__('json').dumps({"plaintext_hex": pt.hex()}))