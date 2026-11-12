import time

t0 = time.monotonic_ns()
c1 = bytes.fromhex("010110148d6788e15e4da55cbd05d60b927dc1f1213e8a19582f58c758100ef21cdce107f47d2eb8b835b26fcc80fec793e85a0860620231d01bdf3f93ee1370")
c2 = bytes.fromhex("3761bcd317e04f8a6c16a158dc415fd5b39a9783672c7db7ddeb91ecd2526dd2837db62bd1d720d2f1bdd1b739d8868e956d34b6302fa01c5c02e56de68147c5")
# RC4 keystream K = c2 XOR 0x00*64 = c2
# P1 = c1 XOR K
tp = bytes(a ^ b for a, b in zip(c1, c2))
dt = time.monotonic_ns() - t0
print(f"OPSPAN_NS:{dt}")
print("CLAIM:" + __import__('json').dumps({"plaintext_hex": tp.hex()}))