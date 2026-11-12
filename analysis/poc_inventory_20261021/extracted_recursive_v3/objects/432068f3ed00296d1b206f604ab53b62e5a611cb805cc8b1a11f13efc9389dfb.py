import sys, time
c1_hex = "56143a0e044e393f2c3de71b0f1cbd20ca4c9b8b9cea58bed5d7eaee2dd95fc42ae9f95ae3e090e1bf575608f14beca7476018723f1d3fe2f5517a14b6e78ab0"
c2_hex = "419c2fdb4c5d8a30c14134fb1b8da81710d3b16d2bcc411116319b4a27d965ce63a3390ce94bd6f39f3a4178d4cbe697f2faea0b5c0d0863f9b0ceb44b760d1d"
start = time.monotonic_ns()
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()
elapsed = time.monotonic_ns() - start
sys.stdout.write(f"OPSPAN_NS:{elapsed}\n")
sys.stdout.write(f"CLAIM:{{\"plaintext_hex\": \"{plaintext_hex}\"}}\n")
sys.stdout.flush()